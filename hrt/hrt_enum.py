hrt_enum = {
    # Command-Specific Response Codes
    0: {
        '00': 'No Command-Specific Errors',
        '01': 'Undefined1',
        '02': 'Invalid Selection (Poll Address)',
        '03': 'Passed Parameter Too Large',
        '04': 'Passed Parameter Too Small',
        '05': 'Too Few Data Bytes Received',
        '06': 'Device-Specific Command Error',
        '07': 'In Write Protect Mode',
        '08': 'Update Failure | Update In Progress | Set To Nearest Possible Value (Upper or Lower Range Pushed)',
        '09': 'Invalid Date Code Detected | Lower Range Value Too High | Applied Process Too High | Incorrect Loop Current Mode or Value | Port not Found',
        '0A': 'Lower Range Value Too Low | Applied Process Too Low | Port in Use',
        '0B': 'Upper Range Value Too High | Loop Current Not Active (Device in Multidrop Mode) | Trim Error, Excess Correction Attempted | Maximum Ports In Use',
        '0C': 'Invalid Mode Selection | Upper Range Value Too Low | Segment Length Too Small',
        '0D': 'Upper and Lower Range Values Out Of Limits | Computation Error, Trim Values Were Not Changed',
        '0E': 'Span Too Small (Device Accuracy May Be Impaired) | New Lower Range Value Pushed',
        '0F': 'Undefined2',
        '10': 'Access Restricted',
        '11': 'Invalid Device Variable Index. The Device Variable does not exist in this Field Device.',
        '12': 'Invalid Units Code',
        '13': 'Device Variable index not allowed for this command.',
        '14-1C': 'Undefined3',
        '1D': 'Invalid Span',
        '1E-1F': 'Undefined4',
        '20': 'Busy | A DR Could Not Be Started',
        '21': 'DR Initiated',
        '22': 'DR Running',
        '23': 'DR Dead',
        '24': 'DR Conflict',
        '25-FF': 'Undefined5'
    },
    # Device Type Codes
    1: {
        '01': 'LD301',
        '02': 'TT301',
        '03': 'FY301',
        '04': 'LD291',
        '05': 'TP301',
        '06': 'DT301',
        '07': 'FY400',
    },
    # Engineering Unit Codes
    2: {
        '01': 'inches of water at 68 degrees F',  # Pressão
        '02': 'inches of mercury at 0 degrees C',  # Pressão
        '03': 'feet of water at 68 degrees F',  # Pressão
        '04': 'millimeters of water at 68 degrees F',  # Pressão
        '05': 'millimeters of mercury at 0 degrees C',  # Pressão
        '06': 'pounds per square inch Pressão',  # Pressão
        '07': 'bars',  # Pressão
        '08': 'millibars',  # Pressão
        '09': 'grams per square centimeter',  # Pressão
        '0A': 'kilograms per square centimeter',  # Pressão
        '0B': 'pascals',  # Pressão
        '0C': 'kilopascals',  # Pressão
        '0D': 'torr',  # Pressão
        '0E': 'atmospheres',  # Pressão
        '20': 'Degrees Celsius',  # Temperatura
        '21': 'Degrees Fahrenheit',  # Temperatura
        '22': 'Degrees Rankine',  # Temperatura
        '23': 'Kelvin',  # Temperatura
        '25': 'ohms',  # Resistência
        '26': 'hertz',  # OUTROS
        '2C': 'feet',  # Tamanho
        '2D': 'meters',  # Tamanho
        '2F': 'inches',  # Tamanho
        '30': 'centimeters',  # Tamanho
        '31': 'millimeters',  # Tamanho
        '32': 'minutes',  # Tempo
        '33': 'seconds',  # Tempo
        '34': 'hours',  # Tempo
        '35': 'days',  # Tempo
        '38': 'microsiemens',  # OUTROS
        '39': 'percent',  # OUTROS
        '3B': 'pH',  # OUTROS
        '42': 'milli siemens per centimeter',  # OUTROS
        '43': 'micro siemens per centimeter',  # OUTROS
        '44': 'newton',  # OUTROS
        '65': 'degrees brix',  # OUTROS
        '69': 'percent solids per weight',  # OUTROS
        '6A': 'percent solids per volume',  # OUTROS
        '6B': 'degrees balling',  # OUTROS
        '6C': 'proof per volume',  # OUTROS
        '6D': 'proof per mass',  # OUTROS
        '8B': 'parts per million',  # OUTROS
        '8F': 'degrees',  # OUTROS
        '90': 'radian',  # OUTROS
        '91': 'inches of water at 60 degrees F',  # Pressão
        '94': 'percent consistency',  # OUTROS
        '95': 'volume percent',  # OUTROS
        '96': 'percent steam quality',  # OUTROS
        '97': 'feet in sixteeenths',  # OUTROS
        '98': 'cubic feet per pound',  # OUTROS
        '99': 'picofarads',  # OUTROS
        '9A': 'mililiters per liter',  # OUTROS
        '9B': 'microliters per liter',  # OUTROS
        'A0': 'percent plato',  # OUTROS
        'A1': 'percent lower explosion level',  # OUTROS
        'A3': 'kohms',  # Resistência
        'A9': 'parts per billion',  # OUTROS
        'ED': 'megapascals',  # Pressão
        'EE': 'inches of water at 4 degrees C',  # Pressão
        'EF': 'millimeters of water at 4 degrees C',  # Pressão
        'FA': 'Not Used',  # GENERICO
        'FB': 'None',  # GENERICO
        'FC': 'Unknown',  # GENERICO
        'FD': 'Special',  # GENERICO
    },
    # Transfer Function Codes
    3: {
        '00': 'Linear Equation',  # y=mx+b
        '01': 'Square Root',  # Equation y=sqrt(x)
        '02': 'Square Root Third Power',  # Equation y=sqrt(x^3)
        '03': 'Square Root Fifth Power',  # Equation y=sqrt(x^5)
        '04': 'Special Curve',
        '05': 'Square',  # Equation y=x^2
        'E6': 'Discrete (Switch)',  # Binary (on/off)
        'E7': 'Square Root Plus Special Curve',  # Do Not Use - See Note 1
        'E8': 'Square Root Third Power Plus Special Curve',  # Do Not Use - See Note 1
        'E9': 'Square Root Fifth Power Plus Special Curve',  # Do Not Use - See Note 1
        'F0-F9': 'Enumeration May Be Used For Manufacturer Specific Definitions',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Material Codes
    4: {
        '00': 'Carbon Steel',
        '01': 'Stainless Steel 304',
        '02': 'Stainless Steel 316',
        '03': 'Hastelloy C',
        '04': 'Monel',
        '05': 'Tantalum',
        '06': 'Titanium',
        '07': 'Pt Ir',
        '08': 'Alloy 20',
        '09': 'Co Cr Ni',
        '0A': 'PTFE',
        '0B': 'Vito',
        '0C': 'Buna N',
        '0D': 'Ethyl Prop',
        '0E': 'Urethane',
        '0F': 'Gold Monel',
        '10': 'Tefzel',
        '11': 'Ryton',
        '12': 'Ceramic',
        '13': 'Stainless Steel 316L',
        '14': 'PVC',
        '15': 'Nitrile Rubber',
        '16': 'Kalrez',
        '17': 'Inconel',
        '18': 'Kynar',
        '19': 'Aluminium',
        '1A': 'Nickel',
        '1B': 'FEP',
        '1C': 'Stainless Steel 316 Ti',
        '1E': 'Hastelloy C276',
        '1F': 'Klinger C4401',
        '20': 'Thermotork',
        '21': 'Grafoil',
        '22': 'PTFE Coated 316l Sst',
        '23': 'Gold Plated Hastelloy C276',
        '24': 'PTFE Glass',
        '25': 'PTFE Graphite',
        '26': 'Aflas',
        'EA': 'PTFE Hastelloy',
        'EB': 'Stainless Steel CF 8M',
        'EC': 'Hastelloy Nitrile SST',
        'ED': 'Gold Plated SST',
        'EF': 'Monel 400',
        'F0-F9': 'Enumeration May Be Used For Manufacturer Specific Definitions',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Desconhecido
    5: {},
    # Alarm Selection Codes
    6: {
        '00': 'High',
        '01': 'Low',
        'EF': 'Hold Last Output Value',
        'F0-F9': 'Enumeration May Be Used For Manufacturer Specific Definitions',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Write Protect Codes
    7: {
        '00': 'No - Not Write Protected',
        '01': 'Yes - Write Protected',
        'F0-F9': 'Enumeration May Be Used For Manufacturer Specific Definitions',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Manufacturer Identification Codes
    8: {
        '01': 'Acromag',
        '02': 'Allen Bradley',
        '03': 'Ametek',
        '04': 'Analog Devices',
        '05': 'Elsag Bailey',
        '06': 'Beckman',
        '07': 'Bell Microsensor',
        '08': 'Bourns',
        '09': 'Bristol Babcock',
        '0A': 'Brooks Instrument',
        '0B': 'Chessell',
        '0C': 'Combustion Engineering',
        '0D': 'Daniel Industries',
        '0E': 'Delta',
        '0F': 'Dieterich Standard',
        '10': 'Dohrmann',
        '11': 'Endress & Hauser',
        '12': 'Elsag Bailey',
        '13': 'Fisher Controls',
        '14': 'Foxboro',
        '15': 'Fuji',
        '16': 'ABB Automation',
        '17': 'Honeywell',
        '18': 'ITT Barton',
        '19': 'Kay Ray/Sensall',
        '1A': 'ABB Automation',
        '1B': 'Leeds & Northrup',
        '1C': 'Leslie',
        '1D': 'M-System Co.',
        '1E': 'Measurex',
        '1F': 'Micro Motion',
        '20': 'Moore Industries',
        '21': 'Moore Products',
        '22': 'Ohkura Electric',
        '23': 'Paine',
        '24': 'Rochester Instrument Systems',
        '25': 'Ronan',
        '26': 'Rosemount',
        '27': 'Peek Measurement',
        '28': 'Schlumberger',
        '29': 'Sensall',
        '2A': 'Siemens',
        '2B': 'Weed',
        '2C': 'Toshiba',
        '2D': 'Transmation',
        '2E': 'Rosemount Analytic',
        '2F': 'Metso Automation',
        '30': 'Flowserve',
        '31': 'Varec',
        '32': 'Viatran',
        '33': 'Delta/Weed',
        '34': 'Westinghouse',
        '35': 'Xomox',
        '36': 'Yamatake',
        '37': 'Yokogawa',
        '38': 'Nuovo Pignone',
        '39': 'Promac',
        '3A': 'Exac Corporation',
        '3B': 'Meggitt Mobrey',
        '3C': 'Arcom Control System',
        '3D': 'Princo',
        '3E': 'Smar',
        '3F': 'Foxboro Eckardt',
        '40': 'Measurement Technology',
        '41': 'Applied System Technologies',
        '42': 'Samson',
        '43': 'Sparling Instruments',
        '44': 'Fireye',
        '45': 'Krohne',
        '46': 'Betz',
        '47': 'Druck',
        '48': 'SOR',
        '49': 'Elcon Instruments',
        '4A': 'EMCO',
        '4B': 'Termiflex Corporation',
        '4C': 'VAF Instruments',
        '4D': 'Westlock Controls',
        '4E': 'Drexelbrook',
        '4F': 'Saab Tank Control',
        '50': 'K-TEK',
        '51': 'Flowdata',
        '52': 'Draeger',
        '53': 'Raytek',
        '54': 'Siemens Milltronics PI',
        '55': 'BTG',
        '56': 'Magnetrol',
        '57': 'Metso Automation',
        '58': 'Milltronics',
        '59': 'HELIOS',
        '5A': 'Anderson Instrument Company',
        '5B': 'INOR',
        '5C': 'ROBERTSHAW',
        '5D': 'PEPPERL+FUCHS',
        '5E': 'ACCUTECH',
        '5F': 'Flow Measurement',
        '60': 'KAMSTRUP',
        '61': 'Knick',
        '62': 'VEGA',
        '63': 'MTS Systems Corp.',
        '64': 'Oval',
        '65': 'Masoneilan-Dresser',
        '66': 'BESTA',
        '67': 'Ohmart',
        '68': 'Harold Beck and Sons',
        '69': 'rittmeyer instrumentation',
        '6A': 'Rossel Messtechnik',
        '6B': 'WIKA',
        '6C': 'Bopp & Reuther Heinrichs',
        '6D': 'PR Electronics',
        '6E': 'Jordan Controls',
        '6F': 'Valcom s.r.l.',
        '70': 'US ELECTRIC MOTORS',
        '71': 'Apparatebau Hundsbach',
        '72': 'Dynisco',
        '73': 'Spriano',
        '74': 'Direct Measurement',
        '75': 'Klay Instruments',
        '76': 'Action Instruments',
        '77': 'MMG Automatiky DTR',
        '78': 'Buerkert Fluid Control Systems',
        '79': 'AALIANT Process Mgt',
        '7A': 'PONDUS INSTRUMENTS',
        '7B': 'ZAP S.A. Ostrow Wielkopolski',
        '7C': 'GLI',
        '7D': 'Fisher-Rosemount Performance Technologies',
        '7E': 'Paper Machine Components',
        '7F': 'LABOM',
        '80': 'Danfoss',
        '81': 'Turbo',
        '82': 'TOKYO KEISO',
        '83': 'SMC',
        '84': 'Status Instruments',
        '85': 'Huakong',
        '86': 'Duon System',
        '87': 'Vortek Instruments, LLC',
        '88': 'AG Crosby',
        '89': 'Action Instruments',
        '8A': 'Keystone Controls',
        '8B': 'Thermo Electric Co.',
        '8C': 'ISE-Magtech',
        '8D': 'Rueger',
        '8E': 'Mettler Toledo',
        '8F': 'Det-Tronics',
        '90': 'TN Technologies',
        '91': 'DeZURIK',
        '92': 'Phase Dynamics',
        '93': 'WELLTECH SHANGHAI',
        '94': 'ENRAF',
        '95': '4tech ASA',
        '96': 'Brandt Instruments',
        '97': 'Nivelco',
        '98': 'Camille Bauer',
        '99': 'Metran',
        '9A': 'Milton Roy Co.',
        '9B': 'PMV',
        '9C': 'Turck',
        '9D': 'Panametrics',
        '9E': 'Stahl',
        '9F': 'Analytical Technology Inc.',
        'A0': 'Fieldbus International',
        'A1': 'BERTHOLD',
        'A2': 'InterCorr',
        'A3': 'China BRICONTE Co Ltd',
        'A4': 'Electron Machine',
        'A5': 'Sierra Instruments',
        'A6': 'Fluid Components Intl',
        'FA': 'not_used',
        'FB': 'none',
        'FC': 'unknown',
        'FD': 'special',
    },
    # Burst Mode Control Codes
    9: {
        '00': 'Off',
        '01': 'On',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Physical Signaling Codes
    10: {
        '00': 'Bell 202 Current',
        '01': 'Bell 202 Voltage',
        '02': 'RS-485',
        '03': 'RS-232',
        '06': 'Special',
    },
    # Flag Assignments
    11: {
        '01': 'Multi-Sensor Field Device',
        '02': 'EEPROM Control',
        '04': 'Protocol Bridge Device',
        '08-20': 'Reserved',
        '40': 'C8PSK Capable Field Device',
        '80': 'C8PSK In Multi-Drop Only',
    },
    # Transfer Service Function Codes
    12: {
        '00': 'None',
    },
    # Transfer Service Identifier Codes
    13: {
        '00': 'None',
    },
    # Operating Mode Codes
    14: {
        '00': 'None',
    },
    # Analog Output Numbers Codes
    15: {
        '00': 'Analog Channel 0',
        '01': 'Analog Channel 1',
        '02': 'Analog Channel 2',
        '03': 'Analog Channel 3',
        '04': 'Analog Channel 4',
    },
    # Loop Current Mode Codes
    16: {
        '00': 'Disabled',
        '01': 'Enabled',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Extended Device Status Codes
    17: {
        '01': 'Maintenance Required. This bit is set to indicate that, while the device has not malfunctioned, the Field Device requires maintenance.',
        '02': 'Device Variable Alert. This bit is set if any Device Variable is in an Alarm or Warning State. The host should identify the Device Variable(s) causeing this to be set using the Device Variable Status indicators.',
    },
    # Lock Device Codes
    18: {
        '00': 'Unlocked',
        '01': 'Lock — Temporary (i.e., Device Reset or Power Loss releases the Lock)',
        '02': 'Lock — Permanent (i.e., Device Reset or Power Loss does not affect the Lock)',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Write Device Variable Codes
    19: {
        '00': 'Normal',
        '01': 'Fixed Value',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Device Variable Family Codes
    20: {
        '00-03': 'Reserved. MUST NOT BE USED',
        '04': 'Temperature',
        '05': 'Pressure',
        '06': 'Valve / Actuator',
        '07': 'Simple PID Control',
        '84-F9': 'Reserved. MUST NOT BE USED',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Device Variable Classification Codes
    21: {
        '00': 'Device Variable Not Classified',
        '01-3F': 'Reserved',
        '40': 'Temperature',
        '41': 'Pressure',
        '42': 'Volumetric Flow',
        '43': 'Velocity',
        '44': 'Volume',
        '45': 'Length',
        '46': 'Time',
        '47': 'Mass',
        '48': 'Mass Flow',
        '49': 'Mass Per Volume',
        '4A': 'Viscosity',
        '4B': 'Angular Velocity',
        '4C': 'Area',
        '4D': 'Energy (Work)',
        '4E': 'Force',
        '4F': 'Power',
        '50': 'Frequency',
        '51': 'Analytical',
        '52': 'Capacitance',
        '53': 'Emf',
        '54': 'Current',
        '55': 'Resistance',
        '56': 'Angle',
        '57': 'Conductance',
        '58': 'Volume Per Volume',
        '59': 'Volume Per Mass',
        '5A': 'Concentration',
        '5B': 'Valve Actuator',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Trim Point Codes
    22: {
        '00': 'Reserved',
        '01': 'Lower Trim Point Supported',
        '02': 'Upper Trim Point Supported',
        '03': 'Lower And Upper Trim Point Supported',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Capture Mode Codes
    23: {
        '00': 'Disabled',
        '01': 'Enabled - Catch data from specified Field Device',
        '02': 'Enabled - Catch data from BACK message',
        'FA': 'Not Used',
        'FB': 'None',
        'FC': 'Unknown',
        'FD': 'Special',
    },
    # Physical Layer Type Codes
    24: {
        '00': 'Asynchronous (e.g., FSK, RS-485)',
        '01': 'Synchronous (e.g., PSK)',
        '03': 'Reserved',
    },
    # Lock Device Status
    25: {
        '01': 'Device Locked',
        '02': 'Lock is Permanent',
        '04': 'Locked by Primary Master',
    },
    # Analog Channel Flags
    26: {
        '01': 'This Analog Channel is a Field Device analog input channel. In other words, the Field Device has an ADC connected to this channel when this bit is set.',
    },
    # Response Code
    27: {
        '01-07': 'Error - Single1',
        '08': 'Warning - Multiple1',
        '09-0D': 'Error - Multiple1',
        '0E': 'Warning - Multiple2',
        '0F': 'Error - Multiple2',
        '10-17': 'Error - Single2',
        '18-1B': 'Warning - Single1',
        '1C': 'Error - Multiple3',
        '1D': 'Error - Multiple4',
        '1E': 'Warning - Multiple3',
        '1F': 'Warning - Multiple4',
        '20-40': 'Error - Single3',
        '41-5F': 'Error - Multiple5',
        '60-6F': 'Warning - Single2',
        '70-7F': 'Warning - Multiple5',
    },
    # EEPROM Control Code
    28: {
        '00': 'Burn EEPROM',
        '01': 'Restore Shadow RAM',
        '02-F9': 'Undefined',
    },
}
