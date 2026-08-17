import serial
import time

arduino = serial.Serial("COM7", 9600)

# Arduino Uno resets when serial connection opens,
# so give it time to start back up
time.sleep(2)

while True:
    sensor = input("\nChoose sensor (temp/light/q): ").lower()

    if (sensor == 'q'):
        arduino.write("QUIT\n".encode())
        response = arduino.readline().decode().strip()
        print("Arduino:", response)
        break

    if (sensor == "temp"):
        value = input("Enter Temperature: ")
        message = f"TEMP:{value}\n"

    elif (sensor == "light"):
        value = input("Enter light level: ")
        message = f"LIGHT:{value}\n"

    else:
        print("Invalid Sensor")
        continue
    

    

    arduino.write(message.encode())

    

    # Wait for Arduino's response
    response = arduino.readline().decode().strip()

    print("Arduino:", response)

arduino.close()
