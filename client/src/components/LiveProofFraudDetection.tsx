import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle } from "lucide-react";

const LOG_ENTRIES = [
  "[PENGAWAS]: Memindai POS ID-092...",
  "[SISTEM]: Terhubung ke CCTV CAM-07",
  "[MONITOR]: Transaksi #1001 dimulai",
  "[SCAN]: Menganalisis pola perilaku kasir",
  "[PERINGATAN]: Aturan R1 (VOID Langsung) Terdeteksi!",
  "[ANOMALI]: VOID Cepat terdeteksi - 3 void dalam 5 detik",
  "[SKOR_KECURANGAN]: Skor Keyakinan: 94%",
  "[AKSI]: Menandai transaksi untuk ditinjau",
  "[NOTIFIKASI]: Peringatan dikirim ke dashboard admin",
];

export default function LiveProofFraudDetection() {
  const [displayedLogs, setDisplayedLogs] = useState<string[]>([]);
  const [fraudDetected, setFraudDetected] = useState(false);
  const [receiptStamped, setReceiptStamped] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!isMounted) return;

    let index = 0;
    const interval = setInterval(() => {
      if (index < LOG_ENTRIES.length) {
        setDisplayedLogs((prev) => [...prev, LOG_ENTRIES[index]]);
        if (index >= 4) {
          setFraudDetected(true);
        }
        if (index >= 6) {
          setReceiptStamped(true);
        }
        index++;
      } else {
        // Reset animation
        index = 0;
        setDisplayedLogs([]);
        setFraudDetected(false);
        setReceiptStamped(false);
      }
    }, 800);

    return () => clearInterval(interval);
  }, [isMounted]);

  if (!isMounted) return null;

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-white mb-4">
          Bukti Langsung: Deteksi Kecurangan
        </h2>
        <p className="text-slate-300 max-w-2xl mx-auto">
          Saksikan deteksi kecurangan real-time dengan analisis CCTV canggih dan pemantauan transaksi yang tersinkronisasi
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* CCTV Video Section */}
        <div className="lg:col-span-2">
          <Card className="bg-slate-900 border-2 border-cyan-500 p-0 overflow-hidden relative">
            {/* Recording Label */}
            <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
              <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse" />
              <span className="text-red-600 font-bold text-sm tracking-widest">RECORDING</span>
            </div>

            {/* Camera Info */}
            <div className="absolute bottom-4 left-4 z-10 text-cyan-400 font-mono text-xs">
              <div>CAM-07 • 1080P HD</div>
              <div>{new Date().toLocaleTimeString("id-ID")}</div>
            </div>

            {/* CCTV Placeholder Video/Image */}
            <div className="relative w-full aspect-video bg-slate-800 overflow-hidden">
              <video
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-full object-cover opacity-60"
                poster="/fraud-detection-mockup.png"
              >
                <source
                  src="https://cdn.pixabay.com/video/2016/03/31/2565-160166391_large.mp4"
                  type="video/mp4"
                />
                <img
                  src="/fraud-detection-mockup.png"
                  alt="CCTV Fraud Detection"
                  className="w-full h-full object-cover"
                />
              </video>

              {/* Overlay Grid Effect */}
              <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-20 pointer-events-none" />

              {/* Scanline Effect */}
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent h-20 w-full animate-scan pointer-events-none" />

              {/* Glow Effect */}
              <div className="absolute inset-0 border-2 border-cyan-500/30 pointer-events-none" />
            </div>
          </Card>
        </div>

        {/* Right Panel: Logs + Receipt */}
        <div className="space-y-6">
          {/* Log Stream */}
          <Card className="bg-slate-800 border-slate-700 p-4">
            <h3 className="text-sm font-semibold text-cyan-400 mb-3 font-mono">
              LOG PEMANTAUAN SISTEM
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {displayedLogs.map((log, idx) => (
                <div
                  key={idx}
                  className={`text-xs font-mono transition-all ${
                    log.includes("PERINGATAN") || log.includes("KECURANGAN") || log.includes("ANOMALI")
                      ? "text-red-400"
                      : log.includes("SISTEM") || log.includes("MONITOR")
                      ? "text-cyan-400"
                      : "text-slate-400"
                  }`}
                >
                  {log}
                </div>
              ))}
            </div>
          </Card>

          {/* Digital Receipt */}
          <Card
            className={`bg-slate-800 border-slate-700 p-4 transition-all ${
              receiptStamped ? "border-red-600 bg-red-950/20" : ""
            }`}
          >
            <h3 className="text-sm font-semibold text-white mb-3">
              Transaksi #1001
            </h3>

            <div className="space-y-2 text-xs text-slate-300 mb-4 font-mono">
              <div className="flex justify-between">
                <span>Item 1: Minuman</span>
                <span>Rp 25,000</span>
              </div>
              <div className="flex justify-between">
                <span>Item 2: Camilan</span>
                <span>Rp 15,000</span>
              </div>
              <div className="border-t border-slate-600 pt-2 mt-2 flex justify-between font-semibold">
                <span>Total</span>
                <span>Rp 40,000</span>
              </div>
            </div>

            {receiptStamped && (
              <div className="relative h-20">
                <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
                  <div className="transform -rotate-12 border-4 border-red-600 px-4 py-2 text-red-600 font-black text-2xl uppercase tracking-tighter bg-slate-900/80 backdrop-blur-sm shadow-[0_0_20px_rgba(220,38,38,0.5)] animate-in zoom-in duration-300">
                    KECURANGAN
                  </div>
                </div>
                <div className="opacity-30">
                  <Badge className="bg-red-600 w-full justify-center">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Ditandai untuk Ditinjau
                  </Badge>
                </div>
              </div>
            )}

            {!receiptStamped && (
              <Badge className="bg-green-600 w-full justify-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                Transaksi Valid
              </Badge>
            )}
          </Card>

          {/* Status Indicator */}
          {fraudDetected && (
            <Card className="bg-red-950/20 border-red-600 p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-red-400">
                    Peringatan Kecurangan
                  </p>
                  <p className="text-xs text-red-300 mt-1">
                    VOID Cepat terdeteksi dengan keyakinan 94%. Admin telah diberitahu.
                  </p>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Features Highlight */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <Card className="bg-slate-800 border-slate-700 p-6 text-center">
          <div className="text-3xl font-bold text-cyan-400 mb-2">
            Langsung
          </div>
          <p className="text-sm text-slate-400">
            Deteksi dan peringatan instan dalam milidetik
          </p>
        </Card>
        <Card className="bg-slate-800 border-slate-700 p-6 text-center">
          <div className="text-3xl font-bold text-cyan-400 mb-2">94%</div>
          <p className="text-sm text-slate-400">
            Skor keyakinan rata-rata deteksi kecurangan
          </p>
        </Card>
        <Card className="bg-slate-800 border-slate-700 p-6 text-center">
          <div className="text-3xl font-bold text-cyan-400 mb-2">6 Aturan</div>
          <p className="text-sm text-slate-400">
            Algoritma deteksi kecurangan berlapis
          </p>
        </Card>
      </div>
    </section>
  );
}
