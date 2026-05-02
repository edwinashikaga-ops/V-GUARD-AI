"""
vguard_sync.py
==============
Modul integrasi Agent Visionary & Liaison untuk sistem V-Guard.
Fungsi utama:
  - Tarik data transaksi baru dari API Kasir (Moka POS)
  - Ambil cuplikan video CCTV pada detik transaksi terjadi
  - Deteksi barang yang dipindah tapi tidak di-scan → Alert 'Unscanned Item'
"""

import asyncio
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import cv2
import numpy as np

# ─────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger("vguard.sync")

# Variabel lingkungan (isi di file .env atau environment sistem)
KASIR_API_BASE   = os.getenv("KASIR_API_BASE", "http://localhost:8000")
KASIR_API_KEY    = os.getenv("KASIR_API_KEY", "changeme-kasir-key")
VGUARD_API_BASE  = os.getenv("VGUARD_API_BASE", "http://localhost:9000")
VGUARD_API_KEY   = os.getenv("VGUARD_API_KEY", "changeme-vguard-key")
CCTV_RTSP_URL    = os.getenv("CCTV_RTSP_URL", "rtsp://admin:password@192.168.1.100/stream")
POLL_INTERVAL    = int(os.getenv("POLL_INTERVAL_SEC", "5"))     # detik antar polling
FRAME_BUFFER_SEC = int(os.getenv("FRAME_BUFFER_SEC", "3"))      # ±N detik ambil frame CCTV
YOLO_CONF_THRESH = float(os.getenv("YOLO_CONF_THRESH", "0.45")) # confidence threshold YOLO
SNAPSHOT_DIR     = os.getenv("SNAPSHOT_DIR", "./snapshots")

os.makedirs(SNAPSHOT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────

@dataclass
class TransactionItem:
    """Satu baris item dalam transaksi kasir."""
    item_id: str
    name: str
    qty: int
    price: float


@dataclass
class Transaction:
    """Satu transaksi dari API Kasir."""
    transaction_id: str
    timestamp: datetime
    items: list[TransactionItem] = field(default_factory=list)
    total: float = 0.0
    cashier_id: str = ""


@dataclass
class DetectedObject:
    """Objek yang terdeteksi YOLO dalam frame CCTV."""
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]   # x1, y1, x2, y2


@dataclass
class UnscannedAlert:
    """Alert untuk barang yang dipindah tapi tidak di-scan."""
    alert_id: str
    transaction_id: str
    detected_objects: list[DetectedObject]
    scanned_items: list[TransactionItem]
    snapshot_path: str
    timestamp: datetime
    severity: str = "HIGH"   # HIGH / MEDIUM / LOW


# ─────────────────────────────────────────────
# AGENT LIAISON  –  Tarik Data Kasir
# ─────────────────────────────────────────────

class LiaisonAgent:
    """
    Agent Liaison: bertugas berkomunikasi dengan API Kasir (Moka POS).
    Melakukan polling transaksi baru dan mengembalikannya ke Coordinator.
    """

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self._last_seen_id: Optional[str] = None
        self.headers = {
            "Authorization": f"Bearer {KASIR_API_KEY}",
            "Content-Type": "application/json",
        }

    async def fetch_latest_transactions(self) -> list[Transaction]:
        """
        Tarik daftar transaksi baru sejak transaksi terakhir yang sudah diproses.
        """
        params = {}
        if self._last_seen_id:
            params["after_id"] = self._last_seen_id

        url = f"{KASIR_API_BASE}/api/v1/transactions"
        try:
            async with self.session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                data = await resp.json()
        except aiohttp.ClientError as exc:
            logger.error("Liaison – Gagal tarik transaksi: %s", exc)
            return []

        transactions: list[Transaction] = []
        for raw in data.get("transactions", []):
            ts = datetime.fromisoformat(raw["timestamp"]).replace(tzinfo=timezone.utc)
            items = [
                TransactionItem(
                    item_id=i["id"],
                    name=i["name"],
                    qty=i["qty"],
                    price=i["price"],
                )
                for i in raw.get("items", [])
            ]
            transactions.append(
                Transaction(
                    transaction_id=raw["id"],
                    timestamp=ts,
                    items=items,
                    total=raw.get("total", 0.0),
                    cashier_id=raw.get("cashier_id", ""),
                )
            )

        if transactions:
            self._last_seen_id = transactions[-1].transaction_id
            logger.info("Liaison – %d transaksi baru ditemukan.", len(transactions))

        return transactions


# ─────────────────────────────────────────────
# AGENT VISIONARY  –  Analisa Video CCTV
# ─────────────────────────────────────────────

class VisionaryAgent:
    """
    Agent Visionary: mengambil frame CCTV pada waktu tertentu dan menjalankan
    deteksi objek menggunakan YOLOv8 (atau model YOLO lainnya).
    """

    def __init__(self):
        self.model = self._load_yolo_model()

    def _load_yolo_model(self):
        """
        Muat model YOLO. Jika ultralytics tersedia gunakan YOLOv8,
        jika tidak fallback ke OpenCV DNN (YOLOv4).
        """
        try:
            from ultralytics import YOLO  # type: ignore
            model_path = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
            logger.info("Visionary – Memuat YOLOv8 dari '%s'", model_path)
            return YOLO(model_path)
        except ImportError:
            logger.warning("Visionary – ultralytics tidak tersedia, fallback ke mock detector.")
            return None

    def capture_frames(
        self,
        rtsp_url: str,
        target_ts: datetime,
        buffer_sec: int = 3,
    ) -> list[np.ndarray]:
        """
        Buka stream RTSP dan ambil frame di sekitar `target_ts` ±`buffer_sec` detik.
        Mengembalikan list frame (numpy array BGR).
        """
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            logger.error("Visionary – Tidak bisa buka CCTV: %s", rtsp_url)
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        # Hitung nomor frame target berdasarkan timestamp
        # (asumsi stream sudah running; dalam produksi pakai NTP sync / PTS)
        frames_to_skip = max(0, int((time.time() - target_ts.timestamp() - buffer_sec) * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frames_to_skip)

        collected: list[np.ndarray] = []
        capture_duration = buffer_sec * 2   # total detik yang dikumpulkan
        max_frames = int(fps * capture_duration)

        for _ in range(max_frames):
            ret, frame = cap.read()
            if not ret:
                break
            collected.append(frame)

        cap.release()
        logger.info("Visionary – %d frame diambil dari CCTV.", len(collected))
        return collected

    def detect_objects(self, frames: list[np.ndarray]) -> list[DetectedObject]:
        """
        Jalankan deteksi YOLO pada kumpulan frame.
        Kembalikan objek unik (deduplikasi berdasarkan label).
        """
        if not frames:
            return []

        # Pilih frame tengah sebagai frame representatif
        representative = frames[len(frames) // 2]

        if self.model is not None:
            return self._detect_ultralytics(representative)
        else:
            return self._detect_mock(representative)

    def _detect_ultralytics(self, frame: np.ndarray) -> list[DetectedObject]:
        """Deteksi menggunakan YOLOv8 (ultralytics)."""
        results = self.model(frame, conf=YOLO_CONF_THRESH, verbose=False)
        objects: list[DetectedObject] = []
        for r in results:
            for box in r.boxes:
                label = r.names[int(box.cls[0])]
                conf  = float(box.conf[0])
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
                objects.append(DetectedObject(label=label, confidence=conf, bbox=(x1, y1, x2, y2)))
        logger.info("Visionary – Deteksi: %s", [o.label for o in objects])
        return objects

    def _detect_mock(self, frame: np.ndarray) -> list[DetectedObject]:
        """Mock detector untuk pengujian tanpa GPU/model."""
        logger.warning("Visionary – Menggunakan mock detector (tidak ada model nyata).")
        return [
            DetectedObject(label="bottle",  confidence=0.87, bbox=(100, 150, 200, 350)),
            DetectedObject(label="bag",     confidence=0.72, bbox=(300, 100, 500, 400)),
            DetectedObject(label="person",  confidence=0.95, bbox=(50,  50,  600, 600)),
        ]

    def save_snapshot(self, frame: np.ndarray, alert_id: str) -> str:
        """Simpan frame ke disk dan kembalikan path-nya."""
        filename = f"{SNAPSHOT_DIR}/alert_{alert_id}.jpg"
        cv2.imwrite(filename, frame)
        logger.info("Visionary – Snapshot disimpan: %s", filename)
        return filename


# ─────────────────────────────────────────────
# KOORDINATOR  –  Logic Utama Deteksi Unscanned
# ─────────────────────────────────────────────

class VGuardCoordinator:
    """
    Koordinator utama yang mengorkestrasi Liaison dan Visionary.
    Mengandung logic inti: bandingkan barang terdeteksi CCTV vs log kasir.
    """

    # Daftar label YOLO yang dianggap sebagai "produk toko" (sesuaikan)
    PRODUCT_LABELS = {
        "bottle", "cup", "bowl", "banana", "apple", "sandwich",
        "orange", "broccoli", "carrot", "hot dog", "pizza", "donut",
        "cake", "book", "clock", "vase", "scissors", "cell phone",
        "keyboard", "mouse", "remote", "backpack", "handbag", "suitcase",
        "bottle", "wine glass", "fork", "knife", "spoon",
        # Tambahkan label produk toko Anda di sini
    }

    def __init__(self, session: aiohttp.ClientSession):
        self.liaison   = LiaisonAgent(session)
        self.visionary = VisionaryAgent()
        self.session   = session
        self.alerts: list[UnscannedAlert] = []

    def _map_detected_to_products(
        self, detected: list[DetectedObject]
    ) -> list[DetectedObject]:
        """Filter hanya objek yang termasuk kategori produk toko."""
        return [obj for obj in detected if obj.label in self.PRODUCT_LABELS]

    def _find_unscanned(
        self,
        detected_products: list[DetectedObject],
        scanned_items: list[TransactionItem],
    ) -> list[DetectedObject]:
        """
        Logika inti:
        Jika jumlah jenis produk terdeteksi > jumlah jenis item di kasir,
        kemungkinan ada barang yang tidak di-scan.

        Catatan: dalam produksi, perlu matching lebih canggih
        (embedding visual produk, barcode cross-check, dsb.)
        """
        scanned_names = {item.name.lower() for item in scanned_items}
        scanned_count = sum(item.qty for item in scanned_items)
        detected_count = len(detected_products)

        unscanned: list[DetectedObject] = []

        # Heuristik sederhana: lebih banyak produk terdeteksi daripada yang di-scan
        if detected_count > scanned_count:
            # Produk yang tidak ada padanannya di kasir
            for obj in detected_products:
                if obj.label.lower() not in scanned_names:
                    unscanned.append(obj)

        return unscanned

    async def _send_alert(self, alert: UnscannedAlert) -> None:
        """Kirim alert ke V-Guard API untuk ditampilkan di dashboard."""
        url = f"{VGUARD_API_BASE}/api/v1/alerts"
        headers = {"X-API-Key": VGUARD_API_KEY, "Content-Type": "application/json"}
        payload = {
            "alert_id":       alert.alert_id,
            "transaction_id": alert.transaction_id,
            "timestamp":      alert.timestamp.isoformat(),
            "severity":       alert.severity,
            "snapshot_path":  alert.snapshot_path,
            "detected_objects": [
                {"label": o.label, "confidence": o.confidence}
                for o in alert.detected_objects
            ],
            "scanned_items": [
                {"name": i.name, "qty": i.qty}
                for i in alert.scanned_items
            ],
        }
        try:
            async with self.session.post(
                url, headers=headers, json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                logger.warning(
                    "🚨 ALERT DIKIRIM – Transaksi %s | Terdeteksi: %s",
                    alert.transaction_id,
                    [o.label for o in alert.detected_objects],
                )
        except aiohttp.ClientError as exc:
            logger.error("Gagal kirim alert ke V-Guard API: %s", exc)

    async def process_transaction(self, txn: Transaction) -> None:
        """Proses satu transaksi: ambil frame CCTV → deteksi → bandingkan → alert."""
        logger.info("Memproses transaksi %s (ts: %s)", txn.transaction_id, txn.timestamp)

        # 1. Ambil frame CCTV
        frames = await asyncio.to_thread(
            self.visionary.capture_frames,
            CCTV_RTSP_URL,
            txn.timestamp,
            FRAME_BUFFER_SEC,
        )

        if not frames:
            logger.warning("Tidak ada frame CCTV untuk transaksi %s", txn.transaction_id)
            return

        # 2. Deteksi objek
        all_objects  = await asyncio.to_thread(self.visionary.detect_objects, frames)
        products     = self._map_detected_to_products(all_objects)
        unscanned    = self._find_unscanned(products, txn.items)

        # 3. Jika ada yang tidak di-scan → buat alert
        if unscanned:
            alert_id = str(uuid.uuid4())[:8]
            snapshot_path = await asyncio.to_thread(
                self.visionary.save_snapshot,
                frames[len(frames) // 2],
                alert_id,
            )
            alert = UnscannedAlert(
                alert_id=alert_id,
                transaction_id=txn.transaction_id,
                detected_objects=unscanned,
                scanned_items=txn.items,
                snapshot_path=snapshot_path,
                timestamp=datetime.now(tz=timezone.utc),
            )
            self.alerts.append(alert)
            await self._send_alert(alert)
        else:
            logger.info("✅ Transaksi %s bersih – semua barang ter-scan.", txn.transaction_id)

    async def run(self) -> None:
        """Loop utama: polling kasir → proses setiap transaksi baru."""
        logger.info("VGuard Sync dimulai. Polling setiap %d detik…", POLL_INTERVAL)
        while True:
            try:
                transactions = await self.liaison.fetch_latest_transactions()
                tasks = [self.process_transaction(txn) for txn in transactions]
                if tasks:
                    await asyncio.gather(*tasks)
            except Exception as exc:
                logger.exception("Error tak terduga di loop utama: %s", exc)
            await asyncio.sleep(POLL_INTERVAL)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

async def main() -> None:
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        coordinator = VGuardCoordinator(session)
        await coordinator.run()


if __name__ == "__main__":
    asyncio.run(main())
