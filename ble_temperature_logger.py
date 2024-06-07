import asyncio
from bleak import BleakClient, BleakError
import matplotlib.pyplot as plt
import datetime
import time
import os

# ESP32-CAM 的 BLE 服務和特性 UUID
SERVICE_UUID = "12345678-1234-1234-1234-123456789012"
CHARACTERISTIC_UUID = "87654321-4321-4321-4321-210987654321"
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"  # 替換成你的ESP32-CAM的MAC地址

# 初始化資料結構
timestamps = []
temperatures = []

# 畫圖函數
def plot_data():
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, temperatures, marker='o')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature over Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('temperature_plot.png')
    plt.show()

# 保存log函數，將新數據追加到CSV文件中
def save_log(timestamp, temperature):
    file_exists = os.path.isfile('temperature_log.csv')
    
    with open('temperature_log.csv', 'a') as f:
        if not file_exists:
            f.write('Timestamp,Temperature\n')
        f.write(f'{timestamp},{temperature}\n')

# BLE通知回調函數
def notification_handler(sender, data):
    global timestamps, temperatures
    temperature = float(data.decode('utf-8'))
    timestamp = datetime.datetime.now()
    
    print(f"Received temperature: {temperature}°C at {timestamp}")
    
    timestamps.append(timestamp)
    temperatures.append(temperature)
    
    # 保存新數據到log
    save_log(timestamp, temperature)
    # 更新圖表
    plot_data()

# 嘗試連接函數
async def connect_and_notify():
    while True:
        try:
            async with BleakClient(DEVICE_ADDRESS) as client:
                print(f"Connected: {client.is_connected}")
                
                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
                
                try:
                    while True:
                        await asyncio.sleep(2)  # 每2秒檢查一次
                except KeyboardInterrupt:
                    await client.stop_notify(CHARACTERISTIC_UUID)
                    print("Stopped notification")
                    break
        except BleakError as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # 等待5秒後重新嘗試連接

if __name__ == "__main__":
    asyncio.run(connect_and_notify())
