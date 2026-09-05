#include <WiFi.h>
#include <WebSocketsClient.h>
#include "secrets.h"

// =====================================================
// RENDER BACKEND
// =====================================================

const char* SERVER_HOST =
    "cropiq-backend-mecl.onrender.com";

const int SERVER_PORT = 443;

const char* SERVER_PATH =
    "/ws/esp32";


// =====================================================
// MOTOR PINS
// =====================================================

// LEFT MOTOR
#define LmotorA 27
#define LmotorB 26

// RIGHT MOTOR
#define RmotorA 25
#define RmotorB 33


// =====================================================
// WEBSOCKET
// =====================================================

WebSocketsClient webSocket;


// =====================================================
// FORWARD
// =====================================================

void Forward()
{
    digitalWrite(LmotorA, HIGH);
    digitalWrite(LmotorB, LOW);

    digitalWrite(RmotorA, HIGH);
    digitalWrite(RmotorB, LOW);

    Serial.println("FORWARD");

    if (webSocket.isConnected())
    {
        webSocket.sendTXT("ROVER_FORWARD");
    }
}


// =====================================================
// BACKWARD
// =====================================================

void Backward()
{
    digitalWrite(LmotorA, LOW);
    digitalWrite(LmotorB, HIGH);

    digitalWrite(RmotorA, LOW);
    digitalWrite(RmotorB, HIGH);

    Serial.println("BACKWARD");

    if (webSocket.isConnected())
    {
        webSocket.sendTXT("ROVER_BACKWARD");
    }
}


// =====================================================
// RIGHT
// =====================================================

void Right()
{
    digitalWrite(LmotorA, HIGH);
    digitalWrite(LmotorB, LOW);

    digitalWrite(RmotorA, LOW);
    digitalWrite(RmotorB, HIGH);

    Serial.println("RIGHT");

    if (webSocket.isConnected())
    {
        webSocket.sendTXT("ROVER_RIGHT");
    }
}


// =====================================================
// LEFT
// =====================================================

void Left()
{
    digitalWrite(LmotorA, LOW);
    digitalWrite(LmotorB, HIGH);

    digitalWrite(RmotorA, HIGH);
    digitalWrite(RmotorB, LOW);

    Serial.println("LEFT");

    if (webSocket.isConnected())
    {
        webSocket.sendTXT("ROVER_LEFT");
    }
}


// =====================================================
// STOP
// =====================================================

void Stop()
{
    digitalWrite(LmotorA, LOW);
    digitalWrite(LmotorB, LOW);

    digitalWrite(RmotorA, LOW);
    digitalWrite(RmotorB, LOW);

    Serial.println("STOP");

    if (webSocket.isConnected())
    {
        webSocket.sendTXT("ROVER_STOPPED");
    }
}


// =====================================================
// PROCESS COMMAND
// =====================================================

void processCommand(String command)
{
    command.trim();
    command.toUpperCase();

    Serial.print("Command received: ");
    Serial.println(command);


    if (command == "F")
    {
        Forward();
    }

    else if (command == "B")
    {
        Backward();
    }

    else if (command == "L")
    {
        Left();
    }

    else if (command == "R")
    {
        Right();
    }

    else if (command == "S")
    {
        Stop();
    }

    else
    {
        Serial.println("Unknown command");

        Stop();
    }
}


// =====================================================
// WEBSOCKET EVENT
// =====================================================

void webSocketEvent(
    WStype_t type,
    uint8_t* payload,
    size_t length
)
{
    switch (type)
    {

        // =============================================
        // DISCONNECTED
        // =============================================

        case WStype_DISCONNECTED:

            Serial.println(
                "Backend disconnected"
            );

            // SAFETY STOP

            digitalWrite(
                LmotorA,
                LOW
            );

            digitalWrite(
                LmotorB,
                LOW
            );

            digitalWrite(
                RmotorA,
                LOW
            );

            digitalWrite(
                RmotorB,
                LOW
            );

            break;


        // =============================================
        // CONNECTED
        // =============================================

        case WStype_CONNECTED:

            Serial.println(
                "Backend connected"
            );

            // Tell backend that ESP32 is ready

            webSocket.sendTXT(
                "ESP32_READY"
            );

            break;


        // =============================================
        // TEXT MESSAGE
        // =============================================

        case WStype_TEXT:
        {
            String command = "";

            for (
                size_t i = 0;
                i < length;
                i++
            )
            {
                command +=
                    (char)payload[i];
            }

            processCommand(
                command
            );

            break;
        }


        default:

            break;
    }
}


// =====================================================
// WIFI CONNECTION
// =====================================================

void connectWiFi()
{
    Serial.println();

    Serial.println(
        "Connecting to Wi-Fi..."
    );


    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );


    while (
        WiFi.status()
        != WL_CONNECTED
    )
    {
        delay(500);

        Serial.print(".");
    }


    Serial.println();

    Serial.println(
        "Wi-Fi Connected"
    );


    Serial.print(
        "ESP32 IP: "
    );

    Serial.println(
        WiFi.localIP()
    );
}


// =====================================================
// SETUP
// =====================================================

void setup()
{
    Serial.begin(115200);


    // =================================================
    // MOTOR PINS
    // =================================================

    pinMode(
        LmotorA,
        OUTPUT
    );

    pinMode(
        LmotorB,
        OUTPUT
    );

    pinMode(
        RmotorA,
        OUTPUT
    );

    pinMode(
        RmotorB,
        OUTPUT
    );


    // =================================================
    // SAFETY STOP
    // =================================================

    digitalWrite(
        LmotorA,
        LOW
    );

    digitalWrite(
        LmotorB,
        LOW
    );

    digitalWrite(
        RmotorA,
        LOW
    );

    digitalWrite(
        RmotorB,
        LOW
    );


    // =================================================
    // STARTUP MESSAGE
    // =================================================

    Serial.println();

    Serial.println(
        "================================"
    );

    Serial.println(
        "          CropIQ ROVER"
    );

    Serial.println(
        "            ESP32"
    );

    Serial.println(
        "================================"
    );


    // =================================================
    // WIFI
    // =================================================

    connectWiFi();


    // =================================================
    // WEBSOCKET
    // =================================================

    webSocket.beginSSL(
        SERVER_HOST,
        SERVER_PORT,
        SERVER_PATH
    );


    webSocket.onEvent(
        webSocketEvent
    );


    // Reconnect automatically

    webSocket.setReconnectInterval(
        5000
    );


    Serial.println();

    Serial.println(
        "Connecting to Render..."
    );
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
    webSocket.loop();
}
