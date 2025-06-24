from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

# Carregue a planilha gerada pelo script anterior 
df = pd.read_excel('lotes_com_qrcode.xlsx')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8" />
    <title>Detalhes do Lote {{ lote }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
</head>
<body class="bg-light">
    <div class="container py-4">
        <h1 class="mb-4">Detalhes do Lote {{ lote }}</h1>
        {% if dados %}
            <table class="table table-striped table-bordered bg-white shadow-sm">
                <tbody>
                    {% for col, val in dados.items() %}
                        <tr>
                            <th style="width: 30%;">{{ col }}</th>
                            <td>{{ val }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div class="alert alert-danger">Lote não encontrado.</div>
        {% endif %}
        <a href="/" class="btn btn-primary mt-3">Voltar</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return "<h2>Bem-vindo! Use a URL /lote/&lt;numero&gt; para ver detalhes do lote.</h2>"

@app.route('/lote/<lote>')
def detalhe_lote(lote):
    linha = df[df['ORL_ST_LOTEFABRICACAO'].astype(str) == lote]
    if linha.empty:
        return render_template_string(HTML_TEMPLATE, lote=lote, dados=None)
    dados = linha.iloc[0].to_dict()
    return render_template_string(HTML_TEMPLATE, lote=lote, dados=dados)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
