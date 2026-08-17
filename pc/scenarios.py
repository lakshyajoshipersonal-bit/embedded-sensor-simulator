def get_scenario_targets(active_scenario, scenario_time):

    if active_scenario == "Normal Operation":
        if scenario_time < 5:
            return 25, 700, 50
        elif scenario_time < 10:
            return 26, 650, 52
        elif scenario_time < 15:
            return 24, 600, 48
        else:
            return 25, 700, 50

    elif active_scenario == "Overheating":
        if scenario_time < 5:
            return 25, 700, 50
        elif scenario_time < 10:
            return 29, 700, 47
        elif scenario_time < 15:
            return 32, 700, 43
        else:
            return 38, 700, 38

    elif active_scenario == "Dark":
        if scenario_time < 5:
            return 22, 700, 50
        elif scenario_time < 10:
            return 22, 500, 53
        elif scenario_time < 15:
            return 22, 300, 55
        else:
            return 22, 100, 60

    elif active_scenario == "Overheat + Dark":
        if scenario_time < 5:
            return 25, 700, 50
        elif scenario_time < 10:
            return 29, 500, 50
        elif scenario_time < 15:
            return 32, 300, 48
        else:
            return 38, 100, 45

    return None