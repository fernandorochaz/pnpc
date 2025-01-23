from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
from os.path import expanduser

# -*- coding: utf-8 -*-

# Configurar estilo para gráficos
plt.style.use('ggplot')

# Inicializar a aplicação Flask
app = Flask(__name__)

# Defina o diretório de Downloads do usuário
downloads_dir = os.path.join(expanduser("~"), "Downloads")  # Acessa a pasta Downloads do usuário logado

# Função para buscar licitações
def fetch_licitacoes(data_inicial, data_final, palavras_chave):
    base_url = 'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao'
    tamanho_pagina = 50
    urls = []

    # Gerar URLs para busca
    for pagina in range(1, 11):
        for uf in ['PE', 'PB', 'AL', 'SE', 'BA', 'RN', 'CE']:
            url = f'{base_url}?dataInicial={data_inicial}&dataFinal={data_final}&codigoModalidadeContratacao=6&uf={uf}&tamanhoPagina={tamanho_pagina}&pagina={pagina}'
            urls.append(url)

    # Lista para armazenar dados das licitações
    processos = []

    # Buscar dados na API
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            dados_dict = response.json().get('data', [])
            for processo in dados_dict:
                processos.append({
                    "sequencial": processo.get('sequencialCompra'),
                    "orgao": processo.get('orgaoEntidade', {}).get('razaoSocial'),
                    "uf": processo.get('unidadeOrgao', {}).get('ufSigla'),
                    "inclusao": processo.get('dataInclusao'),
                    "amparo_legal": processo.get('amparoLegal', {}).get('descricao'),
                    "abertura": processo.get('dataAberturaProposta'),  # Pode ser ausente
                    "encerramento": processo.get('dataEncerramentoProposta'),
                    "n_processo": processo.get('processo'),
                    "objeto": processo.get('objetoCompra'),
                    "link": processo.get('linkSistemaOrigem'),
                    "valor_estimado": processo.get('valorTotalEstimado'),
                    "valor_homologado": processo.get('valorTotalHomologado'),
                    "disputa": processo.get('modoDisputaNome'),
                    "plataforma": processo.get('usuarioNome'),
                    "situacao": processo.get('situacaoCompraNome'),
                    "srp": processo.get('srp')
                })

    # Criar DataFrame
    df = pd.DataFrame(processos)

    # Verificar e ajustar colunas esperadas
    colunas_esperadas = ['abertura', 'inclusao', 'encerramento', 'valor_estimado']
    for coluna in colunas_esperadas:
        if coluna not in df.columns:
            df[coluna] = None  # Adicionar coluna vazia se não existir

    # Ajustar os tipos de dados e formatar colunas
    df['abertura'] = pd.to_datetime(df['abertura'], errors='coerce')
    df['inclusao'] = pd.to_datetime(df['inclusao'], errors='coerce')
    df['encerramento'] = pd.to_datetime(df['encerramento'], errors='coerce')
    df['valor_estimado'] = pd.to_numeric(df['valor_estimado'], errors='coerce')

    # Filtrar por palavras-chave
    df_filtrado = None
    palavras_chave = [p.lower() for p in palavras_chave]
    if 'objeto' in df.columns:
        filtro = df['objeto'].str.lower().str.contains('|'.join(palavras_chave), na=False)
        df_filtrado = df[filtro]

    else:
        print("A coluna 'objeto' não existe no DataFrame!")

    return df, df_filtrado


    print("Colunas do DataFrame:", df.columns)



@app.route('/')
def index():
    return render_template('index.html')

# Defina o diretório de Downloads do usuário
downloads_dir = os.path.join(expanduser("~"), "Downloads")  # Acessa a pasta Downloads do usuário logado

@app.route('/search', methods=['POST'])
def search():
    data_inicial = request.form.get('data_inicial', '')
    data_final = request.form.get('data_final', '')
    palavras_chave = request.form.get('palavras_chave', '').split(',')

    # Verificar se as datas foram fornecidas
    if not data_inicial or not data_final:
        return "Por favor, forneça as datas inicial e final.", 400

    # Buscar dados e salvar os resultados
    df, df_filtrado = fetch_licitacoes(data_inicial, data_final, palavras_chave)

    data_atual = datetime.now().strftime('%d_%m_%Y')
    file_path = os.path.join(downloads_dir, f'licitacoes_{data_atual}.xlsx')

    # Salvar o DataFrame 'df' sempre
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name='Todos', index=False)

        # Salvar o DataFrame 'df_filtrado' apenas se não estiver vazio
        if df_filtrado is not None and not df_filtrado.empty:
            df_filtrado.to_excel(writer, sheet_name='Filtrados', index=False)
        else:
            print("Não há dados filtrados para salvar.")

    # Gerar gráfico se houver dados filtrados
    graph_path = None
    if df_filtrado is not None and not df_filtrado.empty:
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df_filtrado, x='uf', palette='viridis')
        plt.title('Distribuição de Licitações por Estado')
        plt.xlabel('Estado')
        plt.ylabel('Quantidade')
        plt.xticks(rotation=45)
        graph_path = os.path.join(downloads_dir, 'grafico_distribuicao.png')
        plt.savefig(graph_path)
        plt.close()

    # Passar os dados para o template
    return render_template('resultados.html',
                           df=df.head(10),
                           df_filtrado=df_filtrado.head(10) if df_filtrado is not None and not df_filtrado.empty else None,
                           file_path=file_path,
                           graph_path=graph_path)



@app.route('/download/<filename>')
def download(filename):
    return redirect(url_for('static', filename=f'output/{filename}'))

# Executar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
