import struct
import time

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pyModbusTCP.client import ModbusClient

from modbus_toolbox.logger import Logger

logger = Logger(name="Modbus-Toolbox-Accutech")._set_logger()

def test_connection(ip_address, d_port, max_attempts=2):
    for attempt in range(1, max_attempts + 1):
        client = ModbusTcpClient(
            host=ip_address, port=d_port, auto_open=True, auto_close=True
        )
        if client.connect():
            client.close()
            logger.info(f"Conexión exitosa en el intento {attempt}")
            return True
        else:
            client.close()
            logger.info(f"Intento {attempt} de conexión fallido")
            if attempt < max_attempts:
                logger.info("Reintentando...")
    logger.info("No se pudo establecer la conexión después de varios intentos")
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


def read_values_fast(ip_address, d_port, amount=30):
    data = []
    for i in range(1, amount + 1):
        modbus_register_address = 5 + (i * 10)
        data.append(read_specific_register(ip_address, d_port, modbus_register_address))
    return data


def read_values_by_rfid(ip_address, d_port, amount=30):
    data = []
    for rfid in range(1, amount + 1):
        data.append(read_register_for_rfid(ip_address, d_port, rfid))
    return data


def read_values(ip_address, d_port, amount=30, max_attempts=3):
    data = []
    for i in range(1, amount + 1):
        modbus_register_address = 5 + (i * 10)
        value = None
        attempts = 0
        while attempts < max_attempts:
            try:
                value = read_specific_register(
                    ip_address, d_port, modbus_register_address
                )
                break  # Si la lectura es exitosa, salimos del bucle while
            except Exception as e:
                logger.info(f"Intento {attempts + 1} de lectura fallido: {e}")
                attempts += 1
                time.sleep(1)  # Esperar 1 segundo antes de intentar nuevamente
        if value is not None:
            data.append(value)
        else:
            logger.info(
                f"No se pudo leer el valor del registro {modbus_register_address} después de {max_attempts} intentos."
            )
            data.append(
                None
            )  # Puedes manejar el valor None como desees en tu aplicación
    return data

def read_v2(ip_address, d_port, amount=30):
    data = []
    #try to read the initial modbus register if it fails, add 0 to all data values and return
    try:
        initial_value = read_specific_register(15)
        logger.info(f"Valor inicial: {initial_value}")
        for i in range(1, amount + 1):
            modbus_register_address = 5 + (i * 10)
            value = read_specific_register(modbus_register_address)
            if value is not None:
                data.append(value)
            else:
                logger.info(f"No se pudo leer el valor del registro numero: {modbus_register_address}")
                data.append(None)
        return data
    except:
        logger.info(f"No se pudo leer el valor del registro inicial, se retornan 0 en todos los valores.")
        for i in range(0, amount):
            data.append(0)
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
    # modbus_register_address = 40005 + (rfid - 1) * 10
    modbus_register_address = 5 + (rfid * 10)

    # Crear un cliente Modbus TCP
    client = ModbusClient(host=ip_address, port=port, auto_open=True, auto_close=True)
    # client = ModbusTcpClient(
    #     host=ip_address, port=port, auto_open=True, auto_close=True
    # )

    # Conectar al dispositivo
    if client.open():
        # if client:
        # Escribir un registro de punto flotante (32 bits IEEE) con Modbus FC16
        # Convertir el valor a bytes
        struct.pack(">f", value)

        # Crear un objeto BinaryPayloadBuilder y agregar los bytes del valor
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
        builder.add_32bit_float(value)

        # Obtener los registros resultantes como lista de enteros
        regs_to_write = builder.to_registers()

        # Escribir los registros en el dispositivo Modbus
        result = client.write_multiple_registers(modbus_register_address, regs_to_write)
        if result:
            logger.info(f"Valor {value} escrito para RFID {rfid}")
        else:
            logger.info(f"Error al escribir registros para RFID {rfid}")

        # Cerrar la conexión
        client.close()
    else:
        logger.info("Error al conectar al dispositivo")


def read_register_for_rfid(ip_address, port, rfid):
    # Calcular la dirección base del registro para el RFID especificado
    modbus_register_address = 5 + (rfid * 10)

    # Crear un cliente Modbus TCP
    client = ModbusClient(
        host=ip_address, port=port, auto_open=True, auto_close=True, timeout=1
    )

    # Conectar al dispositivo
    if client.open():
        # Leer los registros de punto flotante (32 bits IEEE) con Modbus FC3
        regs_l = client.read_holding_registers(modbus_register_address, 2)
        if regs_l:
            # valor_bytes = struct.pack('>HH', regs_l[0], regs_l[1])  # Concatenar los registros y convertir a bytes
            # valor = struct.unpack('>f', valor_bytes)[0]  # Decodificar los bytes como un valor float
            dec = BinaryPayloadDecoder.fromRegisters(
                regs_l, byteorder=Endian.Little, wordorder=Endian.Big
            )
            # get float value
            value = dec.decode_32bit_float()
            # logger.info(f"Valor leído para RFID {rfid}: {valor}")
            return value
        else:
            # logger.info(f"Error al leer registros para RFID {rfid}")
            return None

        # Cerrar la conexión
        client.close()
    else:
        logger.info("Error al conectar al dispositivo")
        return None
