import serial
import time
import random

arduino = serial.Serial("COM7", 9600)
time.sleep(2)

temperature = 22
light = 700

try:
    while True:
        temperature += random.uniform(-0.5,0.5)
        light += random.randint(-40,40)

        #reasonable range
        temperature = max(15,min(45,temperature))
        light = max(0, min(1000, light))

        temp_message = f"TEMP:{temperature:.1f}\n"
        arduino.write(temp_message.encode())

        temp_response = arduino.readline().decode().strip()

        print(f"Temperature: {temperature:.1f} C")
        print("Arduino:", temp_response)

        light_message = f"LIGHT:{light}\n"
        arduino.write(light_message.encode())

        light_response = arduino.readline().decode().strip()

        print(f"Light: {light}")
        print("Arduino:", light_response)

        print("-----------------------")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping simulation...")

    arduino.write("QUIT\n".encode())
    response = arduino.readline().decode().strip()

    print("Arduino:", response)

finally:
    arduino.close()



