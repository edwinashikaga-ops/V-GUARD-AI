from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="V-Guard AI Gateway")

# Model data untuk kiriman dari CCTV/Visionary
class DetectionData(BaseModel):
    camera_id: str
    object_name: str
    confidence: float
    timestamp: str

# Model data untuk kiriman dari Kasir/Liaison
class TransactionData(BaseModel):
    pos_system: str
    transaction_id: str
    item_name: str
    amount: float

# Endpoint 1: Menerima data dari CCTV Lokal
@app.post("/v1/visionary/detect")
async def receive_detection(data: DetectionData, vguard_key: str = Header(None)):
    if vguard_key != "VGUARD_SECRET_2026": # Ganti dengan key Bapak
        raise HTTPException(status_code=403, detail="Akses Ditolak")
    
    # Logika: Kirim ke modul vguard_sync untuk dicocokkan
    return {"status": "success", "message": f"Deteksi {data.object_name} diterima"}

# Endpoint 2: Menerima data dari POS/Kasir
@app.post("/v1/liaison/pos-sync")
async def receive_pos(data: TransactionData):
    # Logika: Tandai transaksi sebagai 'Verified' di dashboard
    return {"status": "connected", "pos": data.pos_system}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
