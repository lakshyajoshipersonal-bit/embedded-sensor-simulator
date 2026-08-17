import random

def update_sensor_values(temperature,light,humidity,target_temperature,target_light,target_humidity):
    temperature += (target_temperature - temperature) * 0.1
    temperature += random.uniform(-0.1,0.1)

    light += int((target_light - light) * 0.1) 
    light += random.randint(-10,10)

    humidity += (target_humidity - humidity) * 0.1
    humidity += random.uniform(-0.5,0.5)

    temperature = max(15,min(45,temperature))
    light = max(0, min(1000, light))
    humidity = max(0,min(100,humidity))

    return temperature, light, humidity

    