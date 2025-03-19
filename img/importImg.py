import base64
import os

# Diretório absoluto onde o script atual está localizado
dir_atual = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para a imagem JPG
caminho_imagem = os.path.join(dir_atual, 'caldeira.jpg')

with open(caminho_imagem, 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read())
    print(encoded_string)