import pyodbc
import pandas as pd
import qrcode
import os
import re
import subprocess

# Função para limpar nomes de arquivo
def limpa_nome_arquivo(nome):
    return re.sub(r'[^\w\-]', '_', str(nome))

# Conexão com o banco Oracle via ODBC
dsn = 'mega'
usuario = 'AIR'
senha = 'AsrFTT8SjK'
conn = pyodbc.connect(f'DSN={dsn};UID={usuario};PWD={senha}')

# Consulta SQL
sql = """
SELECT 
    ORD_IN_CODIGO,
    ORL_ST_LOTEFABRICACAO,
    PRO_ST_ALTERNATIVO,
    PRO_ST_DESCRICAO,
    ORD_DT_ABERTURA_REAL,
    ESV_ST_VALOR
FROM MEGA.CUS_VW_LOTESORDEM@AIR
"""
df = pd.read_sql(sql, conn)
conn.close()

# Criação das pastas
os.makedirs('html_lotes/images', exist_ok=True)
os.makedirs('qrcodes_lotes', exist_ok=True)

# Caminho absoluto da logo no repositório GitHub Pages
URL_LOGO = "https://airslaid.github.io/rastreamento-lotes/html_lotes/images/logo.png"

# Função para gerar QR Code
def gera_qrcode(data, arquivo):
    qr = qrcode.QRCode(version=2, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(arquivo)

# Função para gerar HTML estilizado
def gera_html_estilizado(lote, dados, arquivo):
    nomes_exibicao = {
        'ORD_IN_CODIGO': 'Ordem de Produção',
        'ORL_ST_LOTEFABRICACAO': 'Número do Lote',
        'PRO_ST_ALTERNATIVO': 'Código do Produto',
        'PRO_ST_DESCRICAO': 'Descrição',
        'ORD_DT_ABERTURA_REAL': 'Data de Fabricação',
        'ESV_ST_VALOR': 'Composição'
    }

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Detalhes do Produto</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;700&display=swap" rel="stylesheet" />
  <style>
    body {{
      font-family: 'Montserrat', sans-serif;
      background-color: #f9fafb;
      margin: 0;
      padding: 20px;
    }}
    .container {{
      max-width: 720px;
      margin: auto;
      background: white;
      padding: 30px 25px;
      border-radius: 10px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    }}
    .header {{
      display: flex;
      align-items: center;
      margin-bottom: 25px;
    }}
    .header img {{
      height: 50px;
      margin-right: 15px;
    }}
    .header h1 {{
      font-size: 1.4rem;
      color: #111;
      margin: 0;
      text-transform: uppercase;
    }}
    .item {{
      margin-bottom: 25px;
      padding: 15px 20px;
      background-color: #f8f9fa;
      border-radius: 8px;
      box-shadow: inset 0 0 3px #ddd;
    }}
    .item-title {{
      font-size: 0.85rem;
      color: #b01e23;
      text-transform: uppercase;
      margin-bottom: 8px;
      font-weight: 600;
    }}
    .item-value {{
      font-size: 1.2rem;
      color: #333;
      font-weight: 500;
      word-break: break-word;
    }}
    @media(max-width: 600px) {{
      .container {{ padding: 20px; }}
      .header h1 {{ font-size: 1.2rem; }}
      .item-value {{ font-size: 1rem; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <img src="{URL_LOGO}" alt="Logo">
      <h1>Detalhes do Produto</h1>
    </div>
    {''.join(f"""
    <div class="item">
      <div class="item-title">{nomes_exibicao.get(col, col)}</div>
      <div class="item-value">{val}</div>
    </div>""" for col, val in dados.items())}
  </div>
</body>
</html>
"""
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(html)

# Gerar HTMLs e QR Codes
registro = []
for _, row in df.iterrows():
    lote = row['ORL_ST_LOTEFABRICACAO']
    nome = limpa_nome_arquivo(lote)
    html_filename = f'lote_{nome}.html'
    html_path = os.path.abspath(f'html_lotes/{html_filename}')
    qr_path = f'qrcodes_lotes/qr_{nome}.png'

    dados = row.to_dict()

    # Ajustes de dados
    if dados['ORD_IN_CODIGO'] is not None:
        dados['ORD_IN_CODIGO'] = int(dados['ORD_IN_CODIGO'])
    if dados['ORD_DT_ABERTURA_REAL'] is not None:
        dados['ORD_DT_ABERTURA_REAL'] = dados['ORD_DT_ABERTURA_REAL'].strftime('%d/%m/%Y')

    # Geração dos arquivos
    gera_html_estilizado(lote, dados, html_path)
    url_github = f'https://airslaid.github.io/rastreamento-lotes/html_lotes/{html_filename}'
    gera_qrcode(url_github, qr_path)

    registro.append({
        'Lote': lote,
        'HTML': url_github,
        'QR': os.path.abspath(qr_path)
    })
    print(f"Lote {lote}: HTML e QR gerados.")

# Exporta planilha Excel com os registros
pd.DataFrame(registro).to_excel('lotes_html_qr.xlsx', index=False)
print("Planilha 'lotes_html_qr.xlsx' foi criada.")

# ⚙️ Etapa final: push automático no Git
print("Enviando para o GitHub...")
subprocess.run(["git", "add", "."], cwd=".")
subprocess.run(["git", "commit", "-m", "Atualização automática dos arquivos"], cwd=".")
subprocess.run(["git", "push"], cwd=".")
print("Push realizado com sucesso para o GitHub Pages ✅")
