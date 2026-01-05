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
├── requirements.txt     # Dependências do projeto
├── dados/               # (opcional) Dados de entrada e saída
└── README.md
