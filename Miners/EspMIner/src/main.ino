// creditos Sec Coin & Duino Coin Team
#include <Arduino.h>
#include <ESP8266WiFi.h> // Include WiFi library
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <Crypto.h>
using namespace experimental::crypto;

namespace {
  const char* ssid          = "WiFi SSID";  
  const char* password      = "WiFi Pass";    
  const char* ducouser      = "Sec Username";     
  const char* rigIdentifier = "None";       

  const char * host = "159.65.220.57"; 
  const int port = 2811;
  unsigned int Shares = 0; // Share variable

  WiFiClient client;
  String clientBuffer = "";

  #define END_TOKEN  '\n'
  #define SEP_TOKEN  ','

  #define LED_BUILTIN 2

  #define BLINK_SHARE_FOUND    1
  #define BLINK_SETUP_COMPLETE 2
  #define BLINK_CLIENT_CONNECT 3
  #define BLINK_RESET_DEVICE   5

  void SetupWifi() {
    Serial.println("Connecting to: " + String(ssid));
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password); i

    int wait_passes = 0;
    while (WiFi.waitForConnectResult() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      if (++wait_passes >= 10) {
        WiFi.begin(ssid, password);
        wait_passes = 0;
      }
    }

    Serial.println("\nConnected to WiFi!");
    Serial.println("Ip Local: " + WiFi.localIP().toString());
  }

  void SetupOTA() {
    ArduinoOTA.onStart([]() { // Prepare OTA stuff
      Serial.println("Start");
    });
    ArduinoOTA.onEnd([]() {
      Serial.println("\nEnd");
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

    ArduinoOTA.setHostname(rigIdentifier); 
    ArduinoOTA.begin();
  }

  void blink(uint8_t count, uint8_t pin = LED_BUILTIN) {
    uint8_t state = HIGH;

    for (int x=0; x<(count << 1); ++x) {
      digitalWrite(pin, state ^= HIGH);
      delay(50);
    }
  }

  void RestartESP(String msg) {
    Serial.println(msg);
    Serial.println("Resetting ESP...");
    blink(BLINK_RESET_DEVICE); 
    ESP.reset();
  }

  void VerifyWifi() {
    unsigned long lastMillis = millis();
    
    while (WiFi.status() != WL_CONNECTED || WiFi.localIP() == IPAddress(0,0,0,0)) {
      WiFi.reconnect();

      if ((millis() - lastMillis) > 60000) {
        // after 1-minute of failed re-connects... 
        RestartESP("N??o foi Possivel se conectar ao wifi");
      }
    }
  }

  void handleSystemEvents(void) {
    VerifyWifi();
    ArduinoOTA.handle();
    yield();
  }

  String getValue(String data, char separator, int index)
  {
    int found = 0;
    int strIndex[] = {0, -1};
    int maxIndex = data.length()-1;

    for(int i=0; i<=maxIndex && found<=index; i++){
      if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
      }
    }

    return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
  }
  
  void waitForClientData(void) {
    clientBuffer = "";
    
    while (client.connected()) {
      if (client.available()) {
        clientBuffer = client.readStringUntil(END_TOKEN);
        if (clientBuffer.length() == 1 && clientBuffer[0] == END_TOKEN)
          clientBuffer = "???\n"; // NOTE: Should never happen...

        break;
      }
      handleSystemEvents();
    }
  }

  void ConnectToServer() {
    if (client.connected())
      return;

    if (!client.connect(host, port)) 
      RestartESP("Connection failed.");
  
    waitForClientData();
    blink(BLINK_CLIENT_CONNECT); 
  }

  bool max_micros_elapsed(unsigned long current, unsigned long max_elapsed) {
    static unsigned long _start = 0;

    if ((current - _start) > max_elapsed) {
      _start = current;
      return true;
    }
      
    return false;
  }
} // namespace

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); 

  SetupWifi();
  SetupOTA();

  blink(BLINK_SETUP_COMPLETE); 
}

void loop() {
  VerifyWifi();
  ArduinoOTA.handle(); // Enable OTA handler
  ConnectToServer();

  client.print("JOB," + String(ducouser) + ",ESP8266"); // Ask for new job
  waitForClientData();

  String hash = getValue(clientBuffer, SEP_TOKEN, 0); 
  String job = getValue(clientBuffer, SEP_TOKEN, 1);
  unsigned int diff = getValue(clientBuffer, SEP_TOKEN, 2).toInt() * 100 + 1; 
  job.toUpperCase();

  float StartTime = micros(); // Start time measurement
  max_micros_elapsed(StartTime, 0);

  for (unsigned int iJob = 0; iJob < diff; iJob++) { // Difficulty loop
    String result = SHA1::hash(hash + String(iJob));

    if (result == job) { // If result is found
      unsigned long ElapsedTime = micros() - StartTime;  // Calculate elapsed time
      float ElapsedTimeSeconds = ElapsedTime * .000001f; // Convert to seconds
      float HashRate = iJob / ElapsedTimeSeconds;

      client.print(String(iJob) + "," + String(HashRate) + ",ESP8266 Miner v1.0" + "," + String(rigIdentifier)); r
      waitForClientData();

      Shares++;
      blink(BLINK_SHARE_FOUND);
      break; // Stop and ask for more work
    }

    if (max_micros_elapsed(micros(), 250000)) 
      handleSystemEvents();
      
  }
}
