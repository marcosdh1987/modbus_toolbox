from pyModbusTCP.client import ModbusClient


def read_plc_register(ip_address, d_port, start_reg, length=36):
    client = ModbusClient(host=ip_address, port=d_port, auto_open=True, auto_close=True)
    regs_l = client.read_holding_registers(start_reg, length)
    return regs_l


def write_plc_register(ip_address, d_port, register, value):
    client = ModbusClient(host=ip_address, port=d_port, auto_open=True, auto_close=True)
    regs_l = client.write_single_register(register, value)
    return regs_l


def decimal_decode(regs_l):
    number = float(regs_l[0]) + float("0." + str(regs_l[1]))
    return number
