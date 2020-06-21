import math

safe_humidity = 60
max_humidity = 38


def main():
    external_temp_f = 27.70
    external_humidity = 47.00
    internal_temp_f = 64.60
    internal_humidity = 33.00
    internal_dewpoint = 34.80

    external_temp_c = (external_temp_f - 32) * 5.0 / 9.0
    print("external temp 1: " + str(external_temp_c))

    internal_temp_c = (internal_temp_f - 32) * 5.0 / 9.0
    print("internal temp 2: " + str(internal_temp_c))

    method1 = calc_target_humidity(external_temp_c, external_humidity, internal_temp_c, internal_humidity)
    print("method1: " + str(method1))

    method2 = determine_target_humidity(internal_temp_c, internal_dewpoint, external_temp_c)
    print("method2: " + str(method2))


def calculate_depoint(temp, humidity):
    c = temp
    rh = humidity
    if c >= 0:
        a = 7.5
    else:
        a = 7.6

    if c >= 0:
        b = 237.3
    else:
        b = 240.7
    ssp = 6.1078 * pow(10, (a * c) / (b + c))
    sp = rh / 100 * ssp
    v = math.log(sp / 6.1078, 10)
    dew = round(b * v / (a - v), 1)
    # print("dew point: " + str(dew))
    return dew


def calculate_humidity(temp, dew_point):
    c = temp
    dp = dew_point
    if c >= 0:
        a = 7.5
    else:
        a = 7.6

    if c >= 0:
        b = 237.3
    else:
        b = 240.7

    tssp = 6.1078 * pow(10, (a * c) / (b + c))

    if dew_point >= 0:
        a = 7.5
    else:
        a = 7.6

    if dew_point >= 0:
        b = 237.3
    else:
        b = 240.7

    dssp = 6.1078 * pow(10, (a * dp) / (b + dp))

    rh = round(100 * dssp / tssp, 1)

    # print("calculated humidity: " + str(rh))

    return rh


def determine_target_humidity(inside_temp, inside_dew, outside_temp):
    inc = 5.0
    max_dew = 46.00
    min_humid = 10.00
    max_humid = 38.00
    max_dp_delta = -10.00

    if inside_dew >= max_dew:
        return max_humid

    target_humidity = calculate_humidity(inside_temp, (max_dew - 32) * 5.0 / 9.0)
    print("target1: " + str(target_humidity))
    target_humidity = math.floor(target_humidity / inc) * inc
    print("target2: " + str(target_humidity))

    dp = calculate_depoint(inside_temp, target_humidity)
    print("int dew point: " + str(dp))
    while dp - outside_temp > max_dp_delta and target_humidity > min_humid:
        target_humidity -= inc
        print("target: " + str(target_humidity))
        dp = calculate_depoint(inside_temp, target_humidity)

    # target_humidity = min(target_humidity, max_humid)
    # target_humidity = max(target_humidity, min_humid)
    print("target humidity" + str(target_humidity))
    return target_humidity


def calc_target_humidity(external_temp_c, external_humidity, internal_temp_c, internal_humidity):
    """Converts the optimal indoor humidity.  Drop target humidity 5% for every 5degree C drop below 0"""

    if external_temp_c >= 0:
        return max_humidity
    else:
        target = max(0, max_humidity + external_temp_c)
        if external_temp_c <= -15:
            target = target + 2.5
        if external_temp_c <= -20:
            target = target + 2.5
        if external_temp_c <= -25:
            target = target + 2.5
        if external_temp_c <= -30:
            target = target + 2.5
        return target


if __name__ == "__main__":
    main()
