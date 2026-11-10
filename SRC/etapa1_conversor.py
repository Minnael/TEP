import pandas as pd
import pyreadr

arquivos = [
    '01_TEP_FaultFree_Training', 
    '02_TEP_Faulty_Training', 
    '03_TEP_Faulty_Testing', 
    '04_TEP_FaultFree_Testing',
]

for arquivo in arquivos:
    resultado = pyreadr.read_r(f"{arquivo}.RData")

    nome_objeto = list(resultado.keys())[0]
    df = resultado[nome_objeto]
    df.to_parquet(f"{arquivo}.parquet", index=False)

    print(f"Conversão do arquivo {arquivo}.RData para {arquivo}.parquet concluída!")