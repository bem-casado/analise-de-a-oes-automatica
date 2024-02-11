import pandas as pd
import numpy as np
from openpyxl import load_workbook

caminho_csv = "C:\\Users\\eap23\\OneDrive\\Área de Trabalho\\açoes\\statusinvest-busca-avancada.csv"
df = pd.read_csv(caminho_csv, sep=";")
# Garanta que as colunas 'DY' e 'ROE' são tratadas como strings

df.columns = df.columns.str.strip()
df["PRECO"] = df["PRECO"].astype(str)
df["DY"] = df["DY"].astype(str)
df["ROE"] = df["ROE"].astype(str)
df["P/L"] = df["P/L"].astype(str)
df["P/VPA"] = df["P/VP"].astype(str)
df["LPA"] = df["LPA"].astype(str)
df["VPA"] = df["VPA"].astype(str)
df["PRECO"] = pd.to_numeric(
    df["PRECO"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)
df["DY"] = pd.to_numeric(
    df["DY"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)
df["ROE"] = pd.to_numeric(
    df["ROE"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)
df["P/L"] = pd.to_numeric(
    df["P/L"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)
df["P/VP"] = pd.to_numeric(
    df["P/VP"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)
df["LPA"] = pd.to_numeric(
    df["LPA"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)
df["VPA"] = pd.to_numeric(
    df["VPA"].str.replace("%", "").str.replace(",", ".").str.strip(), errors="coerce"
)


# Especifique o caminho para o novo arquivo Excel
caminho_xlsx = "C:\\Users\\eap23\\OneDrive\\Área de Trabalho\\açoes\\statusinvest-busca-avancada.xlsx"

# Use o método to_excel para escrever o DataFrame para um arquivo Excel
df.to_excel(caminho_xlsx, index=False)
df_filtrado = df[(df["DY"] >= 5) & (df["ROE"] >= 15)]


# graham
df_filtrado_adicional = df_filtrado[
    (df_filtrado["P/L"] <= 15) & (df_filtrado["P/VP"] <= 1.5)
]
df_filtrado_adicional["Valor_Graham"] = (
    np.sqrt(df_filtrado_adicional["P/L"]
    * df_filtrado_adicional["P/VP"]
    * df_filtrado_adicional["LPA"]
    * df_filtrado_adicional["VPA"])
)
df_filtrado_adicional['Diferença_Graham'] = df_filtrado_adicional['Valor_Graham'] - df_filtrado_adicional['PRECO']

colunas_graham = ['TICKER','DY', 'ROE', 'PRECO', 'Valor_Graham', 'Diferença_Graham']
df_filtrado_graham = df_filtrado_adicional[colunas_graham]

book = load_workbook(caminho_xlsx)
with pd.ExcelWriter(caminho_xlsx, engine="openpyxl") as writer:
    writer.book = book

    # Escreva seu DataFrame em uma nova aba
    df_filtrado.to_excel(writer, sheet_name="Filtrado_DY_ROE", index=False)
    df_filtrado_graham.to_excel(writer, sheet_name="Filtrado_Graham", index=False)



#fii
df_fii = pd.read_csv("C:\\Users\\eap23\\OneDrive\\Área de Trabalho\\açoes\\fii.csv", sep=";")

df_fii.columns = df_fii.columns.str.strip()

# Tratar cada coluna (exemplo para colunas genéricas 'Coluna1', 'Coluna2', etc.)
colunas_para_manter = ['TICKER', 'PRECO', 'ULTIMO DIVIDENDO','DY','VALOR PATRIMONIAL COTA','P/VP','CAGR DIVIDENDOS 3 ANOS']  # Substitua com os nomes reais das suas colunas
colunas_para_converter = ['PRECO', 'ULTIMO DIVIDENDO','DY','VALOR PATRIMONIAL COTA','P/VP','CAGR DIVIDENDOS 3 ANOS']
  
for coluna in colunas_para_converter:
    df_fii[coluna] = pd.to_numeric(
        df_fii[coluna].astype(str)
        .str.replace("%", "")
        .str.replace("R$", "")
        .str.replace(",", ".")
        .str.strip(),
        errors='coerce'
    )
caminho_xlsx = "C:\\Users\\eap23\\OneDrive\\Área de Trabalho\\açoes\\fii.xlsx"
df_fii.to_excel(caminho_xlsx, index=False)

df_fii['CAGR DIVIDENDOS 3 ANOS'] = df_fii['CAGR DIVIDENDOS 3 ANOS'] / 100

# Supondo que k seja 10% (ou 0.10)
k = 0.10

# Calculando o preço justo usando a fórmula de Gordon
# Certifique-se de que o CAGR está em termos decimais (por exemplo, 5% deve ser 0.05)
df_fii['Preco_Justo_Gordon'] = ((df_fii['ULTIMO DIVIDENDO']*12))/ (k - 0.03)

# Adicionar o preço justo calculado ao DataFrame existente
df_fii['Preco_Justo_Gordon'] = df_fii['Preco_Justo_Gordon'].round(2)  # Arredondar para 2 casas decimais
df_fii = df_fii[df_fii['Preco_Justo_Gordon'] > 0]

# Salvando o DataFrame com a nova coluna em uma nova aba no Excel
with pd.ExcelWriter(caminho_xlsx, engine='openpyxl', mode='a') as writer:
    df_fii.to_excel(writer, sheet_name='Analise_Gordon', index=False)

df_fii = df_fii.dropna(subset=['Preco_Justo_Gordon'])
df_fii = df_fii.replace([np.inf, -np.inf], np.nan).dropna(subset=['Preco_Justo_Gordon'])

writer.close()
