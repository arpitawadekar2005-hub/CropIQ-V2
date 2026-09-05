#include <WiFi.h>
#include <WebSocketsClient.h>

// =====================================================
// WIFI
// =====================================================

const char* WIFI_SSID = "OPPO";
const char* WIFI_PASSWORD = "nrsf3263";

// =====================================================
// CROP-IQ RENDER BACKEND
// =====================================================

const char* SERVER_HOST = "cropiq-backend-mecl.onrender.com";
const int SERVER_PORT = 443;
const char* SERVER_PATH = "/ws/esp32";

// =====================================================
// MOTOR PINS
// =====================================================

#define LmotorA 27
#define LmotorB 26

#define RmotorA 25
#define RmotorB 33

// =====================================================
// WEBSOCKET
// =====================================================

WebSocketsClient webSocket;


// =====================================================
// MOTOR FUNCTIONS
// =====================================================

void Forward() {

  digitalWrite(LmotorA, HIGH);
  digitalWrite(LmotorB, LOW);

  digitalWrite(RmotorA, HIGH);
  digitalWrite(RmotorB, LOW);

  Serial.println("ROVER: FORWARD");

  if (webSocket.isConnected()) {
    webSocket.sendTXT("ROVER_FORWARD");
  }
}


void Backward() {

  digitalWrite(LmotorA, LOW);
  digitalWrite(LmotorB, HIGH);

  digitalWrite(RmotorA, LOW);
  digitalWrite(RmotorB, HIGH);

  Serial.println("ROVER: BACKWARD");

  if (webSocket.isConnected()) {
    webSocket.sendTXT("ROVER_BACKWARD");
  }
}


void Left() {

  digitalWrite(LmotorA, LOW);
  digitalWrite(LmotorB, HIGH);

  digitalWrite(RmotorA, HIGH);
  digitalWrite(RmotorB, LOW);

  Serial.println("ROVER: LEFT");

  if (webSocket.isConnected()) {
    webSocket.sendTXT("ROVER_LEFT");
  }
}


void Right() {

  digitalWrite(LmotorA, HIGH);
  digitalWrite(LmotorB, LOW);

  digitalWrite(RmotorA, LOW);
  digitalWrite(RmotorB, HIGH);

  Serial.println("ROVER: RIGHT");

  if (webSocket.isConnected()) {
    webSocket.sendTXT("ROVER_RIGHT");
  }
}


void Stop() {

  digitalWrite(LmotorA, LOW);
  digitalWrite(LmotorB, LOW);

  digitalWrite(RmotorA, LOW);
  digitalWrite(RmotorB, LOW);

  Serial.println("ROVER: STOPPED");

  if (webSocket.isConnected()) {
    webSocket.sendTXT("ROVER_STOPPED");
  }
}


// =====================================================
// PROCESS COMMAND FROM BACKEND
// =====================================================

void processCommand(String command) {

  command.trim();
  command.toUpperCase();

  Serial.print("COMMAND RECEIVED: ");
  Serial.println(command);

  if (command == "F") {

    Forward();

  }
  else if (command == "B") {

    Backward();

  }
  else if (command == "L") {

    Left();

  }
  else if (command == "R") {

    Right();

  }
  else if (command == "S") {

    Stop();

  }
  else {

    Serial.println("UNKNOWN COMMAND");

    Stop();
  }
}


// =====================================================
// WEBSOCKET EVENT HANDLER
// =====================================================

void webSocketEvent(
  WStype_t type,
  uint8_t* payload,
  size_t length
) {

  switch (type) {

    // -------------------------------------------------
    // BACKEND DISCONNECTED
    // -------------------------------------------------

    case WStype_DISCONNECTED:

      Serial.println("BACKEND: DISCONNECTED");

      // SAFETY STOP
      digitalWrite(LmotorA, LOW);
      digitalWrite(LmotorB, LOW);

      digitalWrite(RmotorA, LOW);
      digitalWrite(RmotorB, LOW);

      break;


    // -------------------------------------------------
    // BACKEND CONNECTED
    // -------------------------------------------------

    case WStype_CONNECTED:

      Serial.println("BACKEND: CONNECTED");

      // Tell FastAPI that ESP32 is ready
      webSocket.sendTXT("ESP32_READY");

      break;


    // -------------------------------------------------
    // TEXT COMMAND RECEIVED
    // -------------------------------------------------

    case WStype_TEXT: {

      String command = "";

      for (size_t i = 0; i < length; i++) {

        command += (char)payload[i];

      }

      processCommand(command);

      break;
    }


    default:

      break;
  }
}


// =====================================================
// CONNECT TO WIFI
// =====================================================

void connectWiFi() {

  Serial.println();
  Serial.println("================================");
  Serial.println("Connecting to Wi-Fi...");
  Serial.println("================================");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi Connected!");

  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}


// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("       CropIQ Rover ESP32");
  Serial.println("================================");


  // -------------------------------------------------
  // MOTOR PINS
  // -------------------------------------------------

  pinMode(LmotorA, OUTPUT);
  pinMode(LmotorB, OUTPUT);

  pinMode(RmotorA, OUTPUT);
  pinMode(RmotorB, OUTPUT);


  // -------------------------------------------------
  // SAFETY STOP AT STARTUP
  // -------------------------------------------------

  digitalWrite(LmotorA, LOW);
  digitalWrite(LmotorB, LOW);

  digitalWrite(RmotorA, LOW);
  digitalWrite(RmotorB, LOW);

  Serial.println("Motors initialized.");
  Serial.println("Rover stopped.");


  // -------------------------------------------------
  // WIFI
  // -------------------------------------------------

  connectWiFi();


  // -------------------------------------------------
  // WEBSOCKET CONNECTION
  // -------------------------------------------------

  Serial.println();
  Serial.println("Connecting to CropIQ backend...");

  webSocket.beginSSL(
    SERVER_HOST,
    SERVER_PORT,
    SERVER_PATH
  );

  webSocket.onEvent(webSocketEvent);

  // Try reconnecting every 5 seconds
  webSocket.setReconnectInterval(5000);

  Serial.println("WebSocket initialized.");
}


// =====================================================
// MAIN LOOP
// =====================================================

void loop() {

  webSocket.loop();
}
