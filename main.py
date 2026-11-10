import sys
import subprocess
from pathlib import Path

DIRETORIO_RAIZ = Path(__file__).resolve().parent
DIRETORIO_SRC = DIRETORIO_RAIZ / "SRC"

ETAPAS = {
    "1": ("etapa1_conversor.py", "Conversão de .RData para .parquet"),
    "2": ("etapa2_obterMetricas.py", "Cálculo dos limites normais (3.5σ)"),
    "3": ("etapa3_discretizar.py", "Discretização de treino (First-K Events)"),
    "4": ("etapa4_minerador.py", "Mineração de padrões sequenciais (PrefixSpan)"),
    "5": ("etapa5_detector.py", "Detecção online e Detection Delay"),
    "6": ("etapa6_falsoAlarme.py", "Validação de Falsos Alarmes (FAR) nas 48h"),
}


def executar_script(nome_script):
    caminho_script = DIRETORIO_SRC / nome_script
    print(f"\n[Executando: {nome_script}]...")
    resultado = subprocess.run([sys.executable, str(caminho_script)], cwd=str(DIRETORIO_SRC))
    if resultado.returncode != 0:
        print(f"Erro ao executar {nome_script} (Código de saída: {resultado.returncode})")


def main():
    print("=" * 70)
    print("  TCC: Detecção de Falhas no TEP com PrefixSpan")
    print("=" * 70)
    for chave, (script, descricao) in ETAPAS.items():
        print(f"  {chave}. {descricao} ({script})")
    print("  7. Executar Pipeline Completo de Treino e Teste (Etapas 3 -> 4 -> 5 -> 6)")
    print("  0. Sair")
    print("=" * 70)

    opcao = input("\nEscolha uma opção (0 a 7): ").strip()

    if opcao == "0":
        print("Encerrando.")
        return
    elif opcao in ETAPAS:
        executar_script(ETAPAS[opcao][0])
    elif opcao == "7":
        for num in ["3", "4", "5", "6"]:
            executar_script(ETAPAS[num][0])
        print("\nPipeline completo executado com sucesso!")
    else:
        print("Opção inválida.")


if __name__ == "__main__":
    main()
