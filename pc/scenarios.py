def get_scenario_targets(active_scenario, scenario_time, temp_threshold, light_threshold):

    if active_scenario == "Normal Operation":
        if scenario_time < 5:
            return temp_threshold - 5, light_threshold + 400, 50
        elif scenario_time < 10:
            return temp_threshold - 4, light_threshold + 350, 52
        elif scenario_time < 15:
            return temp_threshold - 6, light_threshold + 300, 48
        else:
            return temp_threshold - 5, light_threshold + 400, 50

    elif active_scenario == "Overheating":
        if scenario_time < 5:
            return temp_threshold - 5, light_threshold + 400, 50
        elif scenario_time < 10:
            return temp_threshold - 1, light_threshold + 400, 47
        elif scenario_time < 15:
            return temp_threshold + 2, light_threshold + 400, 43
        else:
            return temp_threshold + 8, light_threshold + 400, 38

    elif active_scenario == "Dark":
        if scenario_time < 5:
            return temp_threshold - 5, light_threshold + 400, 50
        elif scenario_time < 10:
            return temp_threshold - 5, light_threshold + 300, 53
        elif scenario_time < 15:
            return temp_threshold - 5, light_threshold, 55
        else:
            return temp_threshold - 5, light_threshold - 200, 60

    elif active_scenario == "Overheat + Dark":
        if scenario_time < 5:
            return temp_threshold - 5, light_threshold + 400, 50
        elif scenario_time < 10:
            return temp_threshold - 1, light_threshold + 200, 50
        elif scenario_time < 15:
            return temp_threshold + 2, light_threshold, 48
        else:
            return temp_threshold + 8, light_threshold - 200, 45

    return None