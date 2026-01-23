# 📊 Analisador de Ações – Pipeline de Dados Financeiros

## 📌 Visão Geral

Este projeto implementa um **pipeline de dados em Python** para ingestão, processamento e análise de dados financeiros de ações obtidos a partir de planilhas exportadas do **Status Invest** ou da API **brapi.dev** (plano gratuito).

O foco principal é a **engenharia de dados aplicada ao domínio financeiro**, contemplando:

- Ingestão de dados brutos
- Limpeza e padronização
- Transformação analítica
- Geração de métricas derivadas (ex: preço teto)
- Saída estruturada para consumo posterior

O projeto simula um **fluxo ETL (Extract, Transform, Load)** em pequena escala, comum em ambientes de **Data Engineering**.

Além disso, o pipeline **normaliza automaticamente nomes de colunas** (remoção de acentos, espaços extras e caixa) para aceitar variações comuns nos exports.

Os parâmetros do filtro (DY, ROE, P/L, P/VP) e do Gordon podem ser ajustados via `config.json` ou via CLI. O relatório de ações inclui uma aba de **Ranking** com pesos configurados no código e usando também a coluna **DL/EBIT**.

---

## 🏗️ Arquitetura do Pipeline

**Fluxo de dados:**

1. **Extract**
   - Entrada via arquivo CSV exportado do Status Invest **ou** via brapi.dev (ações)
   - Para brapi, cada ticker é consultado individualmente e a resposta bruta é salva em `data/raw/`

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
├── fetch_brapi.py       # Extração de ações via brapi.dev
├── config.json          # Parâmetros padrão do filtro
├── requirements.txt     # Dependências do projeto
├── dados/               # (opcional) Dados de entrada e saída
├── data/raw/            # (opcional) snapshots brutos da API
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

## ▶️ Como Executar

### CSV (StatusInvest)
```bash
python analisador.py --source csv --acoes ./dados/acoes.csv --out ./out
```

### brapi.dev (somente ações)
1. Crie `tickers.txt` com um ticker por linha (ex: PETR4).
2. Execute:
```bash
python analisador.py --source brapi --tickers ./tickers.txt --out ./out
```

> **FIIs continuam apenas via CSV.** Para processar FIIs, use `--fii` com o CSV exportado.

Se sua conta brapi exigir token, defina a variável de ambiente:
```bash
export BRAPI_TOKEN="seu_token"
```

### Snapshot (offline)
Use um JSON salvo previamente em `data/raw/` para rodar sem acesso à API:
```bash
python analisador.py --source snapshot --snapshot ./data/raw/brapi_snapshot_YYYYMMDD_HHMMSS.json --out ./out
```

Teste offline com o fixture:
```bash
python tests/smoke_snapshot.py
```

## ⚠️ Limitações do plano gratuito do brapi

- 1 ticker por requisição
- Métricas fundamentais limitadas (sem BP/DRE/DFC detalhados)
- Pode haver ausência de indicadores como DL/EBIT, LPA ou VPA

Quando um indicador não está disponível, o pipeline mantém o ticker com **valor NaN** e o ranking
usa uma pontuação neutra para o critério correspondente.

**Métricas do ranking que dependem de disponibilidade na brapi:**
- DY
- ROE
- P/L
- P/VP
- DL/EBIT

## 🔄 Fluxo de dados

1. **Raw**: CSVs do StatusInvest **ou** JSONs do brapi em `data/raw/`
2. **Processed**: DataFrame padronizado com colunas internas
3. **Outputs**: Excel com abas de filtragem, Graham (opcional) e ranking
