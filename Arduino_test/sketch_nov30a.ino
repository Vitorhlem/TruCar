#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <TinyGPS++.h>
#include "FS.h"
#include "SD.h"
#include "SPI.h"
#include <Wire.h>
#include <time.h>

// ================= CONFIGURAÇÕES =================
const char* ssid = "CFP661_EDUC";
const char* password = "6613duck";

// URL da API (Confirmada pela estrutura do projeto)
const char* serverUrl = "https://trucar.onrender.com/telemetry/sync"; 

// ID do Veículo (Use 5 conforme seus testes anteriores, ou altere se criou o veiculo 1)
const int VEHICLE_ID = 5; 

// ================= PINAGEM =================
#define SD_CS   5
#define SD_SCK  18
#define SD_MISO 19
#define SD_MOSI 23

#define I2C_SDA 21
#define I2C_SCL 22

#define GPS_RX 16 
#define GPS_TX 17 

#define LED_PIN 2

// ================= OBJETOS =================
Adafruit_MPU6050 mpu;
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);

// ================= VARIÁVEIS =================
unsigned long lastCapture = 0;
unsigned long lastSync = 0;
const int CAPTURE_INTERVAL = 1000; // Gravar a cada 1s
const int SYNC_INTERVAL = 15000;   // Tentar enviar a cada 15s

unsigned long getUnixTime() {
  if (!gps.date.isValid() || !gps.time.isValid()) return 0;
  struct tm tm;
  tm.tm_year = gps.date.year() - 1900;
  tm.tm_mon = gps.date.month() - 1;
  tm.tm_mday = gps.date.day();
  tm.tm_hour = gps.time.hour();
  tm.tm_min = gps.time.minute();
  tm.tm_sec = gps.time.second();
  tm.tm_isdst = 0;
  time_t t = mktime(&tm);
  return (unsigned long)t;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  
  // I2C MPU
  Wire.begin(I2C_SDA, I2C_SCL);
  if (!mpu.begin()) {
    Serial.println("! MPU Erro");
    while(1); // Trava se não tiver sensor
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("MPU OK");
  }

  // GPS
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  // SD
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS)) {
    Serial.println("! SD Erro");
  } else {
    Serial.println("SD OK");
  }

  // WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi...");
}

void gravarPonto() {
  // --- CRÍTICO: Validação de Data ---
  // O servidor Python rejeita datas < 2024. 
  // Se o GPS não pegou sinal, a data será 1970 e o dado será perdido.
  unsigned long ts = getUnixTime();
  
  // MODO PRODUÇÃO (Descomente para usar no caminhão real):
  if (ts < 1704067200) { // Menor que 01/01/2024
     // Serial.println("Aguardando GPS para gravar..."); 
     // return; 
     
     // MODO TESTE DE BANCADA (Sem GPS):
     // Usamos uma data fixa para o servidor aceitar o dado
     ts = 1715000000 + (millis()/1000); 
  }

  File file = SD.open("/trip_log.json", FILE_APPEND);
  if (!file) {
     file = SD.open("/trip_log.json", FILE_WRITE);
     if(!file) return; 
  }

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  StaticJsonDocument<256> line;
  
  float lat = gps.location.isValid() ? gps.location.lat() : -21.135; // Lat fixa se sem GPS (teste)
  float lng = gps.location.isValid() ? gps.location.lng() : -47.980; // Lng fixa se sem GPS (teste)
  float spd = gps.speed.isValid() ? gps.speed.kmph() : 0.0;

  line["lat"] = lat;
  line["lng"] = lng;
  line["spd"] = spd;
  line["ts"] = ts;

  float accZ = a.acceleration.z;
  // Detectar buraco (Impacto forte no eixo Z)
  if (abs(accZ) > 18.0 || abs(accZ) < 2.0) { 
       line["pothole"] = true; 
       line["z"] = accZ;
  } 

  serializeJson(line, file);
  file.println();
  file.close();
  // Serial.println("Ponto gravado.");
}

void sincronizar() {
  if (!SD.exists("/trip_log.json")) return;
  if (WiFi.status() != WL_CONNECTED) return;

  // Renomeia para processamento seguro
  SD.remove("/sending.json");
  SD.rename("/trip_log.json", "/sending.json");

  File file = SD.open("/sending.json", FILE_READ);
  if (!file) return;

  WiFiClientSecure client;
  client.setInsecure(); // Ignora validação SSL (necessário para Render/HTTPS simples)
  client.setTimeout(15000);

  HTTPClient http;
  
  // Prepara conexão (reutilizada se possível, mas o begin reinicia)
  if (!http.begin(client, serverUrl)) {
    file.close();
    SD.rename("/sending.json", "/trip_log.json");
    return;
  }

  bool criticalError = false;

  // Loop principal de leitura do arquivo
  while (file.available()) {
      
      // Cria o documento JSON novo para CADA LOTE (Batch)
      // Isso evita fragmentação de memória e dados residuais
      DynamicJsonDocument doc(16384); 
      
      doc["vehicle_id"] = VEHICLE_ID;
      doc.createNestedArray("events"); 
      JsonArray points = doc.createNestedArray("points");

      int count = 0;
      
      // Lê até 50 linhas ou fim do arquivo
      while (file.available() && count < 50) {
        String s = file.readStringUntil('\n');
        s.trim();
        if (s.length() == 0) continue;

        StaticJsonDocument<256> temp;
        DeserializationError error = deserializeJson(temp, s);

        if (!error) {
            JsonObject p = points.createNestedObject();
            p["lat"] = temp["lat"];
            p["lng"] = temp["lng"];
            p["spd"] = temp["spd"];
            p["ts"]  = temp["ts"];
            
            if (temp.containsKey("pothole")) {
                p["pothole_detected"] = true;
                p["acc_z"] = temp["z"];
            } else {
                p["acc_z"] = 0.0; // Padrão necessário pelo schema Pydantic às vezes
            }
            count++;
        }
      }

      // Se montou um lote, envia
      if (count > 0) {
         String jsonPayload;
         serializeJson(doc, jsonPayload);
         
         Serial.print("Enviando lote de ");
         Serial.print(count);
         Serial.println(" pontos...");

         http.addHeader("Content-Type", "application/json");
         int httpCode = http.POST(jsonPayload);

         if (httpCode == 200 || httpCode == 201) {
             Serial.println("✅ Lote enviado com sucesso!");
             // Pisca LED rápido
             for(int i=0;i<3;i++) { digitalWrite(LED_PIN, HIGH); delay(50); digitalWrite(LED_PIN, LOW); delay(50); }
         } else {
             Serial.print("❌ Erro HTTP: ");
             Serial.println(httpCode);
             String resp = http.getString();
             Serial.println(resp);
             criticalError = true;
             break; // Para o envio se der erro, para não perder dados
         }
      }
  }

  file.close();
  http.end();

  // Se deu tudo certo, apaga o arquivo temporário
  // Se deu erro, renomeia de volta (os dados processados serão reenviados, duplicidade é melhor que perda)
  if (criticalError) {
      // Nota: O ideal seria remover as linhas já lidas, mas para simplificar,
      // em caso de erro mantemos tudo para tentar depois.
      SD.remove("/trip_log.json"); // Remove se tiver criado um novo vazio nesse meio tempo
      SD.rename("/sending.json", "/trip_log.json");
  } else {
      SD.remove("/sending.json");
  }
}

void loop() {
  // Mantém buffer GPS limpo
  while (gpsSerial.available() > 0) gps.encode(gpsSerial.read());

  unsigned long now = millis();

  // 1. Captura (Gravação no SD)
  if (now - lastCapture > CAPTURE_INTERVAL) {
    lastCapture = now;
    gravarPonto();
  }

  // 2. Sincronização (Envio via WiFi)
  if (now - lastSync > SYNC_INTERVAL) {
    lastSync = now;
    if (WiFi.status() == WL_CONNECTED) {
      sincronizar();
    } else {
      Serial.println("WiFi desconectado. Tentando reconectar...");
      WiFi.reconnect();
    }
  }
}