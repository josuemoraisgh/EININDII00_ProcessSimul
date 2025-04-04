import sqlite3
import pandas as pd
from typing import Dict, Tuple, Union

# ['NAME', 'BYTE_SIZE', 'TYPE', 'MB_POINT', 'ADDRESS', 'CLP100']
# MB_POINT = di, co, hr, ir
mb_banco: Dict[str, Tuple[str, str, str, str]] = {
    'FV100CA': (4, 'FLOAT', 'hr', '01', '0032'),    
    'FI100CA': (4, 'FLOAT', 'ir', '01', '$[0.0227],[2.5 1.0],MODBUS.CLP100.FV100CA/100,0.0227,0'),
    'FV100AR': (4, 'FLOAT', 'hr', '03', '0032'),    
    'FI100AR': (4, 'FLOAT', 'ir', '05', '$[0.15],[1.25 1.0],MODBUS.CLP100.FV100AR/100,0.15,0'), 
    'qFornalha': (4, 'FLOAT', 'ir', '07', '$[0.85],[5.0 1.0],np.exp(-0.05*((MODBUS.CLP100.FI100AR/MODBUS.CLP100.FI100CA)-15)**2),810.0,0.0'),        
    'TI100'  : (4, 'FLOAT', 'ir', '09', '@MODBUS.CLP100.qFornalha/(1000 * MODBUS.CLP100.FI100AR)'),    
    'FI100V' : (4, 'FLOAT', 'hr', '05', '3EB33333'),
    'PI100V' : (4, 'FLOAT', 'ir', '11', '$[1.0],[1000 0.000001],MODBUS.CLP100.qFornalha - 2770 * MODBUS.CLP100.FI100V,100,0'),
    'LI100'  : (4, 'FLOAT', 'ir', '13', '$[1.0],[1.1 0.0000000001],MODBUS.CLP100.FI100A - MODBUS.CLP100.FI100V,100,0'),    
    'PI100A' : (4, 'FLOAT', 'hr', '07', '43C80000'),    
    'FV100A' : (4, 'FLOAT', 'hr', '09', '0032'),    
    'FI100A' : (4, 'FLOAT', 'ir', '15', '$[0.5],[1.0 1.0],math.sqrt(MODBUS.CLP100.PI100A/400)*MODBUS.CLP100.FV100A,100,0'),

}
# ['NAME', 'BYTE_SIZE', 'TYPE', 'FV100CA', 'FI100CA', 'FV100AR', 'FI100AR', 'TI100', 'FI100V', 'PI100V', 'LI100', 'PI100A', 'FV100A', 'FI100A']
hrt_banco: Dict[str, Tuple[Union[int, float], str, str]] = {
    'frame_type': (1, 'UNSIGNED', '06'),
    'address_type': (1, 'UNSIGNED', '00'),
    'error_code': (2, 'ENUM00', '0000'),
    'response_code': (1, 'ENUM27', '30'),
    'device_status': (1, 'BIT_ENUM02', '00'),
    'comm_status': (1, 'BIT_ENUM03', '00'),
    'master_address': (1, 'BIT_ENUM01', '80'),
    'manufacturer_id': (1, 'ENUM08', '3E'),
    'device_type': (1, 'ENUM01', '02'),
    'request_preambles': (1, 'UNSIGNED', '05'),
    'hart_revision': (1, 'UNSIGNED', '05'),
    'transmitter_revision': (1, 'UNSIGNED', '30'),
    'software_revision': (1, 'UNSIGNED', '04'),
    'hardware_revision': (1, 'UNSIGNED', '01'),
    'device_flags': (1, 'BIT_ENUM04', '00'),
    'device_id': (5, 'UNSIGNED', '1F00000010'),
    'polling_address': (1, 'UNSIGNED', '80'),
    'tag': (
        8,
        'PACKED_ASCII',
        '514CF0C60820',
    ),  # TT301
    'message': (
        32,
        'PACKED_ASCII',
        '34510910F4A010581414D405481515481820820820820820',
    ),  # MEDIDOR DE TEMPERATURA
    'descriptor': (
        16,
        'PACKED_ASCII',
        '505350152054552060820820'),  # TEMPERATURA
    'date': (3, 'DATE', '130879'),  # 19/08/2021
    'upper_range_value': (4, 'FLOAT', '44548000'),  # 850
    'lower_range_value': (4, 'FLOAT', 'C3480000'),  # -200
    'PROCESS_VARIABLE': (
        4,
        'FLOAT',
        '@(HART.LI100.percent_of_range / 100) * (HART.LI100.upper_range_value - HART.LI100.lower_range_value) + HART.LI100.lower_range_value'
    ),  # 50
    'percent_of_range': (4, 'FLOAT', '@MODBUS.CLP100.LI100'),
    'loop_current_mode': (1, 'ENUM00', '00'),
    'loop_current': (4, 'FLOAT', '@(HART.LI100.percent_of_range * 0.16) + 4'),
    'write_protect': (1, 'ENUM00', '00'),
    'private_label_distributor': (1, 'ENUM00', '00'),
    'final_assembly_number': (3, 'UNSIGNED', '00FBC6'),
    'physical_signaling_code': (1, 'ENUM10', '00'),  # (Bell 202 Current)
    'units_code': (1, 'ENUM02', '20'),  # (32 - Degrees Celsius)
    'transfer_function_code': (1, 'ENUM03', '00'),  # (0 - Linear)
    'alarm_selection_code': (1, 'ENUM06', 'FB'),  # (None)
    'material_code': (1, 'ENUM04', '02'),  # (Stainless Steel 316)
    'write_protect_code': (1, 'ENUM07', 'FB'),  # (None)
    'burst_mode_control_code': (1, 'ENUM09', 'FB'),  # (None)
    'flag_assignment': (1, 'ENUM11', '01'),  # (Multi-Sensor Field Device)
    'operating_mode_code': (1, 'ENUM14', '00'),  # (None)
    'analog_output_numbers_code': (1, 'ENUM15', '00'),  # (Analog Channel 0)
    'burst_command_number': (1, 'ENUM00', '00'),
    'burst_mode_select': (1, 'ENUM00', '00'),
    'meter_installation': (1, 'ENUM00', '00'),
    'digital_units': (1, 'ENUM00', '00'),
    'sensor_type': (1, 'ENUM00', '00'),
    'analog_output_transfer_function': (1, 'ENUM00', '00'),
    'ma_analog_output_1_value': (4, 'FLOAT', '00000000'),
    'ma_analog_output_1_alarm_select': (1, 'ENUM00', '00'),
    'sensor1_serial_number': (3, 'UNSIGNED', '000000'),
    'DEVICE_MODE': (1, 'ENUM00', '00'),
    'number_wires': (1, 'ENUM00', '00'),
    'device_code': (1, 'UNSIGNED', '00'),
    'lin_mode': (1, 'ENUM00', '00'),
    'SETPOINT': (4, 'FLOAT', '00000000'),
    'MANIPULATED_VARIABLE': (4, 'FLOAT', '00'),
    'CONTROLLER_TYPE': (1, 'ENUM00', '00'),
    'POWER_UP_MODE': (1, 'ENUM00', '00'),
    'CONTROLLER_ACTION': (1, 'ENUM00', '00'),
    'unit_code': (1, 'ENUM00', '00'),
    'SETPOINT_TRACKING_MODE': (1, 'ENUM00', '00'),
    'pid_mode': (1, 'ENUM00', '00'),
    'ERROR_PERCENT_RANGE': (4, 'FLOAT', '00'),
    'PROPORTIONAL_GAIN': (4, 'FLOAT', '00000000'),
    'INTEGRAL_TIME': (4, 'FLOAT', '00000000'),
    'DERIVATIVE_TIME': (4, 'FLOAT', '00000000'),
    'MV_HIGH_LIMIT': (4, 'FLOAT', '00000000'),
    'MV_LOW_LIMIT': (4, 'FLOAT', '00000000'),
    'MV_ROC_LIMIT': (4, 'FLOAT', '00000000'),
    'POWER_UP_SETPOINT_PERCENT_RANGE': (4, 'FLOAT', '00000000'),
    'POWER_UP_OUTPUT': (4, 'FLOAT', '00000000'),
    'set_point_time': (4, 'FLOAT', '00000000'),
    'set_point_generator_mode': (1, 'ENUM00', '00'),
    'set_point_time_generator_mode': (1, 'ENUM00', '00'),
    'range_units': (1, 'UNSIGNED', '00'),
    'pv_display_code': (1, 'ENUM00', '00'),
    'sv_display_code': (1, 'ENUM00', '00'),
    'communication_write_protection_mode': (1, 'ENUM00', '00'),
    'local_adjust_protection_mode': (1, 'ENUM00', '00'),
    'local_adjust_mode': (1, 'ENUM00', '00'),
    'input_unit_code': (1, 'ENUM00', '00'),
    'output_variable': (4, 'FLOAT', '00000000'),
    'mv_ohms': (4, 'FLOAT', '00000000'),
    'cal_point_limits_unit': (1, 'ENUM00', '00'),
    'upper_cal_point_value': (4, 'FLOAT', '00000000'),
    'lower_cal_point_value': (4, 'FLOAT', '00000000'),
    'CONTROLLER_MODE': (1, 'ENUM00', '00'),
    'fail_safe_mode': (1, 'ENUM00', '00'),
    'sensor_range': (1, 'ENUM00', '00'),
}


# Exemplo de uso
if __name__ == '__main__':
    # Colunas adicionais
    extra_columns = ['LI100', 'FI100V', 'FI100A', 'FV100A', 'PI100', 'TI100']

    # Converter o dicionário em DataFrame com colunas repetidas
    rows = []
    for key, val in hrt_banco.items():
        row = [key, val[0], val[1]] + [val[2]] * len(extra_columns)
        rows.append(row)

    columns = ['NAME', 'BYTE_SIZE', 'TYPE'] + extra_columns

    df = pd.DataFrame(rows, columns=columns)

    # Conectar (ou criar) o banco SQLite
    with sqlite3.connect('db/banco.db') as conn:
        # Salvar o DataFrame em SQLite (replace substitui se a tabela já existir)
        df.to_sql('hrt_tabela', conn, if_exists='replace', index=False)

    print('Dados salvos com sucesso na tabela hrt_settings.')