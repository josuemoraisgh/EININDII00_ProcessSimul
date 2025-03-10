import math
import random
from datetime import date, time, datetime
from hrt_enum import hrt_enum

# Funções auxiliares para manipulação de bits
def get_bits(value: int, start: int, count: int) -> int:
    """Extrai 'count' bits de 'value' a partir da posição 'start' (LSB = posição 0)."""
    mask = (1 << count) - 1
    return (value >> start) & mask

def set_bits(value: int, start: int, count: int, new_value: int) -> int:
    """Define 'count' bits em 'value' a partir de 'start' com o valor 'new_value'."""
    mask = ((1 << count) - 1) << start
    value &= ~mask          # zera os bits na posição desejada
    value |= (new_value << start) & mask  # insere o novo valor
    return value

def split_by_length(s: str, n: int) -> list:
    """Divide a string s em pedaços de tamanho n."""
    return [s[i:i+n] for i in range(0, len(s), n)]

# Funções de conversão de HEX para os tipos

def _hrt_type_hex2_uint(str_uint: str) -> int:
    if not str_uint:
        raise ValueError("Função _hrt_type_hex2_uint recebeu string vazia")
    if len(str_uint) > 4:
        raise ValueError("Função _hrt_type_hex2_uint recebeu hex com mais de 4 caracteres")
    for c in str_uint:
        try:
            d = int(c, 36)
        except Exception:
            raise ValueError("Função _hrt_type_hex2_uint: caractere inválido")
        if d > 15:
            raise ValueError("Função _hrt_type_hex2_uint: caractere não é hexadecimal")
    return int(str_uint, 16)

def _hrt_type_hex2_int(str_int: str) -> int:
    if not str_int:
        raise ValueError("Função _hrt_type_hex2_int recebeu string vazia")
    if len(str_int) > 4:
        raise ValueError("Função _hrt_type_hex2_int recebeu hex com mais de 4 caracteres")
    for c in str_int:
        if int(c, 36) > 15:
            raise ValueError("Função _hrt_type_hex2_int: caractere não é hexadecimal")
    val = int(str_int, 16)
    # Interpretar como inteiro com 16 bits (valor com sinal)
    if val >= 0x8000:
        val -= 0x10000
    return val

def _hrt_type_hex2_sreal(str_float: str) -> float:
    number = int(str_float, 16)
    s = get_bits(number, 31, 1)
    e = get_bits(number, 23, 8)
    f = get_bits(number, 0, 23) / 8388608.0
    return ((-1) ** s) * (2 ** (e - 127)) * (1 + f)

def _hrt_type_hex2_pascii(valor: str) -> str:
    parts = split_by_length(valor, 6)
    result = []
    for part in parts:
        # Converte cada parte de hex para inteiro
        num = int(part, 16)
        # Converte o número para uma string binária com 6 bits
        bin_str = format(num, '06b')
        resp = int(bin_str, 2)
        # Se o bit mais significativo (posição 5) for 1, define o bit na posição 6 para 0; senão, para 1.
        if get_bits(resp, 5, 1) == 1:
            new_val = set_bits(resp, 6, 1, 0)
        else:
            new_val = set_bits(resp, 6, 1, 1)
        result.append(new_val)
    # Converte a lista de inteiros em caracteres ASCII
    return ''.join(chr(x) for x in result)

def _hrt_type_hex2_date(valor: str) -> date:
    parts = split_by_length(valor, 2)
    aux = [int(p, 16) for p in parts]
    if len(aux) < 3:
        raise ValueError("Formato do HEX para data incorreto")
    # Cria a data: dia, mês, ano (1900 + valor do terceiro termo)
    return date(1900 + aux[2], aux[1], aux[0])

def _hrt_type_hex2_time(valor: str) -> time:
    parts = split_by_length(valor, 2)
    aux = [int(p, 16) for p in parts]
    if len(aux) < 4:
        raise ValueError("Formato do HEX para tempo incorreto")
    # Conforme o algoritmo Dart:
    resp = aux[0] * 524288 + aux[1] * 2048 + aux[2] * 8 + aux[3] * 0.03125
    hours = int(resp // 3600000)
    minutes = int((resp // 60000) % 60)
    seconds = int((resp // 1000) % 60)
    milliseconds = int(resp % 1000)
    return time(hours, minutes, seconds, milliseconds * 1000)

# Funções de conversão do tipo para HEX

def _hrt_type_uint2_hex(u_int: int) -> str:
    if u_int > 65535:
        raise ValueError("Valor acima do limite máximo")
    valor = format(u_int, 'x')
    resp = valor.zfill(4)
    return resp[-4:].upper()

def _hrt_type_int2_hex(i_val: int) -> str:
    # Converte para representação sem sinal de 16 bits (two's complement)
    if i_val < 0:
        i_val = (i_val + (1 << 16)) % (1 << 16)
    valor = format(i_val, 'x')
    resp = valor.zfill(4)
    return resp[-4:].upper()

def _hrt_type_sreal2_hex(valor_float: float) -> str:
    bits_array = 0
    if valor_float < 0:
        bits_array = set_bits(bits_array, 31, 1, 1)
        valor_float = -valor_float
    e = 127 + math.floor(math.log(valor_float, 2))
    bits_array = set_bits(bits_array, 23, 8, e)
    f = math.floor(((valor_float / (2 ** (e - 127))) - 1) * 8388608)
    bits_array = set_bits(bits_array, 0, 23, f)
    return format(bits_array, 'x').upper()

def _hrt_type_pascii2_hex(valor: str) -> str:
    # Converte a string em bytes ASCII
    resp0 = valor.encode('ascii')
    # Para cada byte, pega os 6 bits menos significativos, converte para binário com 6 dígitos
    bits = ''.join(format(b & 0x3F, '06b') for b in resp0)
    parts = split_by_length(bits, 8)
    resp2 = ''.join(format(int(p, 2), 'x').zfill(2) for p in parts)
    return resp2.upper()

def _hrt_type_date2_hex(valor: date) -> str:
    day = format(valor.day, 'x').zfill(2)
    month = format(valor.month, 'x').zfill(2)
    year = format(valor.year - 1900, 'x').zfill(2)
    return (day + month + year).upper()

def _hrt_type_time2_hex(valor: time) -> str:
    total_ms = valor.hour * 3600000 + valor.minute * 60000 + valor.second * 1000 + int(valor.microsecond / 1000)
    aux = int(total_ms / 0.03125)
    part1 = format(get_bits(aux, 24, 8), 'x').zfill(2)
    part2 = format(get_bits(aux, 16, 8), 'x').zfill(2)
    part3 = format(get_bits(aux, 8, 8), 'x').zfill(2)
    part4 = format(get_bits(aux, 0, 8), 'x').zfill(2)
    return (part1 + part2 + part3 + part4).upper()

def _hrt_type_hex2_enum(index, valor):
    find_value_in_dict(hrt_enum[index],valor)

def _hrt_type_enum2_hex(index, valor):
    hrt_enum[index][valor]

def find_value_in_dict(range_dict, value):
    """
    Procura no dicionário se o valor fornecido corresponde a uma chave exata ou está dentro de um intervalo.

    :param range_dict: Dicionário com chaves que podem ser valores exatos ou intervalos.
    :param value: Valor a ser procurado. Pode ser um número ou uma string hexadecimal.
    :return: O valor correspondente no dicionário se encontrado, None caso contrário.
    """

    # Converte o valor para hexadecimal se for um número
    if isinstance(value, int):
        value_hex = f"{value:02x}"
    elif isinstance(value, str):
        if value.startswith('0x'):
            value_hex = value[2:]
        else:
            value_hex = value
    else:
        raise ValueError("Valor deve ser um número ou uma string hexadecimal")

    # Converte o valor para int para comparações
    value_int = int(value_hex, 16)

    # Percorre o dicionário
    for key in range_dict:
        # Verifica se a chave é um intervalo
        if '-' in key:
            start, end = key.split('-')
            start_int = int(start, 16)
            end_int = int(end, 16)
            # Verifica se o valor está dentro do intervalo
            if start_int <= value_int <= end_int:
                return range_dict[key]
        else:
            # Se a chave não é um intervalo, compara diretamente
            if key == value_hex:
                return range_dict[key]

    # Se não encontrar o valor, retorna None
    return "INVALID TYPE"

# Funções principais

def hrt_type_hex_to(valor: str, type_str: str):
    t = type_str.upper()
    if t in ['UINT', 'UNSIGNED']:
        parts = split_by_length(valor, 2)
        # Retorna a concatenação das conversões (como string)
        return ''.join(str(_hrt_type_hex2_uint(p)) for p in parts)
    elif t in ['SREAL', 'FLOAT']:
        return _hrt_type_hex2_sreal(valor)
    elif t in ['DATE']:
        return _hrt_type_hex2_date(valor)
    elif t in ['INT']:
        return _hrt_type_hex2_int(valor)
    elif t in ['PASCII', 'PACKED_ASCII']:
        return _hrt_type_hex2_pascii(valor)
    elif t in ['TIME']:
        return _hrt_type_hex2_time(valor)
    else:
        return _hrt_type_hex2_enum(int(t[4:]), valor)

def hrt_type_hex_from(valor, type_str: str) -> str:
    t = type_str.upper()
    if t in ['UINT', 'UNSIGNED']:
        return _hrt_type_uint2_hex(valor)
    elif t in ['SREAL', 'FLOAT']:
        return _hrt_type_sreal2_hex(valor)
    elif t in ['DATE']:
        return _hrt_type_date2_hex(valor)
    elif t in ['INT']:
        return _hrt_type_int2_hex(valor)
    elif t in ['PASCII', 'PACKED_ASCII']:
        return _hrt_type_pascii2_hex(valor)
    elif t in ['TIME']:
        return _hrt_type_time2_hex(valor)
    else:
        return _hrt_type_enum2_hex(float(t[4:]), valor)

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo: converter um valor HEX para um número real (SReal/FLOAT)
    hex_value = "41200000"  # Exemplo de valor HEX
    real_value = hrt_type_hex_to(hex_value, "SReal")
    print("Valor real:", real_value)

    # Converter um inteiro para HEX (UInt)
    uint_hex = hrt_type_hex_from(12345, "UInt")
    print("UInt para HEX:", uint_hex)

    # Converter uma data para HEX
    data_hex = hrt_type_hex_from(date(2023, 5, 10), "Date")
    print("Data para HEX:", data_hex)

    # Converter uma string (Packed ASCII) para HEX
    pascii_hex = hrt_type_hex_from("Hello", "Packed_ASCII")
    print("Packed_ASCII para HEX:", pascii_hex)