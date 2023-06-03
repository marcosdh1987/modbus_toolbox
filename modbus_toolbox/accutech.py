from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pyModbusTCP.client import ModbusClient


def test_connection(ip_address, d_port):
    client = ModbusTcpClient(
        host=ip_address, port=d_port, auto_open=True, auto_close=True
    )
    if client.connect():
        client.close()
        return True
    else:
        client.close()
        return False


def read_specific_register(ip_address, d_port, register):
    client = ModbusClient(host=ip_address, port=d_port, auto_open=True, auto_close=True)
    regs_l = client.read_holding_registers(register, 2)
    # convert the two registers into a a number, the source is in two register bases on float 32 bit ieee Floating Point
    dec = BinaryPayloadDecoder.fromRegisters(
        regs_l, byteorder=Endian.Little, wordorder=Endian.Big
    )
    # get float value
    value = dec.decode_32bit_float()
    return value


def read_values(ip_address, d_port, amount=30):
    data = []
    for i in range(1, amount + 1):
        modbus_register_address = 5 + (i * 10)
        data.append(read_specific_register(ip_address, d_port, modbus_register_address))
    return data


def write_specific_register(ip_address, d_port, register, value):
    client = ModbusTcpClient(
        host=ip_address, port=d_port, auto_open=True, auto_close=True
    )
    builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
    # create random float value
    builder.add_32bit_float(value)
    payload = builder.build()
    client.write_registers(register - 2, payload, skip_encode=True)
    client.close()
