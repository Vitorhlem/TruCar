# simulator.py
import requests
import time
from datetime import datetime

# -- CONFIGURAÇÃO --
TRUCAR_API_ENDPOINT = "http://127.0.0.1:8000/api/v1/telemetry/report"
# Este ID deve corresponder ao que você cadastrou no seu DB para um veículo
DEVICE_ID = "TRATOR-001" 

# -- ESTADO INICIAL DO VEÍCULO VIRTUAL --
latitude = -23.5505
longitude = -46.6333
engine_hours = 1250.5

print(f"--- Iniciando Simulador para o Dispositivo: {DEVICE_ID} ---")
print(f"Enviando dados para: {TRUCAR_API_ENDPOINT}")

while True:
    try:
        # 1. Simula o trabalho: move um pouco e aumenta o horímetro
        latitude += 0.0001
        longitude += 0.0001
        engine_hours += 0.0027 # Aproximadamente 1 hora a cada hora real (10s / 3600s)

        # 2. Monta o pacote de dados
        payload = {
            "device_id": DEVICE_ID,
            "timestamp": datetime.utcnow().isoformat(),
            "latitude": latitude,
            "longitude": longitude,
            "engine_hours": round(engine_hours, 2),
        }

        # 3. Envia os dados para o "Ouvinte" do TruCar
        response = requests.post(TRUCAR_API_ENDPOINT, json=payload)
        
        if response.status_code == 204:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Posição enviada com sucesso: Lat {latitude:.4f}, Lon {longitude:.4f}, Horas {engine_hours:.2f}")
        else:
            print(f"[ERRO] Falha ao enviar dados: {response.status_code} - {response.text}")

        # 4. Espera 10 segundos para o próximo envio
        time.sleep(10)

    except requests.exceptions.RequestException as e:
        print(f"[ERRO DE CONEXÃO] Não foi possível conectar ao servidor: {e}")
        time.sleep(15)
    except KeyboardInterrupt:
        print("\n--- Simulador encerrado. ---")
        break