import time
from pymodbus.client.tcp import ModbusTcpClient

while True:
    try:
        print("\n\nConnecting to PLC...")
        client = ModbusTcpClient('192.168.3.254')

        if client.connect():
            print("Connected to PLC")
        else:
            print("Unable to connect to PLC")

        while True:
            response = client.read_holding_registers(address=0, count=10)
            if not response.isError():
                print("D0-D9 Data: ", response.registers)
                client.write_register(address=0, value=response.registers[0] + 1)

            response = client.read_coils(address=0, count=10)
            if not response.isError():
                print("Y0-Y9 Data  ", response.bits[:10])
                client.write_coil(address=0, value=not response.bits[0])

            response = client.read_coils(address=8192, count=10)
            if not response.isError():
                print("M0-M9 Data: ", response.bits[:10])

            response = client.read_discrete_inputs(address=0, count=10)
            if not response.isError():
                print("X0-X9 Data: ", response.bits[:10])

            print()
            time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)

client.close()

