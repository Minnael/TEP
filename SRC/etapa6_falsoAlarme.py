import json
import pandas as pd
from etapa2_obterMetricas import encontrar_metricas


def verificar_regra_na_corrida(eventos_da_corrida, regra):
    """
    Verifica se uma regra apareceu na sequência de eventos da corrida.
    """
    posicao = 0
    for amostra, evento in eventos_da_corrida:
        if evento == regra[posicao]:
            posicao += 1
            if posicao == len(regra):
                return True
    return False


def testar_falsos_alarmes():
    print("1. Carregando limites estatísticos normais...")
    metricas = encontrar_metricas()
    colunas_sensores = metricas.index.tolist()

    print("2. Carregando regras do regras_tep.json...")
    with open('JSON/regras_tep.json', 'r') as arquivo:
        regras_por_falha = json.load(arquivo)

    todas_as_regras = []
    for falha, lista_regras in regras_por_falha.items():
        for suporte, padrao in lista_regras:
            todas_as_regras.append((falha, padrao))

    print(f"-> Total de regras ativas a testar: {len(todas_as_regras)}")

    print("3. Carregando dados de operação normal (04_TEP_FaultFree_Testing.parquet)...")
    df = pd.read_parquet('TEP/04_TEP_FaultFree_Testing.parquet')

    print("4. Identificando eventos espúrios...")
    df_sensores = df.set_index(['faultNumber', 'simulationRun', 'sample'])[colunas_sensores]
    df_eventos = pd.DataFrame(index=df_sensores.index, columns=colunas_sensores)

    for sensor in colunas_sensores:
        limite_sup = metricas.loc[sensor, 'limite_sup']
        limite_inf = metricas.loc[sensor, 'limite_inf']
        df_eventos.loc[df_sensores[sensor] > limite_sup, sensor] = f"{sensor}_ALTO"
        df_eventos.loc[df_sensores[sensor] < limite_inf, sensor] = f"{sensor}_BAIXO"

    df_alertas = df_eventos.stack().dropna().reset_index()
    df_alertas.columns = ['falha', 'corrida', 'amostra', 'sensor', 'evento']
    df_alertas = df_alertas.sort_values(by=['falha', 'corrida', 'amostra'])

    print("5. Calculando a Taxa de Falsos Alarmes (FAR) nas 48h...")
    corridas_com_falso_alarme = 0
    total_corridas = df['simulationRun'].nunique()

    for corrida, df_corrida in df_alertas.groupby('corrida'):
        eventos_da_corrida = list(zip(df_corrida['amostra'], df_corrida['evento']))
        
        alarme_disparou = False
        for falha, regra in todas_as_regras:
            if verificar_regra_na_corrida(eventos_da_corrida, regra):
                alarme_disparou = True
                break

        if alarme_disparou:
            corridas_com_falso_alarme += 1

    taxa_falso_alarme = (corridas_com_falso_alarme / total_corridas) * 100
    
    print("\n" + "=" * 65)
    print(f"Total de Corridas Avaliadas (48h cada): {total_corridas}")
    print(f"Corridas com Falso Alarme:              {corridas_com_falso_alarme}")
    print(f"Taxa de Falsos Alarmes (FAR):           {taxa_falso_alarme:.2f}%")
    print("=" * 65)


if __name__ == '__main__':
    testar_falsos_alarmes()
