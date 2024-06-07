#include <OneWire.h>
#include <DallasTemperature.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>
//for MAC addr
#include <WiFi.h>


#define ONE_WIRE_BUS 4  // DS18B20 數據線連接到 GPIO 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// BLE 服務和特性 UUID
#define SERVICE_UUID        "12345678-1234-1234-1234-123456789012"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-210987654321"

BLECharacteristic *pCharacteristic;

void setup() {
  Serial.begin(115200);
  
  // 初始化DS18B20
  sensors.begin();
  //for MAC addr
  Serial.print("\nDefault ESP32 MAC Address: ");
  Serial.println(WiFi.macAddress());
  // 初始化BLE
  BLEDevice::init("ESP32Temperature");
  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();
}

void loop() {
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);
  
  char tempString[8];
  dtostrf(temperatureC, 1, 2, tempString);
  pCharacteristic->setValue(tempString);
  pCharacteristic->notify();
  
  Serial.print("Temperature: ");
  Serial.print(tempString);
  Serial.println("°C");

  delay(2000); // 每兩秒讀取一次溫度
}
