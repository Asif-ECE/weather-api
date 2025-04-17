TEMP_SIGNIFICANT_DIFF = 3.0
AIR_SIGNIFICANT_DIFF = 10.0

def generate_weather_message(comparison) -> str:
    temp_diff = comparison["temp_diff"]
    air_diff = comparison["air_con_diff"]
    warmer = temp_diff>0
    less_pollution = air_diff<0

    # Determine temperature message
    if abs(temp_diff) < 1:
        temp_msg = "no significant temperature difference"
    elif not warmer:
        if abs(temp_diff) >= TEMP_SIGNIFICANT_DIFF:
            temp_msg = f"{round(abs(temp_diff), 2)}°C cooler"
        else:
            temp_msg = "a bit cooler"
    else:
        if abs(temp_diff) >= TEMP_SIGNIFICANT_DIFF:
            temp_msg = f"{round(abs(temp_diff), 2)}°C hotter"
        else:
            temp_msg = "a bit warmer"

    # Determine air quality message
    if abs(air_diff) < 5:
        air_msg = "similar air quality"
    elif less_pollution:
        if abs(air_diff) >= AIR_SIGNIFICANT_DIFF:
            air_msg = "significantly better air quality"
        else:
            air_msg = "slightly better air quality"
    else:
        if abs(air_diff) >= AIR_SIGNIFICANT_DIFF:
            air_msg = "worse"
        else:
            air_msg = "slightly worse"

    # Build final message
    if "cooler" in temp_msg and "better" in air_msg:
        return f"Your destination is {temp_msg} and has {air_msg}. Enjoy your trip!"
    elif "hotter" in temp_msg and "worse" in air_msg:
        return f"Your destination is {temp_msg} and has {air_msg} than your current location. It’s better to stay where you are."
    elif "cooler" in temp_msg and "worse" in air_msg:
        return f"Your destination is {temp_msg} but has {air_msg}. Pack accordingly!"
    elif "hotter" in temp_msg and "better" in air_msg:
        return f"Your destination is {temp_msg}, but air quality is {air_msg}. Stay hydrated and enjoy!"
    elif "no significant" in temp_msg and "better" in air_msg:
        return f"Temperature is about the same, but you’ll enjoy {air_msg}."
    elif "no significant" in temp_msg and "worse" in air_msg:
        return f"Temperature is similar, but the air quality is {air_msg}."
    else:
        return f"Your destination is {temp_msg} and has {air_msg}."

