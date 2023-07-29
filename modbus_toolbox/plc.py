import struct
import time

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from pyModbusTCP.client import ModbusClient


def read_plc_register_raw(ip_address, d_port, start_reg, length=36):
    client = ModbusClient(host=ip_address, port=d_port, auto_open=True, auto_close=True)
    regs_l = client.read_holding_registers(start_reg, length)
    return regs_l


def write_single_float(ip_address, d_port, register, value):
    # Crear un cliente Modbus TCP
    client = ModbusClient(host=ip_address, port=d_port, auto_open=True, auto_close=True)

    # Conectar al dispositivo
    if client.open():
        # Crear un objeto BinaryPayloadBuilder para empaquetar el valor de punto flotante en registros Modbus
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
        builder.add_32bit_float(value)

        # Obtener los registros resultantes como una lista de enteros
        regs_to_write = builder.to_registers()

        # Escribir los registros en el dispositivo Modbus
        result = client.write_multiple_registers(register, regs_to_write)
        if result:
            print(
                f"Valor {value} escrito en el PLC, registros {register} y {register + 1}"
            )
        else:
            print(
                f"Error al escribir el valor {value} en el PLC, registros {register} y {register + 1}"
            )

        # Cerrar la conexión
        client.close()
    else:
        print("Error al conectar al dispositivo")


def write_plc_register(ip_address, d_port, start_reg, values):
    # Crear un cliente Modbus TCP
    client = ModbusClient(host=ip_address, port=d_port, auto_open=True, auto_close=True)

    # Conectar al dispositivo
    if client.open():
        # Crear un objeto BinaryPayloadBuilder para empaquetar los valores de punto flotante en registros Modbus
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)

        # Agregar los valores de punto flotante al builder
        for value in values:
            builder.add_32bit_float(value)

        # Obtener los registros resultantes como una lista de enteros
        regs_to_write = builder.to_registers()

        # Escribir los registros en el dispositivo Modbus
        result = client.write_multiple_registers(start_reg, regs_to_write)
        if result:
            print("Valores escritos en el PLC:", values)
        else:
            print("Error al escribir valores en el PLC")

        # Cerrar la conexión
        client.close()
    else:
        print("Error al conectar al dispositivo")


def decimal_decode(regs_l):
    number = float(regs_l[0]) + float("0." + str(regs_l[1]))
    return number


def regs2float(regs):
    return struct.unpack("<f", struct.pack("<HH", *regs))[0]


def read_plc_register_fast(ip_address, d_port, start_reg, length=72):
    client = ModbusClient(
        host=ip_address, port=d_port, auto_open=True, auto_close=True, timeout=1
    )
    regs_l = client.read_holding_registers(start_reg, length)
    # iterate through the registers and convert the data to a float value
    data = []
    for i in range(0, length, 2):
        data.append(regs2float(regs_l[i : i + 2]))
    return data


def read_plc_register(ip_address, d_port, start_reg, length=72, max_attempts=3):
    data = []
    attempts = 0
    while attempts < max_attempts:
        try:
            client = ModbusClient(
                host=ip_address, port=d_port, auto_open=True, auto_close=True, timeout=1
            )
            regs_l = client.read_holding_registers(start_reg, length)
            # iterate through the registers and convert the data to a float value
            for i in range(0, length, 2):
                data.append(regs2float(regs_l[i : i + 2]))
            break  # Si la lectura es exitosa, salimos del bucle while
        except Exception as e:
            print(f"Intento {attempts + 1} de lectura fallido: {e}")
            attempts += 1
            time.sleep(1)  # Esperar 1 segundo antes de intentar nuevamente
    if attempts == max_attempts:
        print(
            f"No se pudo leer los registros del PLC después de {max_attempts} intentos."
        )
        return None  # Puedes manejar el valor None como desees en tu aplicación
    return data
