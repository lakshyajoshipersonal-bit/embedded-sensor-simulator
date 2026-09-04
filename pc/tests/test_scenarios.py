from scenarios import get_scenario_targets

temp_threshold = 30.0
light_threshold = 300

def test_normal():
    
    temp, light, _ = get_scenario_targets("Normal Operation", 20, 
                                                        temp_threshold, light_threshold)

    assert temp < temp_threshold and light > light_threshold

#checking if the target temps are actually increasing over time.
def test_overheat():

    temp_early, _, _ = get_scenario_targets("Overheating", 4, 
                                            temp_threshold, light_threshold)
    
    temp_mid, _, _ = get_scenario_targets("Overheating", 9, 
                                           temp_threshold, light_threshold)
    
    temp_last, _, _ = get_scenario_targets("Overheating", 20, 
                                            temp_threshold, light_threshold)
        
    assert temp_early < temp_mid < temp_last

#checking if the target lights are actually decreasing over time.
def test_dark():

    _, light_early, _ = get_scenario_targets("Dark", 4, 
                                                temp_threshold, light_threshold)
        
    _, light_mid, _ = get_scenario_targets("Dark", 9, 
                                               temp_threshold, light_threshold)
        
    _, light_last, _ = get_scenario_targets("Dark", 20, 
                                                temp_threshold, light_threshold)
            
    assert light_early > light_mid > light_last

def test_overheatDark():
    temp, light, _ = get_scenario_targets("Overheat + Dark", 20, 
                                           temp_threshold, light_threshold)
    assert temp > temp_threshold and light < light_threshold

def test_overheating_stage_boundaries():
    temp_threshold = 30
    light_threshold = 300

    # Just before and exactly at 5 seconds
    temp_before_5, _, _ = get_scenario_targets(
        "Overheating", 4.9, temp_threshold, light_threshold
    )

    temp_at_5, _, _ = get_scenario_targets(
        "Overheating", 5.0, temp_threshold, light_threshold
    )

    assert temp_before_5 != temp_at_5

    # Just before and exactly at 10 seconds
    temp_before_10, _, _ = get_scenario_targets(
        "Overheating", 9.9, temp_threshold, light_threshold
    )

    temp_at_10, _, _ = get_scenario_targets(
        "Overheating", 10.0, temp_threshold, light_threshold
    )

    assert temp_before_10 != temp_at_10

    # Just before and exactly at 15 seconds
    temp_before_15, _, _ = get_scenario_targets(
        "Overheating", 14.9, temp_threshold, light_threshold
    )

    temp_at_15, _, _ = get_scenario_targets(
        "Overheating", 15.0, temp_threshold, light_threshold
    )

    assert temp_before_15 != temp_at_15


def test_dark_stage_boundaries():
    temp_threshold = 30
    light_threshold = 300

    # 5-second transition
    _, light_before_5, _ = get_scenario_targets(
        "Dark", 4.9, temp_threshold, light_threshold
    )

    _, light_at_5, _ = get_scenario_targets(
        "Dark", 5.0, temp_threshold, light_threshold
    )

    assert light_before_5 != light_at_5

    # 10-second transition
    _, light_before_10, _ = get_scenario_targets(
        "Dark", 9.9, temp_threshold, light_threshold
    )

    _, light_at_10, _ = get_scenario_targets(
        "Dark", 10.0, temp_threshold, light_threshold
    )

    assert light_before_10 != light_at_10

    # 15-second transition
    _, light_before_15, _ = get_scenario_targets(
        "Dark", 14.9, temp_threshold, light_threshold
    )

    _, light_at_15, _ = get_scenario_targets(
        "Dark", 15.0, temp_threshold, light_threshold
    )

    assert light_before_15 != light_at_15

