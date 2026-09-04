from simulator import update_sensor_values

def test_temperature_update_increase():
    temperature = 22.0
    light = 700
    humidity = 50.0

    target_temperature = 30.0
    target_light = 700
    target_humidity = 50.0

    new_temp, new_light, new_humid = update_sensor_values(temperature, light, humidity,
                                                          target_temperature, target_light, target_humidity)

    assert new_temp > temperature

def test_temperature_update_decrease():
    temperature = 30.0
    light = 700
    humidity = 50.0

    target_temperature = 22.0
    target_light = 700
    target_humidity = 50.0

    new_temp, new_light, new_humid = update_sensor_values(temperature, light, humidity,
                                                          target_temperature, target_light, target_humidity)

    assert new_temp < temperature

def test_temperature_stays_within_limits():
    temperature = 44.0
    light = 700
    humidity = 50.0
    
    target_temperature = 100.0
    target_light = 700
    target_humidity = 50.0

    new_temp, new_light, new_humid = update_sensor_values(temperature, light, humidity,
                                                              target_temperature, target_light, target_humidity)

    assert 15 <= new_temp <= 45

    temperature = 16.0
    target_temperature = 2.0

    new_temp, new_light, new_humid = update_sensor_values(temperature, light, humidity,
                                                                  target_temperature, target_light, target_humidity)

    assert 15 <= new_temp <= 45

