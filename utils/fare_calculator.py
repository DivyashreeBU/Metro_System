def calculate_fare(from_zone, to_zone):
    zone_diff = abs(int(from_zone) - int(to_zone))
    base_fare = 10
    return base_fare + zone_diff * 5