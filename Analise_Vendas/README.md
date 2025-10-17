# 📊 Análise de Vendas com Python: SQL, Pandas e Seaborn

Este projeto é um script completo em Python que realiza uma análise de ponta a ponta sobre um conjunto de dados de vendas fictícias. O script executa todo o processo: cria um banco de dados, insere os dados, analisa as informações com Pandas e, por fim, gera visualizações gráficas para extrair insights.

### Gráfico Gerado pelo Script:
![Gráfico de Análise de Vendas]

---

## 🚀 Tecnologias Utilizadas

-   **🐍 Python**
-   **💾 SQLite3:** Para criação e manipulação do banco de dados.
-   **🐼 Pandas:** Para carregar, tratar e analisar os dados.
-   **📈 Matplotlib & 🎨 Seaborn:** Para a criação de gráficos informativos e com um bom visual.

---

## O Que o Script Faz? (Passo a Passo)

O objetivo é transformar dados brutos em insights visuais. O processo é dividido em 4 etapas simples:

1.  [cite_start]**Criação do Banco de Dados:** O script inicia criando um banco de dados SQLite chamado `dados_vendas.db` e uma tabela chamada `vendas1` para armazenar as informações[cite: 14].

2.  [cite_start]**Inserção de Dados Fictícios:** Para a análise, o script insere um conjunto de 13 vendas de exemplo, ocorridas durante o ano de 2024. Os dados incluem produtos das categorias "Eletrônicos", "Livros" e "Roupas"[cite: 15, 16].

3.  **Análise com Pandas:** Os dados do banco são carregados em um DataFrame do Pandas. A partir daí, são feitas duas análises principais:
    * [cite_start]O total de vendas é agrupado por **categoria** para descobrir qual vende mais[cite: 18].
    * O total de vendas é agrupado por **mês** para entender o comportamento das vendas ao longo do ano.

4.  **Visualização de Dados:** Com os dados analisados, o script usa Matplotlib e Seaborn para gerar dois gráficos lado a lado:
    * [cite_start]Um **gráfico de barras** mostrando o faturamento total de cada categoria[cite: 18].
    * [cite_start]Um **gráfico de linhas** mostrando a evolução das vendas mês a mês[cite: 19].

---

## 💡 Principais Insights Gerados

A análise do script revela automaticamente as seguintes conclusões:

> ### Desempenho por Categoria
> A categoria **Eletrônicos** é a campeã de faturamento, representando a maior parte das vendas. [cite_start]Roupas aparece em segundo lugar, enquanto Livros tem o menor volume[cite: 19, 20].

> ### Sazonalidade das Vendas
> O gráfico mensal mostra picos de vendas no **início (Jan-Fev)** e no **final do ano (Nov-Dez)**, sugerindo uma forte influência de eventos como férias, Black Friday e Natal. [cite_start]Há uma queda visível no meio do ano[cite: 20, 21].

---

## Como Executar

1.  **Pré-requisitos:** Certifique-se de ter as bibliotecas necessárias instaladas:
    ```bash
    pip install pandas matplotlib seaborn
    ```
2.  **Execute o Script:** Basta rodar o arquivo Python em seu terminal.
    ```bash
    python seu_script.py
    ```
    Ao final da execução, uma janela com os gráficos será exibida.