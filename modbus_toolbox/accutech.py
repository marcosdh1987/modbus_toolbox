import struct

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


# def read_values(ip_address, d_port, amount=30):
#     data = []
#     for i in range(1, amount + 1):
#         modbus_register_address = 5 + (i * 10)
#         data.append(read_specific_register(ip_address, d_port, modbus_register_address))
#     return data


def read_values(ip_address, d_port, amount=30):
    data = []
    for rfid in range(1, amount + 1):
        data.append(read_register_for_rfid(ip_address, d_port, rfid))
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


def write_register_for_rfid(ip_address, port, rfid, value):
    # Calcular la dirección base del registro para el RFID especificado
    modbus_register_address = 40005 + (rfid - 1) * 10

    # Crear un cliente Modbus TCP
    client = ModbusClient(host=ip_address, port=port, auto_open=True, auto_close=True)

    # Conectar al dispositivo
    if client.open():
        # Escribir un registro de punto flotante (32 bits IEEE) con Modbus FC16
        valor_bytes = struct.pack(">f", value)  # Convertir el valor a bytes
        regs_to_write = struct.unpack(
            ">HH", valor_bytes
        )  # Convertir los bytes a registros
        result = client.write_multiple_registers(modbus_register_address, regs_to_write)
        if result:
            print(f"Valor {value} escrito para RFID {rfid}")
        else:
            print(f"Error al escribir registros para RFID {rfid}")

        # Cerrar la conexión
        client.close()
    else:
        print("Error al conectar al dispositivo")


def read_register_for_rfid(ip_address, port, rfid):
    # Calcular la dirección base del registro para el RFID especificado
    modbus_register_address = 40005 + (rfid - 1) * 10

    # Crear un cliente Modbus TCP
    client = ModbusClient(host=ip_address, port=port, auto_open=True, auto_close=True)

    # Conectar al dispositivo
    if client.open():
        # Leer los registros de punto flotante (32 bits IEEE) con Modbus FC3
        regs_l = client.read_holding_registers(modbus_register_address, 2)
        if regs_l:
            valor_bytes = struct.pack(
                ">HH", regs_l[0], regs_l[1]
            )  # Concatenar los registros y convertir a bytes
            valor = struct.unpack(">f", valor_bytes)[
                0
            ]  # Decodificar los bytes como un valor float
            # print(f"Valor leído para RFID {rfid}: {valor}")
            return valor
        else:
            # print(f"Error al leer registros para RFID {rfid}")
            return None

        # Cerrar la conexión
        client.close()
    else:
        print("Error al conectar al dispositivo")
        return None
