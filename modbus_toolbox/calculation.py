def make_calcs(data, coeff):
    """Calculate the differential value of the data

    Args:
        data (list): List of data from modbus rtu address
        coeff (list): List of coefficients from db
    Returns:
        list: List of calculated values
    """
    Qstd = gas_calc(
        data[1], data[2], data[3], coeff[2], coeff[3], coeff[4], coeff[5], coeff[6],
    )
    vcf = vcf_calc(data[10], coeff[3])
    Ostd = mtf_calc(data[7], coeff[6]) * vcf
    Wstd = mtf_calc(data[13], coeff[7])
    dp01 = dp_calc(data[21], data[23])
    dp02 = dp_calc(data[26], data[28])
    dp03 = dp_calc(data[31], data[33])
    data = [1, Qstd, Ostd, Wstd, dp01, dp02, dp03, 0, 0, 0]
    return data


def gas_calc(P: float, Tf: float, Qf: float, atm: float, Pb: float, Tb: float, Zf: float, Zb: float):
    """Convert raw data to gas flow rate

    Args:
        P (float): Pressure of gas flow rate (psig) (r40017)
        Tf (float): Temperature of gas flow rate (F) (r40019)
        Qf (float): Raw gas flow rate (m3/s) (r40021)
        atm (float): Atmospheric pressure (psia) (query from db)
        Pb (float): Base pressure (psia) (query from db)
        Tb (float): Base temperature (F) (query from db)
        Zf (float): Compressibility at flowing conditions (query from db)
        Zb (float): Compressibility at base conditions (query from db)
        data (list): List of data
        coeff (list): List of coefficients

    Aux:
        Pf (float): Pressure of gas flow rate (psia) = P + Atm press (14.7 psia)

    Returns:
        value: value of gas flow rate at standard conditions (m3/d)
    """
    # calculate the gas m3/s to m3/d
    Qf = Qf * 86400
    Pf = P + atm
    # convert gas flow rate to standard conditions
    return Qf * (Pf / Pb) * ((460 + Tf) / (460 + Tb)) * (Zf / Zb)


def mtf_calc(flow, factor):
    """Convert raw flow rate to standard conditions

    Args:
        flow (float): flow rate (m3/d)
        factor (float): MTF factor (query from db)
    Returns:
        value: value of mtf
    """
    return flow * factor


def dp_calc(p1, p2):
    """Calculate differential pressure

    Args:
        p1 (float): pressure 1 (psig)
        p2 (float): pressure 2 (psig)
    Returns:
        value: value of differential pressure
    """
    return p1 - p2


def error_series(sensor_value, setpoint, e_buffer):
    """Function to calculate the error series from the sensor value and the setpoint."""
    # calculate the error
    error = sensor_value - setpoint
    # append the error to the buffer
    e_buffer.append(error)
    if len(e_buffer) > 3:
        # remove the first element
        e_buffer.pop(0)
    # return the buffer
    return e_buffer


def pid_control_calc(e_series, kp, ki, kd):
    "Function to calculate the PID control signal from a series of 3 values."
    # calculate the proportional error
    e_p = e_series[2]
    # calculate the integral error
    e_i = (e_series[2] + e_series[1] + e_series[0]) / 3
    # calculate the derivative error
    e_d = (e_series[2] - e_series[1] - e_series[0]) / 3
    return kp * e_p + ki * e_i + kd * e_d


def ai_control_calc(e_series, kp, ki, kd):
    "Function to calculate the PID control signal from a series of 3 values."
    u = 15
    return u


def vcf_calc(temp, base_temp: float = 15.5):
    """Calculate the volume correction factor (VCF) from the temperature."""
    # calculate the volume correction factor
    vcf = 1 + (0.000028 * (temp - base_temp))
    return vcf
