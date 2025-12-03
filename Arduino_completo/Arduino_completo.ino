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

const char* serverUrl = "https://trucar.onrender.com/telemetry/sync"; 
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
const int CAPTURE_INTERVAL = 1000; 
const int SYNC_INTERVAL = 15000;   

// --- FERRAMENTA DE DIAGNÓSTICO I2C ---
void scannerI2C() {
  byte error, address;
  int nDevices = 0;
  Serial.println("\n--- INICIANDO SCANNER I2C ---");
  Serial.println("Verificando pinos SDA=" + String(I2C_SDA) + " SCL=" + String(I2C_SCL));
  
  for(address = 1; address < 127; address++ ) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("✅ Dispositivo I2C encontrado no endereço: 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      
      if (address == 0x68) Serial.print(" (Provavelmente MPU6050 ou DS3231)");
      if (address == 0x69) Serial.print(" (Provavelmente MPU6050 Alt)");
      
      Serial.println();
      nDevices++;
    } else if (error == 4) {
      Serial.print("❓ Erro desconhecido no endereço 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }
  if (nDevices == 0) {
    Serial.println("❌ NENHUM dispositivo I2C encontrado.\nVerifique:\n1. Fios SDA/SCL invertidos?\n2. Fios soltos?\n3. O sensor tem energia (VCC/GND)?");
  } else {
    Serial.println("--- FIM DO SCANNER I2C ---\n");
  }
}

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
  delay(2000); // Espera abrir o monitor serial

  Serial.println("\n\n==================================");
  Serial.println("   TRUCAR - LOG DE DIAGNÓSTICO");
  Serial.println("==================================");
  
  // 1. I2C e MPU
  Wire.begin(I2C_SDA, I2C_SCL);
  scannerI2C(); // Roda o diagnóstico

  Serial.print("Inicializando MPU6050... ");
  if (!mpu.begin()) {
    Serial.println("❌ FALHA! (Tentando endereço 0x69...)");
    // Tenta endereço alternativo se o padrão falhar
    if (!mpu.begin(0x69)) {
        Serial.println("❌ FALHA TOTAL NO MPU. O sistema continuará sem acelerômetro.");
    } else {
        Serial.println("✅ MPU OK (Endereço 0x69)");
        setupMPU();
    }
  } else {
    Serial.println("✅ MPU OK (Endereço 0x68)");
    setupMPU();
  }

  // 2. GPS
  Serial.print("Inicializando GPS (RX:");
  Serial.print(GPS_RX);
  Serial.print(", TX:");
  Serial.print(GPS_TX);
  Serial.println(")...");
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);

  // 3. SD Card
  Serial.print("Inicializando Cartão SD... ");
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  if (!SD.begin(SD_CS)) {
    Serial.println("❌ FALHA NO SD! Verifique conexões ou formatação (FAT32).");
  } else {
    Serial.println("✅ SD OK.");
    Serial.printf("Espaço Total: %lluMB\n", SD.totalBytes() / (1024 * 1024));
    Serial.printf("Espaço Usado: %lluMB\n", SD.usedBytes() / (1024 * 1024));
  }

  // 4. WiFi
  WiFi.begin(ssid, password);
  Serial.println("Iniciando WiFi (não bloqueante)...");
}

void setupMPU() {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void debugGPS() {
    Serial.print("[GPS DEBUG] Satélites: ");
    Serial.print(gps.satellites.value());
    Serial.print(" | HDOP: ");
    Serial.print(gps.hdop.value());
    Serial.print(" | Caracteres lidos: ");
    Serial.println(gps.charsProcessed());

    if (gps.charsProcessed() < 10) {
        Serial.println("⚠️ ALERTA: Poucos dados do GPS. Verifique se TX/RX estão invertidos.");
    }
}

void gravarPonto() {
  File file = SD.open("/trip_log.json", FILE_APPEND);
  if (!file) {
     file = SD.open("/trip_log.json", FILE_WRITE);
     if(!file) {
        Serial.println("❌ Erro ao abrir arquivo no SD para escrita.");
        return; 
     }
  }

  StaticJsonDocument<300> line;
  
  // --- LÓGICA DE DADOS ---
  bool gpsValido = gps.location.isValid();
  
  float lat, lng, spd;
  unsigned long ts;

  if (gpsValido) {
      lat = gps.location.lat();
      lng = gps.location.lng();
      spd = gps.speed.kmph();
      ts = getUnixTime();
      Serial.printf("📍 GPS REAL: Lat %.6f | Lng %.6f | Vel %.1f km/h | Sat %d\n", lat, lng, spd, gps.satellites.value());
  } else {
      // DADOS MOCKADOS (FALSOS) PARA TESTE
      lat = -21.135; 
      lng = -47.980;
      spd = 0.0;
      ts = 1715000000 + (millis()/1000); // Data fake futura
      
      // AVISO VISUAL CLARO
      Serial.println("⚠️ GPS SEM SINAL (FIX): Usando coordenadas de teste (Sertãozinho). Mova para céu aberto.");
      debugGPS(); // Mostra detalhes do erro
  }

  line["lat"] = lat;
  line["lng"] = lng;
  line["spd"] = spd;
  line["ts"] = ts;

  // Leitura do MPU (se disponível)
  sensors_event_t a, g, temp;
  bool mpuSuccess = mpu.getEvent(&a, &g, &temp);
  
  if (mpuSuccess) {
      float accZ = a.acceleration.z;
      // Serial.printf("   MPU Z: %.2f m/s^2\n", accZ);
      
      if (abs(accZ) > 18.0 || abs(accZ) < 2.0) { 
          line["pothole"] = true; 
          line["z"] = accZ;
          Serial.println("   🕳️ BURACO DETECTADO!");
      } 
  } else {
      line["pothole"] = false;
      // Serial.println("   (MPU não lido)");
  }

  serializeJson(line, file);
  file.println();
  file.close();
}

void sincronizar() {
  if (!SD.exists("/trip_log.json")) return;
  if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Wifi desconectado, pulando sync.");
      return;
  }

  Serial.println("🔄 Iniciando sincronização com servidor...");

  SD.remove("/sending.json");
  SD.rename("/trip_log.json", "/sending.json");

  File file = SD.open("/sending.json", FILE_READ);
  if (!file) {
      Serial.println("Erro ao ler arquivo de envio.");
      return;
  }

  WiFiClientSecure client;
  client.setInsecure();
  client.setTimeout(15000);
  HTTPClient http;

  if (!http.begin(client, serverUrl)) {
    Serial.println("❌ Falha ao conectar no servidor.");
    file.close();
    SD.rename("/sending.json", "/trip_log.json");
    return;
  }

  // Loop de envio simplificado para debug
  DynamicJsonDocument doc(10000);
  doc["vehicle_id"] = VEHICLE_ID;
  doc.createNestedArray("events");
  JsonArray points = doc.createNestedArray("points");

  int count = 0;
  while (file.available() && count < 20) { // Envia lotes menores no debug
     String s = file.readStringUntil('\n');
     StaticJsonDocument<256> temp;
     if (!deserializeJson(temp, s)) {
         points.add(temp);
         count++;
     }
  }

  if (count > 0) {
      String json;
      serializeJson(doc, json);
      Serial.printf("📤 Enviando %d pontos (%d bytes)...\n", count, json.length());
      
      int code = http.POST(json);
      if (code == 200 || code == 201) {
          Serial.println("✅ ENVIO SUCESSO! 200 OK");
          SD.remove("/sending.json"); // Apaga só se deu certo
      } else {
          Serial.printf("❌ ERRO SERVIDOR: %d\n", code);
          Serial.println(http.getString());
          file.close();
          http.end();
          SD.rename("/sending.json", "/trip_log.json"); // Devolve dados
          return;
      }
  } else {
      SD.remove("/sending.json"); // Arquivo estava vazio ou corrompido
  }

  file.close();
  http.end();
}

void loop() {
  // Mantém leitura do GPS constante
  while (gpsSerial.available() > 0) {
      gps.encode(gpsSerial.read());
  }

  unsigned long now = millis();

  // Grava a cada 2 segundos para facilitar leitura do log
  if (now - lastCapture > 2000) {
    lastCapture = now;
    gravarPonto();
  }

  if (now - lastSync > SYNC_INTERVAL) {
    lastSync = now;
    if (WiFi.status() == WL_CONNECTED) {
        sincronizar();
    } else {
        Serial.print("WiFi: Conectando... ");
        Serial.println(WiFi.status());
    }
  }
}