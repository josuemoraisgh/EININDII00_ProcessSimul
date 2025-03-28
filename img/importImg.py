import base64
import os

# Diretório absoluto onde o script atual está localizado
dir_atual = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para a imagem JPG
caminho_imagem = os.path.join(dir_atual, 'caldeira.jpg')

# Caminho do arquivo de saída
caminho_saida = os.path.join(dir_atual, 'imgCaldeira.py')

with open(caminho_imagem, 'rb') as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Criar o conteúdo do novo arquivo
conteudo_saida = f"""imagem_base64 = b'{encoded_string}'"""

# Salvar no arquivo imgCaldeira.py
with open(caminho_saida, 'w') as output_file:
    output_file.write(conteudo_saida)

print(f"Arquivo {caminho_saida} salvo com sucesso.")