# 📊 Analisador de Ações – Pipeline de Dados Financeiros

## 📌 Visão Geral

Este projeto implementa um **pipeline de dados em Python** para ingestão, processamento e análise de dados financeiros de ações obtidos a partir de planilhas exportadas do **Status Invest**.

O foco principal é a **engenharia de dados aplicada ao domínio financeiro**, contemplando:

- Ingestão de dados brutos
- Limpeza e padronização
- Transformação analítica
- Geração de métricas derivadas (ex: preço teto)
- Saída estruturada para consumo posterior

O projeto simula um **fluxo ETL (Extract, Transform, Load)** em pequena escala, comum em ambientes de **Data Engineering**.

Além disso, o pipeline **normaliza automaticamente nomes de colunas** (remoção de acentos, espaços extras e caixa) para aceitar variações comuns nos exports.

Os parâmetros do filtro (DY, ROE, P/L, P/VP) e do Gordon podem ser ajustados via `config.json` ou via CLI. O relatório de ações agora inclui uma aba de **Ranking** com pesos configurados no código e usando também a coluna **DL/EBIT**.

---

## 🏗️ Arquitetura do Pipeline

**Fluxo de dados:**

1. **Extract**
   - Entrada via arquivo Excel (.xlsx) exportado do Status Invest

2. **Transform**
   - Limpeza de dados inconsistentes
   - Conversão de tipos
   - Normalização de colunas
   - Cálculo de métricas financeiras (ex: preço teto)

3. **Load**
   - Exibição no terminal
   - Exportação opcional para arquivo estruturado (CSV / Excel)
   - Aba de ranking com pesos (ROE, DY, P/L, P/VP, DL/EBIT)

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Pandas**
- **Excel (.xlsx)** como fonte de dados
- Estrutura preparada para expansão de pipeline ETL

---

## 📁 Estrutura do Projeto

```text
analisador-acoes/
│
├── analisador.py        # Script principal do pipeline
├── config.json          # Parâmetros padrão do filtro
├── requirements.txt     # Dependências do projeto
├── dados/               # (opcional) Dados de entrada e saída
└── README.md
```

## ⚙️ Configuração

O arquivo `config.json` define valores padrão:

```json
{
  "acoes": {
    "dy_min": 5,
    "roe_min": 15,
    "pl_max": 15,
    "pvp_max": 1.5
  },
  "gordon": {
    "k": 0.1,
    "g": 0.03
  }
}
```

Os argumentos de CLI sobrescrevem os valores do `config.json`.
