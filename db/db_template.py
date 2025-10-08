import sqlite3
import pandas as pd
from typing import Dict, Tuple, Union

# ['NAME', 'BYTE_SIZE', 'TYPE', 'MB_POINT', 'ADDRESS', 'CLP100']
# MB_POINT = di - Leitura, co - Escrita, hr - Escrita, ir - Leitura
mb_banco: Dict[str, Tuple[str, str, str, str]] = {
    'FIT100CA'  : (4, 'UNSIGNED', 'ir', '01','@int(65535*HART.FIT100CA.percent_of_range)'),   
    'FIT100AR'  : (4, 'UNSIGNED', 'ir', '02','@int(65535*HART.FIT100AR.percent_of_range)'),        
    'TIT100'    : (4, 'UNSIGNED', 'ir', '03','@int(65535*HART.TIT100.percent_of_range)'),
    # 'W_FIT100V' : (4, 'UNSIGNED', 'ir', '04','3F000000'), 
    'PIT100V'   : (4, 'UNSIGNED', 'ir', '05','@int(65535*HART.PIT100V.percent_of_range)'),
    'LIT100'    : (4, 'UNSIGNED', 'ir', '06','@int(65535*HART.LIT100.percent_of_range)'),      
    # 'W_PIT100A' : (4, 'UNSIGNED', 'ir', '07','3F000000'),      
    'FIT100A'   : (4, 'UNSIGNED', 'ir', '08','@int(65535*HART.FIT100A.percent_of_range)'),
    # 'W_FV100CA' : (4, 'UNSIGNED', 'ir', '09','3F000000'),         
    # 'W_FV100AR' : (4, 'UNSIGNED', 'ir', '10','3F000000'),   
    # 'W_FV100A'  : (4, 'UNSIGNED', 'ir', '11','3F000000'), 
    # 'W_AUX'     : (4, 'UNSIGNED', 'ir', '12','3F000000'),        
    
    'FV100CA'   : (4, 'UNSIGNED', 'hr', '01', '3F000000'),   
    'FV100AR'   : (4, 'UNSIGNED', 'hr', '02', '3F000000'), 
    'FIT100V'   : (4, 'UNSIGNED', 'hr', '03', '3F000000'),
    'PIT100A'   : (4, 'UNSIGNED', 'hr', '04', '3F000000'),    
    'FV100A'    : (4, 'UNSIGNED', 'hr', '05', '3F000000'), 
    
    # 'AM_FV100CA' : (1, 'BOOL', 'co', '01', '0'),
    # 'AM_FV100AR' : (1, 'BOOL', 'co', '02', '0'),        
    # 'AM_FV100A'  : (1, 'BOOL', 'co', '03', '0'),  
}
# ['NAME', 'BYTE_SIZE', 'TYPE', 'FV100CA', 'FIT100CA', 'FV100AR', 'FIT100AR', 'TIT100', 'FIT100V', 'PIT100V', 'LIT100', 'PIT100A', 'FV100A', 'FIT100A']
hrt_banco: Dict[str, Tuple[Union[int, float], str, str]] = {
    'frame_type': (1, 'UNSIGNED', '06', '06', '06', '06', '06', '06', '06', '06', '06', '06', '06'), # 02 Request ou 06 Response
    'address_type': (1, 'UNSIGNED', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'), # 00 Frame curto ou 80 Frame Longo
    'error_code': (2, 'ENUM00', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000', '0000'),
    'response_code': (1, 'ENUM27', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30'),
    'device_status': (1, 'BIT_ENUM02', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'comm_status': (1, 'BIT_ENUM03', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'master_address': (1, 'BIT_ENUM01', '80', '80', '80', '80', '80', '80', '80', '80', '80', '80', '80'), # 80 - Master Primário ou 00 Master Secundário)
    'burst_mode': (1, 'BIT_ENUM01', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'), # 40 - Burst ON ou 00 Burst OFF)
    'manufacturer_id': (1, 'ENUM08', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E', '3E'),
    'device_type': (1, 'ENUM01', '03', '01', '03', '01', '02', '01', '01', '01', '01', '03', '01'),
    'request_preambles': (1, 'UNSIGNED', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05'),
    'hart_revision': (1, 'UNSIGNED', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05', '05'),
    'transmitter_revision': (1, 'UNSIGNED', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30'),
    'software_revision': (1, 'UNSIGNED', '04', '03', '01', '01', '04', '01', '01', '01', '01', '01', '01'),
    'hardware_revision': (1, 'UNSIGNED', '08', '01', '01', '01', '01', '01', '01', '01', '01', '01', '01'),
    'device_flags': (1, 'BIT_ENUM04', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'device_id': (3, 'UNSIGNED', '000010', '000011', '000012', '000013', '000014', '000015', '000016', '000017', '000018', '000019', '00001A'),
    'polling_address': (1, 'UNSIGNED', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0A', '0B'),
    'tag': (6,'PACKED_ASCII','0065B1C300C1','189531C300C1','0065B1C30052','189531C30052','014254C70C20','006254C70C16','010254C70C16','00C254C70C20','010254C70C01','0065B1C30060','010254C70C16'),  # TT301
    'message': (32,'PACKED_ASCII',
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
        '34510910F4A010581414D405481515481820820820820820', # MEDIDOR DE TEMPERATURA
    ),  
    'descriptor': (12,'PACKED_ASCII','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820','505350152054552060820820'),  # TEMPERATURA
    'date': (3, 'DATE', '1D097D', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879', '130879'),  # 19/08/2021
    'upper_range_value': (4, 'FLOAT', '42C80000', '3CB9F559', '42C80000', '3E199999', '447A0000', '3EB33333', '41200000', '42C80000', '44160000', '42C80000', '3F0CCCCC'),  # Varia
    'lower_range_value': (4, 'FLOAT', '00000000', '3727C5AC', '00000000', '3727C5AC', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),  # 0
    'PROCESS_VARIABLE': (4,'FLOAT',
        '@HART.FV100CA.percent_of_range * (HART.FV100CA.upper_range_value - HART.FV100CA.lower_range_value) + HART.FV100CA.lower_range_value',
        '@HART.FIT100CA.percent_of_range * (HART.FIT100CA.upper_range_value - HART.FIT100CA.lower_range_value) + HART.FIT100CA.lower_range_value',
        '@HART.FV100AR.percent_of_range * (HART.FV100AR.upper_range_value - HART.FV100AR.lower_range_value) + HART.FV100AR.lower_range_value',
        '@HART.FIT100AR.percent_of_range * (HART.FIT100AR.upper_range_value - HART.FIT100AR.lower_range_value) + HART.FIT100AR.lower_range_value',
        '@HART.TIT100.percent_of_range * (HART.TIT100.upper_range_value - HART.TIT100.lower_range_value) + HART.TIT100.lower_range_value',
        '@HART.FIT100V.percent_of_range * (HART.FIT100V.upper_range_value - HART.FIT100V.lower_range_value) + HART.FIT100V.lower_range_value',
        '@HART.PIT100V.percent_of_range * (HART.PIT100V.upper_range_value - HART.PIT100V.lower_range_value) + HART.PIT100V.lower_range_value',
        '@HART.LIT100.percent_of_range * (HART.LIT100.upper_range_value - HART.LIT100.lower_range_value) + HART.LIT100.lower_range_value',
        '@HART.PIT100A.percent_of_range * (HART.PIT100A.upper_range_value - HART.PIT100A.lower_range_value) + HART.PIT100A.lower_range_value',
        '@HART.FV100A.percent_of_range * (HART.FV100A.upper_range_value - HART.FV100A.lower_range_value) + HART.FV100A.lower_range_value',
        '@HART.FIT100A.percent_of_range * (HART.FIT100A.upper_range_value - HART.FIT100A.lower_range_value) + HART.FIT100A.lower_range_value'
    ),  # 50
    'percent_of_range': (4, 'FLOAT', 
        '@(MODBUS.CLP100.FV100CA / 65535)', # FV100CA -> 0@100% esta em 50%
        '$[1.0],[3.0 1.0], 1,@HART.FV100CA.percent_of_range', # FIT100CA  -> 0.00001@0.0227kg/s
        '@MODBUS.CLP100.FV100AR/65535', # FV100AR -> 0@100% esta em 50%
        '$[1.0],[1.5 1.0], 0.5,@HART.FV100AR.percent_of_range', #FIT100AR -> 0.00001@0.15kg/s        
        '$[1.0],[5.0 1.0], 1.2,@exp(-0.05*((15.0*HART.FIT100AR.percent_of_range/HART.FIT100CA.percent_of_range)-15.0)**2.0)', # TIT100 -> 0@1000ºC
        '@MODBUS.CLP100.FIT100V/65535', # FIT100V -> 0@0.35kg/s esta em 0.175 (50%)
        '$[1.0],[4.0 0.000001], 0.8,@HART.TIT100.percent_of_range - 0.5*HART.FIT100V.percent_of_range', # PIT100V -> 0@10Bar
        '$[1.0],[4.0 0.000001], 0.8,@HART.FIT100A.percent_of_range - HART.FIT100V.percent_of_range', # LIT100 -> 0@100%
        '@MODBUS.CLP100.PIT100A/65535', # PIT100A -> 0@600kPa esta em 400 (66,66%)  
        '@MODBUS.CLP100.FV100A/65535', # FV100A -> 0@100% esta em 50% 
        '$[1.0],[6.0 1.0], 2,@math.sqrt(HART.PIT100A.percent_of_range/0.6666)*HART.FV100A.percent_of_range' # FIT100A -> 0@0.55kg/s
    ),
    'loop_current_mode': (1, 'ENUM00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'loop_current': (4, 'FLOAT', 
        '@(HART.FV100CA.percent_of_range * 0.16) + 4',
        '@(HART.FIT100CA.percent_of_range * 0.16) + 4',
        '@(HART.FV100AR.percent_of_range * 0.16) + 4',
        '@(HART.FIT100AR.percent_of_range * 0.16) + 4',
        '@(HART.TIT100.percent_of_range * 0.16) + 4',
        '@(HART.FIT100V.percent_of_range * 0.16) + 4',
        '@(HART.PIT100V.percent_of_range * 0.16) + 4',
        '@(HART.LIT100.percent_of_range * 0.16) + 4',
        '@(HART.PIT100A.percent_of_range * 0.16) + 4',
        '@(HART.FV100A.percent_of_range * 0.16) + 4',
        '@(HART.FIT100A.percent_of_range * 0.16) + 4'
    ),
    'write_protect': (1, 'ENUM00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'private_label_distributor': (1, 'ENUM00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'final_assembly_number': (3, 'UNSIGNED', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6', '00FBC6'),
    'physical_signaling_code': (1, 'ENUM10', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),  # (Bell 202 Current)
    'units_code': (1, 'ENUM02', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20'),  # (32 - Degrees Celsius)
    'transfer_function_code': (1, 'ENUM03', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),  # (0 - Linear)
    'alarm_selection_code': (1, 'ENUM06', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB'),  # (None)
    'material_code': (1, 'ENUM04', '02', '02', '02', '02', '02', '02', '02', '02', '02', '02', '02'),  # (Stainless Steel 316)
    'write_protect_code': (1, 'ENUM07', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB'),  # (None)
    'burst_mode_control_code': (1, 'ENUM09', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB', 'FB'),  # (None)
    'flag_assignment': (1, 'ENUM11', '01', '01', '01', '01', '01', '01', '01', '01', '01', '01', '01'),  # (Multi-Sensor Field Device)
    'operating_mode_code': (1, 'ENUM14', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),  # (None)
    'analog_output_numbers_code': (1, 'ENUM15', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),  # (Analog Channel 0)
    'ma_analog_output_1_value': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'sensor1_serial_number': (3, 'UNSIGNED', '000000', '000000', '000000', '000000', '000000', '000000', '000000', '000000', '000000', '000000', '000000'),
    'SETPOINT': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'MANIPULATED_VARIABLE': (4, 'FLOAT', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'ERROR_PERCENT_RANGE': (4, 'FLOAT', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'PROPORTIONAL_GAIN': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'INTEGRAL_TIME': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'DERIVATIVE_TIME': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'MV_HIGH_LIMIT': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'MV_LOW_LIMIT': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'MV_ROC_LIMIT': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'POWER_UP_SETPOINT_PERCENT_RANGE': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'POWER_UP_OUTPUT': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'set_point_time': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'range_units': (1, 'UNSIGNED', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    'output_variable': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'mv_ohms': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'upper_cal_point_value': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'lower_cal_point_value': (4, 'FLOAT', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000', '00000000'),
    'process_variable_unit_code': (1, 'ENUM00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00'),
    # 'CONTROLLER_ACTION': (1, 'ENUM00', '00'),
    # 'CONTROLLER_MODE': (1, 'ENUM00', '00'),
    # 'CONTROLLER_TYPE': (1, 'ENUM00', '00'),
    # 'DEVICE_MODE': (1, 'ENUM00', '00'),
    # 'POWER_UP_MODE': (1, 'ENUM00', '00'),
    # 'SETPOINT_TRACKING_MODE': (1, 'ENUM00', '00'),
    # 'ZERO_CUTOFF_FLAG': (1, 'ENUM00', '00'),
    # 'analog_output_alarm_select': (1, 'ENUM00', '00'),
    # 'analog_output_value': (4, 'FLOAT', '00000000'),
    # 'char_and_display_mode': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_auto_clamp': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_characterization': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_comm': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_function': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_mode': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_multidrop': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_password': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_range': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_temp_trim': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_total': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_trim_20': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_trim_4': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_trim_lower': (1, 'UNSIGNED', '00'),
    # 'chg_cnt_trim_upper': (1, 'UNSIGNED', '00'),
    # 'company_identification_code': (1, 'ENUM00', '00'),
    # 'coordinate': (1, 'UNSIGNED', '00'),
    # 'coordinate_group_number': (1, 'UNSIGNED', '00'),
    # 'coordinate_group_number_pid': (1, 'UNSIGNED', '00'),
    # 'coordinate_order': (1, 'UNSIGNED', '00'),
    # 'coordinate_order_pid': (1, 'UNSIGNED', '00'),
    # 'coordinate_pid': (1, 'UNSIGNED', '00'),
    # 'cut_off': (4, 'FLOAT', '00000000'),
    # 'cut_off_mode': (1, 'ENUM00', '00'),
    # 'drain_vent_material': (1, 'ENUM00', '00'),
    # 'eeprom_select': (1, 'ENUM00', '00'),
    # 'flange_material': (1, 'ENUM00', '00'),
    # 'flange_type': (1, 'ENUM00', '00'),
    # 'fluid_density_value': (4, 'FLOAT', '00000000'),
    # 'indic_variable_first': (1, 'ENUM00', '00'),
    # 'indic_variable_second': (1, 'ENUM00', '00'),
    # 'jumper_switch': (1, 'ENUM00', '00'),
    # 'jumper_switch_s_c': (1, 'ENUM00', '00'),
    # 'kayray_model_code': (1, 'ENUM00', '00'),
    # 'level_of_cntrl': (1, 'UNSIGNED', '00'),
    # 'level_of_conf': (1, 'UNSIGNED', '00'),
    # 'level_of_info': (1, 'UNSIGNED', '00'),
    # 'level_of_load': (1, 'UNSIGNED', '00'),
    # 'level_of_maint': (1, 'UNSIGNED', '00'),
    # 'level_of_monit': (1, 'UNSIGNED', '00'),
    # 'level_of_total': (1, 'UNSIGNED', '00'),
    # 'level_of_trim': (1, 'UNSIGNED', '00'),
    # 'level_password': (1, 'UNSIGNED', '00'),
    # 'load_restore_trim': (1, 'UNSIGNED', '00'),
    # 'local_keys_mode_control_codes': (1, 'ENUM00', '00'),
    # 'manipulated_variable_unit_code': (1, 'ENUM00', '00'),
    # 'max_flow': (4, 'FLOAT', '00000000'),
    # 'meter_installation': (1, 'ENUM00', '00'),
    # 'micro_motion_model_code': (1, 'ENUM00', '00'),
    # 'module_fill_fluid': (1, 'ENUM00', '00'),
    # 'module_isolator_material': (1, 'ENUM00', '00'),
    # 'module_range_code': (1, 'ENUM00', '00'),
    # 'module_type_code': (1, 'ENUM00', '00'),
    # 'number_of_remote_seals': (1, 'ENUM00', '00'),
    # 'o_ring_material': (1, 'ENUM00', '00'),
    # 'operation_code_1': (1, 'UNSIGNED', '00'),
    # 'operation_code_2': (1, 'UNSIGNED', '00'),
    # 'output_table_mode': (1, 'ENUM00', '00'),
    # 'over_pressure_maximum_applied': (4, 'FLOAT', '00000000'),
    # 'over_pressure_minimum_applied': (4, 'FLOAT', '00000000'),
    # 'over_pressure_number_of_overpressures': (2, 'UNSIGNED', '0000'),
    # 'over_temperature_maximum': (4, 'FLOAT', '00000000'),
    # 'over_temperature_minimum': (4, 'FLOAT', '00000000'),
    # 'password_1': (6, 'ASCII', '202020202020'),
    # 'password_2': (6, 'ASCII', '202020202020'),
    # 'password_3': (6, 'ASCII', '202020202020'),
    # 'password_4': (6, 'ASCII', '202020202020'),
    # 'password_value': (6, 'ASCII', '202020202020'),
    # 'physical_signaling_codes': (1, 'ENUM00', '00'),
    # 'power_up_setpoint': (4, 'FLOAT', '00000000'),
    # 'pressure_damping_value': (4, 'FLOAT', '00000000'),
    # 'pressure_lower_range_limit': (4, 'FLOAT', '00000000'),
    # 'pressure_lower_range_value': (4, 'FLOAT', '00000000'),
    # 'pressure_minimum_span': (4, 'FLOAT', '00000000'),
    # 'pressure_output_transfer_function': (1, 'ENUM00', '00'),
    # 'pressure_percent_range': (4, 'FLOAT', '00000000'),
    # 'pressure_sensor_serial_number': (3, 'UNSIGNED', '000000'),
    # 'pressure_unit_code': (1, 'ENUM00', '00'),
    # 'pressure_units': (1, 'ENUM00', '00'),
    # 'pressure_upper_range_limit': (4, 'FLOAT', '00000000'),
    # 'pressure_upper_range_value': (4, 'FLOAT', '00000000'),
    # 'pressure_value': (4, 'FLOAT', '00000000'),

    # 'remote_seal_fill_fluid': (1, 'ENUM00', '00'),
    # 'remote_seal_isolator_material': (1, 'ENUM00', '00'),
    # 'remote_seal_type': (1, 'ENUM00', '00'),
    # 'request_temperature_value': (4, 'FLOAT', '00000000'),
    # 'rosemount_analytical_model_code': (1, 'ENUM00', '00'),
    # 'rosemount_model_code': (1, 'ENUM00', '00'),
    # 'sensor_a_lower_sensor_trim_point': (4, 'FLOAT', '00000000'),
    # 'sensor_a_upper_sensor_trim_point': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_actual_1': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_actual_2': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_actual_3': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_actual_4': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_actual_5': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_meas_1': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_meas_2': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_meas_3': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_meas_4': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_meas_5': (4, 'FLOAT', '00000000'),
    # 'sensor_char_trim_mode': (1, 'ENUM00', '00'),
    # 'sensor_char_trim_point_index': (1, 'UNSIGNED', '00'),
    # 'sensor_char_trim_point_mode': (1, 'ENUM00', '00'),
    # 'sensor_char_trim_points': (1, 'UNSIGNED', '00'),
    # 'setpoint_unit_code': (1, 'ENUM00', '00'),
    # 'smar_ordering_code': (22, 'ASCII', '20202020202020202020202020202020202020202020'),
    # 'soft_local_adjust': (1, 'ENUM00', '00'),
    # 'soft_local_adjust_config': (1, 'ENUM00', '00'),
    # 'table_coordinate_0': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_1': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_10': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_11': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_12': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_13': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_14': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_15': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_16': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_17': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_18': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_19': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_2': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_20': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_21': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_22': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_23': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_24': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_25': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_26': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_27': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_28': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_29': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_3': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_30': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_31': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_4': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_5': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_6': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_7': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_8': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_9': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_0': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_1': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_10': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_11': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_12': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_13': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_14': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_15': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_16': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_17': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_18': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_19': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_2': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_20': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_21': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_22': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_23': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_24': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_25': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_26': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_27': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_28': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_29': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_3': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_30': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_31': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_4': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_5': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_6': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_7': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_8': (4, 'FLOAT', '00000000'),
    # 'table_coordinate_pid_9': (4, 'FLOAT', '00000000'),
    # 'table_points': (1, 'UNSIGNED', '00'),
    # 'table_points_pid': (1, 'UNSIGNED', '00'),
    # 'temperature_units': (1, 'ENUM00', '00'),
    # 'temperature_value': (4, 'FLOAT', '00000000'),
    # 'total': (4, 'FLOAT', '00000000'),
    # 'total_conversion_factor': (4, 'FLOAT', '00000000'),
    # 'total_unit_string': (5, 'ASCII', '2020202020'),
    # 'total_units_code': (1, 'ENUM00', '00'),
    # 'totalizer_mode': (1, 'ENUM00', '00'),
    # 'unique_device_type_code': (1, 'ENUM00', '00'),
    # 'universal_revision': (1, 'UNSIGNED', '00'),
    # 'user_unit_mode': (1, 'ENUM00', '00'),
    # 'user_unit_string': (5, 'ASCII', '2020202020'),
    # 'user_units_code': (1, 'ENUM00', '00'),
    # 'user_value_lower': (4, 'FLOAT', '00000000'),
    # 'user_value_upper': (4, 'FLOAT', '00000000'),
    # 'xmtr_specific_status_0': (1, 'BIT_ENUM00', '00'),
    # 'xmtr_specific_status_1': (1, 'BIT_ENUM00', '00'),
    # 'xmtr_specific_status_2': (1, 'BIT_ENUM00', '00'),
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