import json
from prefixspan import PrefixSpan

def minerar_padroes(caminho_json='banco_transacoes_tep.json', suporte_percentual=0.5, min_len=2, max_len=5):
    with open(caminho_json, 'r') as arquivo:
        banco_completo = json.load(arquivo)

    regras_por_falha = {}

    for falha, transacoes in banco_completo.items():
        suporte_minimo = int(500 * suporte_percentual)

        ps = PrefixSpan(transacoes)
        ps.minlen = min_len
        ps.maxlen = max_len

        padroes = ps.frequent(suporte_minimo, closed=True)
        padroes.sort(key=lambda x: x[0], reverse=True)

        regras_por_falha[falha] = padroes
        print(f"Falha {falha}: {len(padroes)} padrões encontrados (Suporte mín: {suporte_minimo})")

    return regras_por_falha

if __name__ == '__main__':
    resultados = minerar_padroes()