def calculate_water_norm(weight, activity_minutes, temperature):
    water = weight * 30

    water += (activity_minutes // 30) * 500

    if temperature and temperature > 25:
        water += 750

    return water


def calculate_calorie_norm(weight, height, age, activity_minutes):
    base = 10 * weight + 6.25 * height - 5 * age

    if activity_minutes < 30:
        activity_bonus = 200
    elif activity_minutes < 60:
        activity_bonus = 300
    else:
        activity_bonus = 400

    return int(base + activity_bonus)


def calories_from_workout(workout_type, minutes):
    burn_rates = {
        "бег": 10,
        "ходьба": 4,
        "велосипед": 8,
        "плавание": 9
    }
    
    return burn_rates.get(workout_type.lower(), 5) * minutes