import pandas as pd

def processar_csv(caminho_entrada, caminho_saida):
    """
    Processa o arquivo CSV de entrada e gera um arquivo CSV agrupado
    - Aplica dedução do 1326 apenas quando existir
    - Quando não houver 1326, inclui todos 1318 no CRÉDITO
    """
    try:
        # Lê o CSV com separador ";"
        df = pd.read_csv(caminho_entrada, sep=";", dtype=str)
        
        # Converte colunas numéricas e preenche NaN com 0
        for col in ['CREDITO', 'DEBITO']:
            df[col] = df[col].str.replace('.', '').str.replace(',', '.').astype(float).fillna(0)
        
        # Lista para guardar resultados válidos
        resultados = []
        
        # Agrupa por NR. DOC
        for nr_doc, grupo in df.groupby('NR. DOC'):
            tem_1318 = '1318' in grupo['CD.OPER'].values
            tem_1321 = '1321' in grupo['CD.OPER'].values
            tem_1322 = '1322' in grupo['CD.OPER'].values
            tem_1326 = '1326' in grupo['CD.OPER'].values
            
            # Ignora grupos solitários
            if not ((tem_1318 and tem_1321 and tem_1322) or (tem_1318 and tem_1326)):
                continue
            
            # Processa grupos válidos
            if tem_1318:
                todos_1318 = grupo[grupo['CD.OPER'] == '1318']
                
                # Quando tem 1326: aplica regra especial
                if tem_1326:
                    primeiro_1318 = todos_1318.iloc[0]
                    outros_1318 = todos_1318.iloc[1:]
                    
                    LIQ_MARKETPLACE = primeiro_1318['CREDITO']
                    BX_MARKETPLACE = grupo[grupo['CD.OPER'] == '1326']['DEBITO'].sum()
                    DIFERENCA_BX_MANUAL = LIQ_MARKETPLACE - BX_MARKETPLACE
                    
                    # CRÉDITO = outros 1318 + 1322 (se existir)
                    credito_total = outros_1318['CREDITO'].sum()
                    if tem_1322:
                        credito_total += grupo[grupo['CD.OPER'] == '1322']['CREDITO'].sum()
                
                # Quando não tem 1326: inclui todos 1318 no CRÉDITO
                else:
                    LIQ_MARKETPLACE = 0  # Não aplicável
                    BX_MARKETPLACE = 0
                    DIFERENCA_BX_MANUAL = 0
                    
                    # CRÉDITO = todos 1318 + 1322
                    credito_total = todos_1318['CREDITO'].sum()
                    if tem_1322:
                        credito_total += grupo[grupo['CD.OPER'] == '1322']['CREDITO'].sum()
                
                # Calcula DÉBITO (1321 se existir)
                debito_total = grupo[grupo['CD.OPER'] == '1321']['DEBITO'].sum() if tem_1321 else 0
                
                # Diferença final
                DIFERENCA_TX_COMISSAO = (DIFERENCA_BX_MANUAL + credito_total) - debito_total
                
                resultados.append({
                    'NR. DOC': nr_doc,
                    'CREDITO': credito_total,
                    'DEBITO': debito_total,
                    'DIFERENCA_TX-COMISSAO': DIFERENCA_TX_COMISSAO,
                    'LIQ_MARKETPLACE': LIQ_MARKETPLACE,
                    'BX_MARKETPLACE': BX_MARKETPLACE,
                    'DIFERENCA_BX-MANUAL': DIFERENCA_BX_MANUAL
                })
        
        # Cria DataFrame de saída
        df_saida = pd.DataFrame(resultados)
        
        # Formata os valores no padrão brasileiro
        for col in ['CREDITO', 'DEBITO', 'DIFERENCA_TX-COMISSAO', 'LIQ_MARKETPLACE', 
                   'BX_MARKETPLACE', 'DIFERENCA_BX-MANUAL']:
            df_saida[col] = df_saida[col].map(lambda x: f"{float(x):.2f}".replace('.', ','))
        
        # Salva o arquivo CSV
        df_saida.to_csv(caminho_saida, index=False, sep=";", encoding="utf-8-sig")
        
        print(f"✅ Arquivo '{caminho_saida}' gerado com sucesso!")
        print(f"Total de registros processados: {len(resultados)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {str(e)}")
        return False


if __name__ == "__main__":
    processar_csv("EXTRATO MAGALU 031024.csv", "resultado_agrupado.csv")