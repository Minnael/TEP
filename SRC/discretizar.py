import json
import pandas as pd
from obterMetricas import encontrar_metricas

def discretizador(janela):
    metricas = encontrar_metricas()
    
    df = pd.read_parquet('TEP/02_TEP_Faulty_Training.parquet')
    df = df[(df['sample'] > 20) & (df['sample'] <= 20 + janela)]

    colunas_sensores = metricas.index.tolist()
    df_sensores = df.set_index(['faultNumber', 'simulationRun', 'sample'])[colunas_sensores]

    df_eventos = pd.DataFrame(index=df_sensores.index, columns=colunas_sensores)
    for sensor in colunas_sensores:
        limite_sup = metricas.loc[sensor, 'limite_sup']
        limite_inf = metricas.loc[sensor, 'limite_inf']

        df_eventos.loc[df_sensores[sensor] > limite_sup, sensor] = f"{sensor}_ALTO"
        df_eventos.loc[df_sensores[sensor] < limite_inf, sensor] = f"{sensor}_BAIXO"

    df_alertas = df_eventos.stack().dropna().reset_index()
    df_alertas.columns = ['faultNumber', 'simulationRun', 'sample', 'sensor', 'evento']
    df_unicos = df_alertas.drop_duplicates(subset=['faultNumber', 'simulationRun', 'evento'], keep='first')

    banco_completo = {}
    for falha, df_da_falha in df_unicos.groupby('faultNumber'):
        transacoes = df_da_falha.groupby('simulationRun')['evento'].apply(list).tolist()
        banco_completo[str(int(falha))] = transacoes

    return banco_completo



banco_json = discretizador(janela=60)

with open('banco_transacoes_tep.json', 'w') as arquivo:
    arquivo.write("{\n")
    total_itens = len(banco_json)
    
    for i, (falha, transacoes) in enumerate(banco_json.items()):
        transacoes_json = json.dumps(transacoes)
        virgula = "," if i < total_itens - 1 else ""
        arquivo.write(f'  "{falha}": {transacoes_json}{virgula}\n')
        
    arquivo.write("}\n")