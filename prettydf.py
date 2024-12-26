import pandas as pd
from pprint import pprint
from pymodbus.client.serial import ModbusSerialClient
from hexss import json_load, json_update


def df_transform(df, column_mapping):
    pretty_df = pd.DataFrame()

    for key, cols in column_mapping.items():
        pretty_df[key] = df.iloc[:, [col for col in cols]].apply(
            lambda row: sum(row.iloc[i] * (65536 ** (len(cols) - i - 1)) for i in range(len(cols))),
            axis=1
        )
    return pretty_df


def df_reverse(pretty_df, column_mapping):
    original_df = pd.DataFrame()

    for key, cols in column_mapping.items():
        num_cols = len(cols)
        for col_index, col in enumerate(cols):
            original_df[col] = pretty_df[key].apply(
                lambda x: (x // (65536 ** (num_cols - col_index - 1))) % 65536
            )

    original_df = original_df.reindex(sorted(original_df.columns), axis=1)
    return original_df


column_mapping = {
    "Target | (0,1)": [0, 1],
    "Speed | (4,5)": [4, 5],
    "Acceleration | (10)": [10],
    "Deceleration | (11)": [11],
    "Zone Boundary (+) | (6,7)": [6, 7],
    "Zone Boundary (-) | (8,9)": [8, 9],
    "(2)": [2],
    "(3)": [3],
    "(12)": [12],
    "(13)": [13],
    "(14)": [14],
    "(15)": [15],
}


def read_():
    client = ModbusSerialClient(port="COM13", baudrate=38400, timeout=2)
    all_positions = []
    for i in range(64):
        start_address = 4096
        num_registers = 16
        slave_id = 2
        response = client.read_input_registers(
            address=start_address + i * 16,
            count=num_registers,
            slave=slave_id
        )
        if not response.isError():
            position_data = response.registers
            data_dict = {}
            for j in range(num_registers):
                data_dict[f"{j}"] = position_data[j]
            all_positions.append(data_dict)
    client.close()
    df = pd.DataFrame(all_positions)
    return df


def write_(i, values: list):
    client = ModbusSerialClient(port="COM13", baudrate=38400, timeout=2)
    start_address = 4096
    slave_id = 2
    response = client.write_registers(
        address=start_address + i * 16,
        values=values,
        slave=slave_id
    )
    if not response.isError():
        ...

    client.close()


old_df = None


def read_p_df():
    global old_df
    df = read_()
    old_df = df.copy()
    p_df = df_transform(df, column_mapping)
    data = {
        'data': p_df.values.tolist(),
        'rowHeaders': [f"{i}" for i in range(len(p_df.values.tolist()))],
        'colHeaders': p_df.columns.tolist(),
        'columns': [{'type': 'numeric'} for _ in range(len(p_df.columns.tolist()))],
        'manualColumnResize': True,
        'manualRowResize': True,
        'contextMenu': True,
        'licenseKey': 'non-commercial-and-evaluation',
        'stretchH': 'all',
        'height': 'auto',
        'width': '100%'
    }
    pprint(p_df)
    return data


def write_p_df(p_df):
    global old_df

    df = df_reverse(p_df, column_mapping)
    if old_df is not None:
        for i in range(len(old_df)):
            if old_df.iloc[i].values.tolist() != df.iloc[i].values.tolist():
                print(f'{i}-->{df.iloc[i].values.tolist()}')
                write_(i, df.iloc[i].values.tolist())

        old_df = df.copy()
