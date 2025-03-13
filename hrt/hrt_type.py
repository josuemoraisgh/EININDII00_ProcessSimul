import math
from datetime import date, time, datetime
from hrt.hrt_enum import hrt_enum
from hrt.hrt_bitenum import hrt_bitEnum
import unittest

# Funções auxiliares para manipulação de bits
def get_bits(value: int, start: int, count: int) -> int:
    mask = (1 << count) - 1
    return (value >> start) & mask

def set_bits(value: int, start: int, count: int, new_value: int) -> int:
    mask = ((1 << count) - 1) << start
    value &= ~mask
    value |= (new_value << start) & mask
    return value

def split_by_length(s: str, n: int) -> list:
    return [s[i:i+n] for i in range(0, len(s), n)]

# Funções de conversão de HEX para os tipos
def _hrt_type_hex2_uint(str_uint: str) -> int:
    if not str_uint:
        raise ValueError("Função _hrt_type_hex2_uint recebeu string vazia")
    if len(str_uint) > 4:
        raise ValueError("Função _hrt_type_hex2_uint recebeu hex com mais de 4 caracteres")
    return int(str_uint, 16)

def _hrt_type_hex2_int(str_int: str) -> int:
    if not str_int:
        raise ValueError("Função _hrt_type_hex2_int recebeu string vazia")
    if len(str_int) > 4:
        raise ValueError("Função _hrt_type_hex2_int recebeu hex com mais de 4 caracteres")
    val = int(str_int, 16)
    return val - 0x10000 if val >= 0x8000 else val

def _hrt_type_hex2_sreal(str_float: str) -> float:
    number = int(str_float, 16)
    s = get_bits(number, 31, 1)
    e = get_bits(number, 23, 8)
    f = get_bits(number, 0, 23) / 8388608.0
    return ((-1) ** s) * (2 ** (e - 127)) * (1 + f)

def _hrt_type_hex2_pascii(valor: str) -> str:
    # Converte o valor hexadecimal para inteiro e depois para uma string binária de múltiplos de 6 bits
    binary_str = bin(int(valor, 16))[2:]
    binary_str = binary_str.zfill(6*(int(len(binary_str) / 6)+(1 if len(binary_str) % 6 > 0 else 0)))  # Garante que o binário tenha o tamanho correto
    numbers = split_by_length(binary_str, 6)
    # Mapeia os valores binários para caracteres ASCII ajustando o bit de posição 6
    ascii_values = []
    for e in numbers:
        resp = int(e, 2)
        if get_bits(resp, 5, 1) == 1:
            resp = set_bits(resp, 6, 1, 0)
        else:
            resp = set_bits(resp, 6, 1, 1)
        ascii_values.append(resp)
    # Decodifica os valores ASCII para string
    return ''.join(map(chr, ascii_values))

def _hrt_type_hex2_date(valor: str) -> date:
    parts = split_by_length(valor, 2)
    aux = [int(p, 16) for p in parts]
    if len(aux) < 3:
        raise ValueError("Formato do HEX para data incorreto")
    return date(1900 + aux[2], aux[1], aux[0])

def _hrt_type_hex2_time(valor: str) -> datetime:
    partes = split_by_length(valor, 2)
    if len(partes) != 4:
        raise ValueError("Formato do HEX para tempo incorreto")
    valores = [int(x, 16) for x in partes]
    total_ms = valores[0] * 524288 + valores[1] * 2048 + valores[2] * 8 + valores[2] * 0.03125
    hours = int(total_ms // 3600000)
    minutes = int((total_ms % 3600000) // 60000)
    seconds = int((total_ms % 60000) // 1000)
    milliseconds = int(total_ms % 1000)
    return datetime(1900, 1, 1, hours, minutes, seconds, milliseconds * 1000)

# Funções de conversão dos tipos para HEX
def _hrt_type_uint2_hex(u_int: int) -> str:
    if u_int > 65535:
        raise ValueError("Valor acima do limite máximo")
    return format(u_int, '04X')

def _hrt_type_int2_hex(i_val: int) -> str:
    if not (-32768 <= i_val <= 65535):
        raise ValueError("Valor fora do intervalo permitido")
    if i_val < 0:
        i_val = (i_val + (1 << 16)) % (1 << 16)
    return format(i_val, '04X')

def _hrt_type_sreal2_hex(valor_float: float) -> str:
    bits_array = 0
    if valor_float < 0:
        bits_array = set_bits(bits_array, 31, 1, 1)
        valor_float = -valor_float
    e = 127 + math.floor(math.log(valor_float, 2))
    bits_array = set_bits(bits_array, 23, 8, e)
    f = math.floor(((valor_float / (2 ** (e - 127))) - 1) * 8388608)
    bits_array = set_bits(bits_array, 0, 23, f)
    return format(bits_array, '08x').lower()

def _hrt_type_pascii2_hex(valor: str) -> str:
    encoded_values = [ord(c) for c in valor]
    binary_values = [bin(get_bits(e, 0, 6))[2:].zfill(6) for e in encoded_values]
    binary_str = ''.join(binary_values).zfill((6*len(encoded_values))+8-(6*len(encoded_values))%8)
    eight_bit_chunks = split_by_length(binary_str, 8)
    hex_str = ''.join(f"{int(chunk, 2):02X}" for chunk in eight_bit_chunks)
    return hex_str

def _hrt_type_date2_hex(valor: date) -> str:
    return f"{valor.day:02X}{valor.month:02X}{valor.year - 1900:02X}"

def _hrt_type_time2_hex(valor: datetime) -> str:
    total_ms = valor.hour * 3600000 + valor.minute * 60000 + valor.second * 1000 + int(valor.microsecond / 1000)
    aux = int(total_ms / 0.03125)
    return f"{(aux >> 24) & 0xFF:02X}{(aux >> 16) & 0xFF:02X}{(aux >> 8) & 0xFF:02X}{aux & 0xFF:02X}"

# Funções principais
def hrt_type_hex_to(valor: str, type_str: str):
    t = type_str.upper()
    if t in ['UINT', 'UNSIGNED']:
        return _hrt_type_hex2_uint(valor)
    elif t in ['SREAL', 'FLOAT']:
        return _hrt_type_hex2_sreal(valor)
    elif t == 'DATE':
        return _hrt_type_hex2_date(valor)
    elif t == 'TIME':
        return _hrt_type_hex2_time(valor)
    elif t == 'INT':
        return _hrt_type_hex2_int(valor)
    elif t in ['PASCII', 'PACKED_ASCII']:
        return _hrt_type_hex2_pascii(valor)
    else:
        return "INVALID TYPE"

def hrt_type_hex_from(valor, type_str: str) -> str:
    t = type_str.upper()
    if t in ['UINT', 'UNSIGNED']:
        return _hrt_type_uint2_hex(int(valor))
    elif t in ['SREAL', 'FLOAT']:
        return _hrt_type_sreal2_hex(float(valor))
    elif t == 'DATE':
        return _hrt_type_date2_hex(valor)
    elif t == 'TIME':
        return _hrt_type_time2_hex(valor)
    elif t == 'INT':
        return _hrt_type_int2_hex(int(valor))
    elif t in ['PASCII', 'PACKED_ASCII']:
        return _hrt_type_pascii2_hex(valor)
    else:
        return "INVALID TYPE"

class TestHrtType(unittest.TestCase):
    # Teste para Int
    def test_valor_hex_vazio(self):
        with self.assertRaises(ValueError):
            hrt_type_hex_to('', 'Int')

    def test_valor_hex_maior_4_caracteres(self):
        with self.assertRaises(ValueError):
            hrt_type_hex_to('00FFF', 'Int')

    def test_valor_hex_caracteres_invalidos(self):
        with self.assertRaises(ValueError):
            hrt_type_hex_to('AZF', 'Int')

    def test_valor_hex_00FF_para_255(self):
        self.assertEqual(hrt_type_hex_to('00FF', 'Int'), 255)

    def test_valor_hex_80FF_para_negativo_32513(self):
        self.assertEqual(hrt_type_hex_to('80FF', 'Int'), -32513)

    def test_valor_hex_0BCD_para_3021(self):
        self.assertEqual(hrt_type_hex_to('0BCD', 'Int'), 3021)
        
    def test_valor_negativo_32513_para_hex(self):
        resultado = _hrt_type_int2_hex(-32513)
        self.assertEqual(resultado, '80FF')

    def test_valor_int_maior_65535_erro(self):
        with self.assertRaises(ValueError):
            _hrt_type_int2_hex(65536)       
    
    # Teste para data
    def test_valor_date_para_hex_12032024(self):
        valor_date = datetime(2024, 3, 12)
        resultado = hrt_type_hex_from(valor_date, 'Date')
        self.assertEqual(resultado, '0C037C')

    def test_valor_hex_para_date_12032024(self):
        valor_hex = '0C037C'
        resultado = hrt_type_hex_to(valor_hex, 'Date')
        self.assertEqual(resultado, datetime(2024, 3, 12, 0, 0).date())     
    
    # Teste para PASCII
    def test_transmissor_para_hex(self):
        valor = 'TRANSMISSOR DE TEMPERATURA'
        self.assertEqual(hrt_type_hex_from(valor, 'PAscii'), '051204E4CD2534CF4A010581414D405481515481')
     
    def test_transmissor_para_hex(self):
        valor_hex = '051204E4CD2534CF4A010581414D405481515481' 
        self.assertEqual(hrt_type_hex_to(valor_hex, 'PAscii'), 'TRANSMISSOR DE TEMPERATURA')
                    
    def test_abacate_para_hex(self):
        valor = 'ABACATE'
        self.assertEqual(hrt_type_hex_from(valor, 'PAscii'), '0010810C1505')

    def test_hex_para_abacate(self):
        valor_hex = '0010810C1505'
        self.assertEqual(hrt_type_hex_to(valor_hex, 'PAscii'), 'ABACATE')

    # Teste para SREAL
    def test_double_para_hex(self):
        valor = 1.4861602783203125
        self.assertEqual(hrt_type_hex_from(valor, 'SReal'), '3fbe3a80')

    def test_hex_para_double(self):
        valor_hex = '3FBE3A80'
        self.assertAlmostEqual(hrt_type_hex_to(valor_hex, 'SReal'), 1.4861602783203125)

    # Teste para TIME
    def test_datetime_para_hex(self):
        valor = datetime.strptime('1900-01-01 00:23:18.526', '%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(hrt_type_hex_from(valor, 'Time'), '02AADFC0')

    def test_hex_para_datetime(self):
        valor_esperado = datetime.strptime('1900-01-01 00:23:18.526', '%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(hrt_type_hex_to('02AADFC0', 'Time'), valor_esperado)

    # Teste para UINT
    def test_int_maior_65535_deve_erro(self):
        valor_int = 65536
        with self.assertRaises(ValueError):
            hrt_type_hex_from(valor_int, 'UInt')

    def test_int_para_hex(self):
        valor_int = 255
        self.assertEqual(hrt_type_hex_from(valor_int, 'UInt'), '00FF')

    def test_hex_vazio_deve_erro(self):
        valor_hex = ''
        with self.assertRaises(ValueError):
            hrt_type_hex_to(valor_hex, 'UInt')

    def test_hex_maior_4_caracteres_deve_erro(self):
        valor_hex = '00FFF'
        with self.assertRaises(ValueError):
            hrt_type_hex_to(valor_hex, 'UInt')

    def test_hex_caracteres_invalidos_deve_erro(self):
        valor_hex = 'AZF'
        with self.assertRaises(ValueError):
            hrt_type_hex_to(valor_hex, 'UInt')

    def test_hex_para_int(self):
        valor_hex = '00FF'
        self.assertEqual(hrt_type_hex_to(valor_hex, 'UInt'), 255)

    def test_hex_abcd_para_int(self):
        valor_hex = 'ABCD'
        self.assertEqual(hrt_type_hex_to(valor_hex, 'UInt'), 43981)    

if __name__ == '__main__':
    unittest.main()