# 📊 Análise de Gorjetas de Restaurante com Seaborn e Pandas

Este projeto utiliza Python para analisar um conjunto de dados sobre gorjetas em um restaurante. O objetivo é comparar o comportamento de consumo e gorjetas entre os períodos de **Almoço** e **Jantar**, transformando dados brutos em gráficos claros e informativos.

### Gráfico Gerado pelo Script:
![Gráfico de Análise de Gorjetas](https://i.imgur.com/your-image-url.png)
_**Dica:** Rode o script, salve a imagem do gráfico que aparece e substitua o link acima pelo seu para um README incrível!_

---

## 🚀 Tecnologias Utilizadas

-   **🐍 Python**
-   **🐼 Pandas:** Para a criação e manipulação da tabela de dados (DataFrame).
-   **🎨 Seaborn & 📈 Matplotlib:** Para a criação dos gráficos.

---

## O Que o Script Faz? (Passo a Passo)

1.  [cite_start]**Criação dos Dados:** O script começa criando um conjunto de dados de exemplo (um DataFrame do Pandas) com informações sobre `valor_total` da conta, `gorjeta`, `dia` da semana e `periodo` do dia (Almoço ou Jantar)[cite: 22, 23, 24].

2.  **Análise e Agrupamento:** Utilizando o método `groupby` do Pandas, os dados são agrupados por "periodo". [cite_start]O script então calcula a **soma** do `valor_total` e da `gorjeta` para o Almoço e para o Jantar, separadamente[cite: 25].

3.  [cite_start]**Visualização Gráfica:** Com os dados já agrupados, o script usa `Seaborn` e `Matplotlib` para gerar dois gráficos de barras lado a lado, permitindo uma comparação visual direta[cite: 26]:
    * **Gráfico 1:** Mostra o valor total faturado em cada período.
    * **Gráfico 2:** Mostra o total de gorjetas recebidas em cada período.

---

## Como Executar

1.  **Pré-requisitos:** Certifique-se de ter as bibliotecas necessárias instaladas:
    ```bash
    pip install pandas matplotlib seaborn
    ```

2.  **Execute o Script:** Basta rodar o arquivo Python em seu terminal.
    ```bash
    python nome_do_seu_script.py
    ```
    Ao final da execução, uma janela com os dois gráficos será exibida na tela.