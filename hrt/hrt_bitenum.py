hrt_bitEnum = {
    # Sem Nada
    0: {
        0x00: "OK",
        0x01: "Fora dos Limites",
    },
    # Sem Nada
    1: {
        0x00: "OK",
        0x01: "Fora dos Limites",
    },    
    # device_status
    2: {
        0x00: "OK",        
        0x01: "Variável Primária Fora dos Limites",
        0x02: "Variável Não-Primária Fora dos Limites",
        0x04: "Corrente de Loop Saturada",
        0x08: "Corrente de Loop Fixa",
        0x10: "Reservado",
        0x20: "Inicialização a Frio",
        0x40: "Configuração Alterada",
        0x80: "Mau Funcionamento do Dispositivo"
    },
    # comm_status
    3: {
        0x00: "OK",        
        0x01: "Erro de Paridade",
        0x02: "Reservado",
        0x04: "Erro de Overrun",
        0x08: "Erro de Checksum",
        0x10: "Reservado",
        0x20: "Erro de Buffer",
        0x40: "Erro de Comunicação",
        0x80: "Reservado"
    },
    # Sem Nada
    4: {
        0x00: "OK",
        0x01: "Fora dos Limites",
    },     
}