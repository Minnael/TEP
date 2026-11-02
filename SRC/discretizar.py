from obterMetricas import encontrar_metricas
import pandas
import pyreadr

metricas = encontrar_metricas()

def discretizador():
    dicionario_de_regras = pyreadr.read_r('TEP/02_Dicionario_de_Regras_de_Sequencia.RData')
    df = list(dicionario_de_regras.values())[0]

    # 1. DESCARTA O QUE OCORREU ANTES DA AMOSTRA 20 NO DATASET INTEIRO (TODAS AS FALHAS)
    df_valido = df[df['sample'] >= 20].copy()
    
    colunas_processo = metricas.index.tolist()
    df_valores = df_valido[colunas_processo]

    # 2. VETORIZAÇÃO EXTREMA: PROCESSA TODOS OS MILHÕES DE DADOS NUMÉRICOS SIMULTANEAMENTE
    mascara_alto = df_valores > metricas['limite_sup']
    mascara_baixo = df_valores < metricas['limite_inf']

    # 3. CRIAÇÃO DA TABELA VAZIA E PREENCHIMENTO DOS TEXTOS
    df_eventos = pandas.DataFrame(index=df_valores.index, columns=colunas_processo)
    
    for var in colunas_processo:
        df_eventos.loc[mascara_alto[var], var] = f"{var}_ALTO"
        df_eventos.loc[mascara_baixo[var], var] = f"{var}_BAIXO"

    # 4. AGRUPA AS STRINGS GERADAS NA MESMA LINHA, IGNORANDO AS CÉLULAS VAZIAS (NAN)
    df_valido['itemsets'] = df_eventos.apply(lambda linha: linha.dropna().tolist(), axis=1)

    # 5. REMOVE AS LINHAS ONDE NENHUM EVENTO OCORREU (LISTAS VAZIAS)
    df_valido = df_valido[df_valido['itemsets'].map(len) > 0]

    # 6. NOVIDADE: SEPARA AS TRANSAÇÕES USANDO UM DICIONÁRIO
    banco_completo = {}
    falhas_existentes = df_valido['faultNumber'].unique() # DESCOBRE QUAIS FALHAS EXISTEM (1, 2, 3...)
    
    for falha in falhas_existentes:
        df_da_falha = df_valido[df_valido['faultNumber'] == falha]
        
        # AGRUPA POR SIMULAÇÃO E GUARDA NA GAVETA (CHAVE) CORRETA DO DICIONÁRIO
        banco_completo[falha] = df_da_falha.groupby('simulationRun')['itemsets'].apply(list).tolist()
    
    return banco_completo


# --- TESTANDO E ACESSANDO OS RESULTADOS ---
transacoes_por_falha = discretizador()

# VOCÊ PODE USAR A "CHAVE" (NÚMERO DA FALHA) PARA ACESSAR O QUE QUISER!
print(f"Gavetas geradas (Falhas): {transacoes_por_falha.keys()}")

# EXEMPLO: ACESSANDO A PRIMEIRA RUN (ÍNDICE 0) DA FALHA 4 (CHAVE 4)
print("\nCascata da Falha 4 (Run 1 - 3 primeiros eventos):")
for instante in transacoes_por_falha[4][0][:3]:
    print(instante)