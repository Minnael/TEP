import pandas as pd

def encontrar_metricas():
    df = pd.read_parquet('TEP/01_TEP_FaultFree_Training.parquet')

    df = df.iloc[:, 3:]
    medias = df.mean(numeric_only=True)
    desvios = df.std(numeric_only=True)
    tabela_limites = pd.DataFrame({
        'media': medias,
        'desvio': desvios
    })

    '''
    ASSUNTO UTILIZADO: REGRA DOS 3 SIGMAS.
        -Limite Inferior = média(μ) - 3 * desvio(σ)
        -Limite Superior = média(μ) + 3 * desvio(σ)
        -Qualquer valor entre lim_inf e lim_sup é comportamento normal.
    '''
    tabela_limites['limite_sup'] = tabela_limites['media'] + (3 * tabela_limites['desvio'])
    tabela_limites['limite_inf'] = tabela_limites['media'] - (3 * tabela_limites['desvio'])

    return tabela_limites
