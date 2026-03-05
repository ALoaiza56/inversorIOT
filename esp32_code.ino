#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// 🔹 Datos WiFi
const char* ssid = "univalle";
const char* password = "Univalle";

// 🔹 IP del servidor Flask
// Tu PC tiene la IP: 192.168.69.255
// Tu ESP32 tiene la IP: 192.168.70.55
const char* serverName = "http://192.168.69.255:5000"; 

// 🔹 LED interno ESP32
const int ledPin = 2;

// 🔹 Variables simuladas
float voltaje1, voltaje2, corriente1, corriente2;

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado!");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // 🔹 Simulación de valores
    voltaje1 = random(210, 230) + random(0, 100)/100.0;
    voltaje2 = random(210, 230) + random(0, 100)/100.0;
    corriente1 = random(5, 15) + random(0, 100)/100.0;
    corriente2 = random(5, 15) + random(0, 100)/100.0;

    enviarDatos();
    consultarComando();
  } else {
    Serial.println("WiFi desconectado. Reintentando...");
    WiFi.begin(ssid, password);
  }

  delay(5000);  // cada 5 segundos
}

void enviarDatos() {
  HTTPClient http;
  String url = String(serverName) + "/guardar";

  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Crear documento JSON
  StaticJsonDocument<200> doc;
  doc["v1"] = voltaje1;
  doc["v2"] = voltaje2;
  doc["i1"] = corriente1;
  doc["i2"] = corriente2;

  String jsonOutput;
  serializeJson(doc, jsonOutput);

  int httpResponseCode = http.POST(jsonOutput);

  Serial.println("---- ENVIO DATOS (JSON) ----");
  Serial.print("Payload: "); Serial.println(jsonOutput);
  Serial.print("Codigo HTTP: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Respuesta servidor: " + response);
  } else {
    Serial.print("Error enviando datos. Codigo: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}

void consultarComando() {
  HTTPClient http;
  String url = String(serverName) + "/comando";

  http.begin(url);
  int httpResponseCode = http.GET();

  Serial.println("---- CONSULTA COMANDO ----");

  if (httpResponseCode == 200) {
    String payload = http.getString();
    payload.trim();

    Serial.println("Estado recibido: " + payload);

    if (payload == "ON") {
      digitalWrite(ledPin, HIGH);
      Serial.println("LED ENCENDIDO");
    }
    else if (payload == "OFF") {
      digitalWrite(ledPin, LOW);
      Serial.println("LED APAGADO");
    }
  } else {
    Serial.print("Error consultando comando. Codigo: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}
