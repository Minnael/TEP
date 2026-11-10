import json
import pandas as pd
from etapa2_obterMetricas import encontrar_metricas

def detector(janela=60):
    metricas = encontrar_metricas()
    sensores = metricas.index.tolist()

    with open('JSON/regras_tep.json', 'r') as arquivo:
        regras_por_falha = json.load(arquivo)

    # 1. Carrega apenas as amostras pós-falha (160 até 160 + janela)
    df = pd.read_parquet('TEP/03_TEP_Faulty_Testing.parquet')
    df = df[(df['sample'] >= 160) & (df['sample'] <= 160 + janela)]

    # 2. Gera os eventos (igual ao discretizar.py)
    df_sensores = df.set_index(['faultNumber', 'simulationRun', 'sample'])[sensores]
    df_eventos = pd.DataFrame(index=df_sensores.index, columns=sensores)

    for sensor in sensores:
        limite_sup = metricas.loc[sensor, 'limite_sup']
        limite_inf = metricas.loc[sensor, 'limite_inf']
        df_eventos.loc[df_sensores[sensor] > limite_sup, sensor] = f"{sensor}_ALTO"
        df_eventos.loc[df_sensores[sensor] < limite_inf, sensor] = f"{sensor}_BAIXO"

    df_alertas = df_eventos.stack().dropna().reset_index()
    df_alertas.columns = ['falha', 'corrida', 'amostra', 'sensor', 'evento']

    # 3. Testa as regras em cada falha
    for falha, regras in regras_por_falha.items():
        if not regras:
            continue

        padroes = [r[1] for r in regras]  # apenas as listas de eventos
        df_falha = df_alertas[df_alertas['falha'] == int(falha)]
        delays = []

        for corrida, df_corrida in df_falha.groupby('corrida'):
            eventos = list(zip(df_corrida['amostra'], df_corrida['evento']))
            
            # Verifica se alguma regra bateu nesta corrida
            for padrao in padroes:
                pos = 0
                for amostra, evento in eventos:
                    if evento == padrao[pos]:
                        pos += 1
                        if pos == len(padrao):
                            delays.append(amostra - 160)
                            break
                if pos == len(padrao):
                    break

        taxa = (len(delays) / 500) * 100
        delay_medio = sum(delays) / len(delays) if delays else 0
        print(f"Falha {falha}: {len(delays)}/500 detectadas ({taxa:.1f}%) | Delay médio: {delay_medio:.1f} amostras")

if __name__ == '__main__':
    detector()
