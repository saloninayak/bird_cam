#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// Wi-Fi
const char* ssid = "ADD HERE";
const char* password = "ADD HERE";

// Railway endpoint
const char* serverUrl =
    "https://birdcam-production-957f.up.railway.app/upload";

// PIR sensor
#define PIR_GPIO_NUM 12

// AI Thinker ESP32-CAM pins
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5

#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

WiFiClientSecure secureClient;

void connectToWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void uploadPhoto(camera_fb_t* frame) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected");
    connectToWiFi();
  }

  secureClient.setInsecure();  // Testing only
  secureClient.setTimeout(60000);

  HTTPClient http;
  http.setConnectTimeout(30000);
  http.setTimeout(60000);

  Serial.println("Connecting to Railway...");

  if (!http.begin(secureClient, serverUrl)) {
    Serial.println("Could not connect to upload endpoint");
    return;
  }

  http.addHeader("Content-Type", "image/jpeg");

  Serial.println("Uploading photo...");

  int responseCode = http.POST(frame->buf, frame->len);

  Serial.print("HTTP response: ");
  Serial.println(responseCode);

  if (responseCode > 0) {
    Serial.println(http.getString());
  } else {
    Serial.print("HTTP error: ");
    Serial.println(http.errorToString(responseCode));
  }

  http.end();
}

void setupCamera() {
  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Low-memory settings for reliable capture
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  esp_err_t cameraStatus = esp_camera_init(&config);

  if (cameraStatus != ESP_OK) {
    Serial.printf(
        "Camera initialization failed with error 0x%x\n",
        cameraStatus
    );

    while (true) {
      delay(1000);
    }
  }

  Serial.println("Camera initialized");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(PIR_GPIO_NUM, INPUT);

  setupCamera();
  connectToWiFi();

  Serial.println("Bird camera ready");
}

void loop() {
  if (digitalRead(PIR_GPIO_NUM) == HIGH) {
    Serial.println("Motion detected");

    camera_fb_t* frame = esp_camera_fb_get();

    if (frame == nullptr) {
      Serial.println("Camera capture failed");
    } else {
      Serial.printf("Captured photo: %u bytes\n", frame->len);

      uploadPhoto(frame);

      esp_camera_fb_return(frame);
    }

    // Prevent repeated uploads during the same motion event
    while (digitalRead(PIR_GPIO_NUM) == HIGH) {
      delay(100);
    }

    delay(1000);
  }

  delay(100);
}