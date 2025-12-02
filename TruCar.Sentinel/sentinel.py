import cv2
import time
import requests
from ultralytics import YOLO
from datetime import datetime

# --- CONFIGURAÇÕES ---
TRUCK_ID = "1"
API_URL = "http://localhost:8000/alerts/alert" # Endereço local do TruCar
ALERT_THRESHOLD = 10.0 # Segundos detectando para disparar alerta
COOLDOWN_TIME = 10.0 # Segundos entre um alerta e outro (para não spammar)

# Carrega o modelo YOLOv8 Nano (mais leve e rápido)
# Na primeira execução, ele vai baixar o arquivo 'yolov8n.pt' automaticamente
print("Carregando modelo IA...")
model = YOLO('yolov8n.pt') 

# IDs das classes no COCO Dataset: 
# 0 = person (motorista)
# 67 = cell phone (celular)
TARGET_CLASSES = [0, 67] 

def send_alert_to_trucar(frame, truck_id, event_type):
    """
    Função que envia o alerta para o Backend do TruCar.
    Em produção, isso salvaria em cache local se estivesse sem internet.
    """
    payload = {
        "truck_id": truck_id,
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "severity": "CRITICAL",
        "description": "Motorista detectado usando celular por mais de 2 segundos."
    }
    
    print(f"\n🚨 ENVIANDO ALERTA PARA TRUCAR: {payload}")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=2)
        print(f"Status API: {response.status_code}")
    except Exception as e:
        print(f"Erro de conexão com TruCar: {e}")
        
def main():
    # Abre a webcam (0 é geralmente a webcam padrão)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro ao abrir webcam.")
        return

    # Variáveis de Estado
    phone_start_time = None
    last_alert_time = 0
    
    print("Sentinel iniciado. Pressione 'q' para sair.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # 1. Inferência (A mágica da IA)
        # conf=0.5 significa: só mostre se tiver 50% de certeza
        results = model(frame, verbose=False, conf=0.5, classes=[67]) 

        phone_detected = False

        # 2. Processar Resultados
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Desenhar retângulo no vídeo
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, "CELULAR", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                phone_detected = True

        # 3. Lógica Temporal (Senior Logic)
        current_time = time.time()

        if phone_detected:
            if phone_start_time is None:
                phone_start_time = current_time # Começou a olhar pro celular agora
            
            elapsed = current_time - phone_start_time
            
            # Se passou do tempo limite e não está em cooldown
            if elapsed > ALERT_THRESHOLD and (current_time - last_alert_time) > COOLDOWN_TIME:
                # DISPARAR ALERTA!
                cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 255), -1) # Flash vermelho na tela
                cv2.putText(frame, "ALERTA: USO DE CELULAR!", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                send_alert_to_trucar(frame, TRUCK_ID, "DISTRACTION_CELLPHONE")
                last_alert_time = current_time # Reseta cooldown

        else:
            phone_start_time = None # Motorista largou o celular, reseta cronômetro

        # Mostrar o vídeo
        cv2.imshow('TruCar Sentinel - Edge View', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()