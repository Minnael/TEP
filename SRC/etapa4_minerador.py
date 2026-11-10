import os
import json
from prefixspan import PrefixSpan

def minerar_padroes(caminho_json='JSON/banco_transacoes_tep.json', suporte_percentual=0.5, min_len=2, max_len=5, caminho_saida='JSON/regras_tep.json'):
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

    if caminho_saida:
        os.makedirs('JSON', exist_ok=True)
        with open(caminho_saida, 'w') as arquivo_regras:
            json.dump(regras_por_falha, arquivo_regras, indent=2)
        print(f"\nRegras salvas com sucesso em: {caminho_saida}")

    return regras_por_falha

if __name__ == '__main__':
    resultados = minerar_padroes()