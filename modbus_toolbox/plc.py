import struct

from pyModbusTCP.client import ModbusClient


def read_plc_register_raw(ip_address, d_port, start_reg, length=36):
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


def regs2float(regs):
    return struct.unpack("<f", struct.pack("<HH", *regs))[0]


def read_plc_register(ip_address, d_port, start_reg, length=72):
    client = ModbusClient(
        host=ip_address, port=d_port, auto_open=True, auto_close=True, timeout=1
    )
    regs_l = client.read_holding_registers(start_reg, length)
    # iterate through the registers and convert the data to a float value
    data = []
    for i in range(0, length, 2):
        data.append(regs2float(regs_l[i : i + 2]))
    return data
