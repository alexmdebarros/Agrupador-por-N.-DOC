import pandas as pd

# Lê o CSV com separador ";"
df = pd.read_csv("EXTRATO MAGALU 031024.csv", sep=";", dtype=str)

# Converte colunas numéricas e preenche NaN com 0
for col in ['CREDITO', 'DEBITO']:
    df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float).fillna(0)

# Função para filtrar grupos com 1318, 1321 e 1322
def grupo_valido(grupo):
    codigos = grupo['CD.OPER'].astype(str).unique()
    return all(op in codigos for op in ['1318', '1321', '1322'])

# Lista para guardar resultados válidos
resultados = []

# Agrupa por NR. DOC
for nr_doc, grupo in df.groupby('NR. DOC'):
    if grupo_valido(grupo):
        credito_total = grupo['CREDITO'].sum()
        debito_total = grupo['DEBITO'].sum()
        diferenca = credito_total - debito_total
        resultados.append({
            'NR. DOC': nr_doc,
            'CREDITO': credito_total,
            'DEBITO': debito_total,
            'DIFERENCA': diferenca
        })

# Cria DataFrame de saída
df_saida = pd.DataFrame(resultados)

# Formata os valores no padrão brasileiro: 1234,56 (sem milhar)
for col in ['CREDITO', 'DEBITO', 'DIFERENCA']:
    df_saida[col] = df_saida[col].map(lambda x: f"{x:.2f}".replace('.', ','))

# Salva o arquivo CSV com separador ","
df_saida.to_csv("resultado.csv", index=False, sep=";", encoding="utf-8-sig")

print("✅ Arquivo 'resultado.csv' gerado com sucesso no formato BR!")