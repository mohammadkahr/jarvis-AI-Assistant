#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* serverUrl = "http://192.****/get_device_states";

#define LED_KITCHEN  2
#define LED_BATHROOM 4
#define LED_ROOM1    5
#define LED_ROOM2    18

unsigned long lastTime = 0;
const long timerDelay = 5000;
void setup() {
  Serial.begin(115200);

  pinMode(LED_KITCHEN, OUTPUT);
  pinMode(LED_BATHROOM, OUTPUT);
  pinMode(LED_ROOM1, OUTPUT);
  pinMode(LED_ROOM2, OUTPUT);

  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if ((millis() - lastTime) > timerDelay) {
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;

      Serial.println("Requesting device states from server...");
      http.begin(serverUrl);
      int httpResponseCode = http.GET();

      if (httpResponseCode > 0) {
        Serial.printf("HTTP Response code: %d\n", httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);

        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, payload);

        if (error) {
          Serial.print("deserializeJson() failed: ");
          Serial.println(error.c_str());
          return;
        }

        const char* kitchen_light = doc["lights"]["kitchen"]; // "on" or "off"
        const char* bathroom_light = doc["lights"]["bathroom"];
        const char* room1_light = doc["lights"]["room1"];
        const char* room2_light = doc["lights"]["room2"];

        digitalWrite(LED_KITCHEN,  strcmp(kitchen_light, "on") == 0 ? HIGH : LOW);
        digitalWrite(LED_BATHROOM, strcmp(bathroom_light, "on") == 0 ? HIGH : LOW);
        digitalWrite(LED_ROOM1,    strcmp(room1_light, "on") == 0 ? HIGH : LOW);
        digitalWrite(LED_ROOM2,    strcmp(room2_light, "on") == 0 ? HIGH : LOW);

        Serial.println("LEDs updated successfully!");

      } else {
        Serial.printf("Error code: %d\n", httpResponseCode);
      }
      http.end();
    } else {
      Serial.println("WiFi Disconnected");
    }
    lastTime = millis();
  }
}