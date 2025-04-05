import sqlite3
import pandas as pd
from typing import Dict, Tuple, Union

# ['NAME', 'BYTE_SIZE', 'TYPE', 'MB_POINT', 'ADDRESS', 'CLP100']
# MB_POINT = di, co, hr, ir
mb_banco: Dict[str, Tuple[str, str, str, str]] = {
    'FV100CA': (4, 'FLOAT', 'hr', '01', '42480000'),    
    'FIT100CA': (4, 'FLOAT', 'ir', '01', '$[0.0227],[2.5 1.0],@MODBUS.CLP100.FV100CA/100.0,0.0227,0.0'),
    'FV100AR': (4, 'FLOAT', 'hr', '03', '42480000'),    
    'FIT100AR': (4, 'FLOAT', 'ir', '03', '$[0.15],[1.25 1.0],@MODBUS.CLP100.FV100AR/100.0,0.15,0.0'), 
    'qFor'   : (4, 'FLOAT', 'ir', '05', '$[0.85],[5.0 1.0],@exp(-0.05*((MODBUS.CLP100.FIT100AR/MODBUS.CLP100.FIT100CA)-15.0)**2.0),810.0,0.0'),        
    'TIT100'  : (4, 'FLOAT', 'ir', '07', '@MODBUS.CLP100.qFor/(1000.0 * MODBUS.CLP100.FIT100AR)'),    
    'FIT100V' : (4, 'FLOAT', 'hr', '05', '3EB33333'),
    'PIT100V' : (4, 'FLOAT', 'ir', '09', '$[1.0],[1000 0.000001],@MODBUS.CLP100.qFor - 2770.0 * MODBUS.CLP100.FIT100V,100.0,0.0'),
    'LIT100'  : (4, 'FLOAT', 'ir', '11', '$[1.0],[1.1 0.0000000001],@MODBUS.CLP100.FIT100A - MODBUS.CLP100.FIT100V,100.0,0.0'),    
    'PIT100A' : (4, 'FLOAT', 'hr', '07', '43C80000'),    
    'FV100A' : (4, 'FLOAT', 'hr', '09', '42480000'),    
    'FIT100A' : (4, 'FLOAT', 'ir', '13', '$[0.5],[1.0 1.0],@math.sqrt(MODBUS.CLP100.PIT100A/400.0)*MODBUS.CLP100.FV100A,100.0,0.0'),

}
# ['NAME', 'BYTE_SIZE', 'TYPE', 'FV100CA', 'FIT100CA', 'FV100AR', 'FIT100AR', 'TIT100', 'FIT100V', 'PIT100V', 'LIT100', 'PIT100A', 'FV100A', 'FIT100A']
hrt_banco: Dict[str, Tuple[Union[int, float], str, str]] = {
    'frame_type': (1, 'UNSIGNED', '06', '06', '06', '06', '06', '06', '06', '06', '06', '06', '06'),
    'address_type': (1, 'UNSIGNED', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'error_code': (2, 'ENUM00', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000'),
    'response_code': (1, 'ENUM27', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30'),
    'device_status': (1, 'BIT_ENUM02', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'comm_status': (1, 'BIT_ENUM03', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'master_address': (1, 'BIT_ENUM01', '80', '80', '80', '80', '80', '80', '80', '80', '80', '80', '80'),
    'manufacturer_id': (1, 'ENUM08', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E'),
    'device_type': (1, 'ENUM01', '02', '02', '02', '02', '02', '02', '02', '02', '02', '02', '02'),
    'request_preambles': (1, 'UNSIGNED', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05'),
    'hart_revision': (1, 'UNSIGNED', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05'),
    'transmitter_revision': (1, 'UNSIGNED', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30'),
    'software_revision': (1, 'UNSIGNED', '04', '04', '04', '04', '04', '04', '04', '04', '04', '04', '04'),
    'hardware_revision': (1, 'UNSIGNED', '01', '01', '01', '01', '01', '01', '01', '01', '01', '01', '01'),
    'device_flags': (1, 'BIT_ENUM04', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'device_id': (5, 'UNSIGNED', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010', '1F00000010'),
    'polling_address': (1, 'UNSIGNED', '80', '80', '80', '80', '80', '80', '80', '80', '80', '80', '80'),
    'tag': (8,'PACKED_ASCII','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820','514CF0C60820'),  # TT301
    'message': (32,'PACKED_ASCII','34510910F4A010581414D405481515481820820820820820'),  # MEDIDOR DE TEMPERATURA
    'descriptor': (16,'PACKED_ASCII','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820'),  # TEMPERATURA
    'date': (3, 'DATE', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879'),  # 19/08/2021
    'upper_range_value': (4, 'FLOAT', '44548000', '44548000', '44548000', '44548000', '44548000', '44548000', '44548000', '44548000', '44548000', '44548000', '44548000'),  # 850
    'lower_range_value': (4, 'FLOAT', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000', 'C3480000'),  # -200
    'PROCESS_VARIABLE': (4,'FLOAT',
        '@(HART.FV100CA.percent_of_range / 100) * (HART.FV100CA.upper_range_value - HART.FV100CA.lower_range_value) + HART.FV100CA.lower_range_value',
        '@(HART.FIT100CA.percent_of_range / 100) * (HART.FIT100CA.upper_range_value - HART.FIT100CA.lower_range_value) + HART.FIT100CA.lower_range_value',
        '@(HART.FV100AR.percent_of_range / 100) * (HART.FV100AR.upper_range_value - HART.FV100AR.lower_range_value) + HART.FV100AR.lower_range_value',
        '@(HART.FIT100AR.percent_of_range / 100) * (HART.FIT100AR.upper_range_value - HART.FIT100AR.lower_range_value) + HART.FIT100AR.lower_range_value',
        '@(HART.TIT100.percent_of_range / 100) * (HART.TIT100.upper_range_value - HART.TIT100.lower_range_value) + HART.TIT100.lower_range_value',
        '@(HART.FIT100V.percent_of_range / 100) * (HART.FIT100V.upper_range_value - HART.FIT100V.lower_range_value) + HART.FIT100V.lower_range_value',
        '@(HART.PIT100V.percent_of_range / 100) * (HART.PIT100V.upper_range_value - HART.PIT100V.lower_range_value) + HART.PIT100V.lower_range_value',
        '@(HART.LIT100.percent_of_range / 100) * (HART.LIT100.upper_range_value - HART.LIT100.lower_range_value) + HART.LIT100.lower_range_value',
        '@(HART.PIT100A.percent_of_range / 100) * (HART.PIT100A.upper_range_value - HART.PIT100A.lower_range_value) + HART.PIT100A.lower_range_value',
        '@(HART.FV100A.percent_of_range / 100) * (HART.FV100A.upper_range_value - HART.FV100A.lower_range_value) + HART.FV100A.lower_range_value',
        '@(HART.FV100A.percent_of_range / 100) * (HART.FV100A.upper_range_value - HART.FV100A.lower_range_value) + HART.FV100A.lower_range_value'
    ),  # 50
    'percent_of_range': (4, 'FLOAT', 
        '42480000', # FV100CA -> 0@100 %
        '$[0.0227],[2.5 1.0],@MODBUS.CLP100.FV100CA/100.0', # FIT100CA  -> 0.0@0.0227,  
        '42480000', # FV100ARA -> 0@100 %
        '@MODBUS.CLP100.FV100AR/100.0' #FIT100AR -> 0.0@0.15
        '@MODBUS.CLP100.qFor/(1000.0 * MODBUS.CLP100.FIT100AR)', # TIT100 -> 0@1000ºC
        '3EB33333', # FIT100V -> 0@0.35 kg/s
        '$[1.0],[1000 0.000001],@MODBUS.CLP100.qFor - 2770.0 * MODBUS.CLP100.FIT100V', # PIT100V -> 
        '$[1.0],[1.1 0.0000000001],@MODBUS.CLP100.FIT100A - MODBUS.CLP100.FIT100V', # LIT100 -> 0@100 %
        '43C80000', # PIT100A -> 0@600 kPa   
        '42480000', # FV100A -> 0@100 %  
        '$[0.5],[1.0 1.0],@math.sqrt(MODBUS.CLP100.PIT100A/400.0)*MODBUS.CLP100.FV100A,' # FIT100A -> Nm3/h
    ),
    'loop_current_mode': (1, 'ENUM00', '00'),
    'loop_current': (4, 'FLOAT', 
        '@(HART.FV100CA.percent_of_range * 0.16) + 4'
        '@(HART.FIT100CA.percent_of_range * 0.16) + 4'
        '@(HART.FV100AR.percent_of_range * 0.16) + 4'
        '@(HART.FIT100AR.percent_of_range * 0.16) + 4'
        '@(HART.TIT100.percent_of_range * 0.16) + 4'
        '@(HART.FIT100V.percent_of_range * 0.16) + 4'
        '@(HART.PIT100V.percent_of_range * 0.16) + 4'
        '@(HART.LIT100.percent_of_range * 0.16) + 4'
        '@(HART.PIT100A.percent_of_range * 0.16) + 4'
        '@(HART.FV100A.percent_of_range * 0.16) + 4'
        '@(HART.FIT100A.percent_of_range * 0.16) + 4'
    ),
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
    'ma_analog_output_1_value': (4, 'FLOAT', '00000000'),
    'sensor1_serial_number': (3, 'UNSIGNED', '000000'),
    'SETPOINT': (4, 'FLOAT', '00000000'),
    'MANIPULATED_VARIABLE': (4, 'FLOAT', '00'),
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
    'range_units': (1, 'UNSIGNED', '00'),
    'output_variable': (4, 'FLOAT', '00000000'),
    'mv_ohms': (4, 'FLOAT', '00000000'),
    'upper_cal_point_value': (4, 'FLOAT', '00000000'),
    'lower_cal_point_value': (4, 'FLOAT', '00000000'),
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