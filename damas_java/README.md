# ♛ Damas Premium - Edição Definitiva (Java Swing)

![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=java&logoColor=white)
![Swing](https://img.shields.io/badge/GUI-Java_Swing-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-success?style=for-the-badge)

Um motor de jogo completo de Damas desenvolvido em Java puro. Este projeto aplica conceitos sólidos de Análise e Desenvolvimento de Sistemas, desde a modelagem de dados em matrizes até a implementação de uma Inteligência Artificial baseada no algoritmo recursivo Minimax.

## 🚀 Funcionalidades e Destaques Técnicos

* **Inteligência Artificial (Minimax):** Cérebro algorítmico capaz de simular o tabuleiro no futuro (Depth-3) e prever as respostas do jogador humano para calcular a jogada mais letal.
* **Motor Cinemático a 60 FPS:** Sistema de interpolação linear (`Math.sin`) assíncrono usando `javax.swing.Timer` para animações fluidas e saltos parabólicos das peças, sem congelar a *thread* principal.
* **Renderização 2.5D Customizada:** Substituição de sprites estáticos por arte renderizada em tempo real via código, utilizando `RadialGradientPaint` para iluminação esférica, sombras projetadas e relevo de interface.
* **Regras Oficiais Brasileiras:** Validação estrita de física de tabuleiro, incluindo captura obrigatória, captura para trás, *chain captures* (combos de múltiplas peças) e a mecânica completa da "Dama Voadora".
* **Máquina de Estados (State Machine):** Gerenciamento limpo de interface entre `TELA_MENU`, `TELA_JOGO` e `TELA_FIM`.
* **Painel de Logs em Tempo Real:** Terminal de depuração visual acoplado à interface para acompanhamento do log de decisões e pontuações da IA.

---

## 🧠 Arquitetura do Software

A base de código foi estruturada isolando responsabilidades, dividindo o motor nas seguintes engrenagens principais:

### 1. Modelagem de Dados (A Matriz)
A "Memória RAM" do jogo é representada por uma matriz `int[][] memoriaTabuleiro` de 8x8. O sistema não manipula imagens no backend, mas sim constantes matemáticas: `0` (Vazio), `1` (Peão IA), `2` (Peão Humano), `3` (Dama IA) e `4` (Dama Humana).

### 2. O Juiz (Motor de Regras)
Os métodos `acharJogadas` e `verificarFimDeJogo` atuam como validadores imutáveis. Eles escaneiam a matriz aplicando matemática de coordenadas para garantir que o *Drag & Drop* do mouse não viole as leis da física do tabuleiro ou permita teletransportes.

### 3. O Cérebro da Inteligência Artificial
Implementado em três níveis de dificuldade, culminando no padrão *Grandmaster*:
* **Função Heurística (`avaliarTabuleiro`):** Varre a matriz dando pesos numéricos. Peões valem 100, Damas 350. Peças nas bordas recebem bônus de segurança, enquanto a permanência na última linha de defesa recebe bônus táticos.
* **Simulador de Linha do Tempo (`simularJogada`):** Cria clones da matriz de estado para aplicar movimentos imaginários sem poluir a interface visual do jogador.
* **Minimax Recursivo:** A IA simula uma jogada sua, vira a mesa e simula a melhor resposta do humano, repetindo o processo recursivamente para descobrir qual ramificação do futuro minimiza o dano do humano e maximiza o dano da IA.

### 4. A View e o Controller (`JPanel` e `MouseAdapter`)
O padrão arquitetural isola a renderização (`Graphics2D` correndo na repintura) da interação do usuário. O ouvinte de mouse traduz coordenadas físicas de pixels para índices da matriz algébrica, acionando o estado `modoCombo` quando regras de restrição de turno se aplicam.

---

## 🛠️ Como Executar o Projeto

O projeto foi construído sem dependências externas pesadas, garantindo fácil compilação e execução em qualquer ambiente que possua a JVM.

**Pré-requisitos:**
* Java Development Kit (JDK) 8 ou superior instalado.

**Passo a passo no terminal:**
1. Clone este repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/damas-premium-java.git](https://github.com/SEU_USUARIO/damas-premium-java.git)