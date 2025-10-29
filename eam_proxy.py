# ==============================================================
# 🌐 API IoT Cloud - Conexão entre ESP32 e App Desktop
# ==============================================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

app = FastAPI(title="IoT Cloud API", version="1.0")

# ==============================================================
# 📊 Armazenamento em memória dos status (pode futuramente usar Redis ou DB)
# ==============================================================

devices_status = {}

# ==============================================================
# 📡 ESP32 envia eventos aqui
# ==============================================================

@app.post("/event")
async def receive_event(request: Request):
    """Recebe dados de status enviados pelo ESP32"""
    data = await request.json()
    device = data.get("device", "desconhecido")
    status = data.get("status", "sem_status")

    devices_status[device] = {
        "status": status,
        "last_update": datetime.now().isoformat()
    }

    print(f"📡 Evento recebido → {device} = {status}")
    return {"message": "Evento recebido com sucesso", "device": device, "status": status}


# ==============================================================
# 📈 App Desktop consulta o status do dispositivo
# ==============================================================

@app.get("/status/{device_id}")
async def get_status(device_id: str):
    """Retorna o status atual de um dispositivo"""
    info = devices_status.get(device_id)

    if not info:
        return JSONResponse(
            content={
                "device": device_id,
                "status": "desconhecido",
                "online": False
            },
            status_code=200
        )

    delta = datetime.now() - datetime.fromisoformat(info["last_update"])
    online = delta < timedelta(seconds=15)

    return {
        "device": device_id,
        "status": info["status"],
        "last_update": info["last_update"],
        "online": online
    }


# ==============================================================
# 🔍 Endpoint básico de verificação
# ==============================================================

@app.get("/")
def root():
    return {"status": "ok", "message": "API IoT na nuvem ativa e recebendo eventos."}


# ==============================================================
# 🚀 Execução local (opcional)
# ==============================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Executando IoT Cloud API em http://127.0.0.1:8080 ...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
