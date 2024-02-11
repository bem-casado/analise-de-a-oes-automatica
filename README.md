# Analisador de Ações Status Invest

Este projeto oferece uma ferramenta automatizada que utiliza Python e Pandas para analisar dados de ações baixados do Status Invest. Ele se concentra na identificação do preço teto e na análise baseada em parâmetros específicos, ajudando investidores a tomar decisões informadas sobre suas ações.

## Começando

Para utilizar esta ferramenta, siga os passos abaixo para configurar o ambiente e começar a analisar seus dados.

### Pré-requisitos

Antes de começar, você precisará ter Python e Pandas instalados no seu ambiente. Este projeto foi desenvolvido utilizando as seguintes versões:

- Python 3.8 ou superior
- Pandas 1.2.3

### Instalação

Siga estes passos para configurar o projeto no seu ambiente local:

1. Clone o repositório para sua máquina local:

```bash
git clone https://github.com/seuusuario/analisador-acoes-statusinvest.git
Navegue até o diretório do projeto:
bash
Copy code
cd analisador-acoes-statusinvest
Instale as dependências necessárias:
bash
Copy code
pip install -r requirements.txt
Uso
Para usar a ferramenta, execute o script principal, passando o caminho para o arquivo Excel baixado do Status Invest como argumento:

bash
Copy code
python analisador.py --arquivo caminho_para_o_excel.xlsx
O script analisará os dados do arquivo Excel, focando na identificação do preço teto e em outros parâmetros definidos, e exibirá a análise no terminal ou a salvará em um arquivo de saída, conforme configurado.

Contribuindo
Contribuições são sempre bem-vindas! Se você tem uma sugestão para melhorar esta ferramenta, siga estes passos para contribuir:

Faça o fork do projeto.
Crie uma branch para sua feature (git checkout -b feature/NovaFeature).
Faça commit das suas mudanças (git commit -m 'Adicionando uma nova feature').
Faça push para a branch (git push origin feature/NovaFeature).
Abra um Pull Request.
