import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.Timer;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.GradientPaint;
import java.awt.RadialGradientPaint;
import java.awt.geom.Point2D;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Main {

    // MÁQUINA DE ESTADOS
    static final int TELA_MENU = 0;
    static final int TELA_JOGO = 1;
    static final int TELA_FIM = 2;
    static int estadoAtual = TELA_MENU;
    static String mensagemFim = "";

    static int modoDeJogo = 0;
    static int dificuldadeIA = 0;

    static int[][] memoriaTabuleiro = new int[8][8];
    static int pecaSendoArrastada = 0;
    static int linhaDeOrigem = -1;
    static int colunaDeOrigem = -1;
    static int mouseX = 0;
    static int mouseY = 0;
    static int turnoAtual = 2;

    static boolean modoCombo = false;
    static int linhaCombo = -1;
    static int colunaCombo = -1;

    static JPanel telaDoJogo;

    // ANIMAÇÃO
    static boolean animandoIA = false;
    static int animOrigemL = -1, animOrigemC = -1;
    static int animDestinoL = -1, animDestinoC = -1;
    static int animPeca = 0;
    static float progressoAnimacao = 0f;
    static int[] jogadaPendenteIA = null;

    static List<String> logPensamentos = new ArrayList<>();
    static final String[] COLUNAS = {"A", "B", "C", "D", "E", "F", "G", "H"};

    static void adicionarLog(String mensagem) {
        logPensamentos.add(mensagem);
        if (logPensamentos.size() > 22) logPensamentos.remove(0);
        if (telaDoJogo != null) telaDoJogo.repaint();
    }

    static void iniciarNovaPartida() {
        turnoAtual = 2;
        modoCombo = false;
        logPensamentos.clear();
        adicionarLog("--- PARTIDA INICIADA ---");
        if (modoDeJogo == 2) adicionarLog("IA Nível " + dificuldadeIA + " Ativada!");

        for (int linha = 0; linha < 8; linha++) {
            for (int coluna = 0; coluna < 8; coluna++) {
                if ((linha + coluna) % 2 != 0) {
                    if (linha < 3) memoriaTabuleiro[linha][coluna] = 1;
                    else if (linha > 4) memoriaTabuleiro[linha][coluna] = 2;
                    else memoriaTabuleiro[linha][coluna] = 0;
                } else {
                    memoriaTabuleiro[linha][coluna] = 0;
                }
            }
        }
    }

    // =========================================================
    // O JUIZ DO FIM DO MUNDO (Agora mais robusto)
    // =========================================================
    static void verificarFimDeJogo() {
        boolean isVezDaIA = (turnoAtual == 1);
        List<int[]> capturas = acharJogadas(memoriaTabuleiro, true, -1, -1, isVezDaIA);
        List<int[]> normais = acharJogadas(memoriaTabuleiro, false, -1, -1, isVezDaIA);

        // Se o jogador da vez não tiver para onde ir, FIM DE JOGO!
        if (capturas.isEmpty() && normais.isEmpty()) {
            estadoAtual = TELA_FIM;
            if (isVezDaIA) {
                mensagemFim = "VITÓRIA DAS BRANCAS!";
                adicionarLog("FIM: IA ficou sem peças/jogadas.");
            } else {
                mensagemFim = (modoDeJogo == 2) ? "DERROTA! A IA TE ESMAGOU." : "VITÓRIA DAS PRETAS!";
                adicionarLog("FIM: Jogador ficou sem movimentos.");
            }
        }
    }

    static int avaliarTabuleiro(int[][] tab) {
        int nota = 0;
        for (int l = 0; l < 8; l++) {
            for (int c = 0; c < 8; c++) {
                int peca = tab[l][c];
                if (peca == 1) {
                    nota += 100 + (l * 5);
                    if (c == 0 || c == 7) nota += 15;
                    if (l == 0) nota += 25;
                    if (l > 3 && c > 2 && c < 5) nota += 10;
                } else if (peca == 3) {
                    nota += 350;
                } else if (peca == 2) {
                    nota -= 100 + ((7 - l) * 5);
                    if (c == 0 || c == 7) nota -= 15;
                    if (l == 7) nota -= 25;
                } else if (peca == 4) {
                    nota -= 350;
                }
            }
        }
        return nota;
    }

    static int[][] copiarMatriz(int[][] original) {
        int[][] copia = new int[8][8];
        for (int i = 0; i < 8; i++) System.arraycopy(original[i], 0, copia[i], 0, 8);
        return copia;
    }

    static List<int[]> acharJogadas(int[][] tab, boolean buscarCapturas, int linFoco, int colFoco, boolean turnoDaIA) {
        List<int[]> jogadas = new ArrayList<>();
        int[][] direcoes = {{-1, -1}, {-1, 1}, {1, -1}, {1, 1}};

        int aliada1 = turnoDaIA ? 1 : 2;
        int aliadaDama = turnoDaIA ? 3 : 4;
        int inimigo1 = turnoDaIA ? 2 : 1;
        int inimigoDama = turnoDaIA ? 4 : 3;

        for (int l = 0; l < 8; l++) {
            for (int c = 0; c < 8; c++) {
                if (linFoco != -1 && (l != linFoco || c != colFoco)) continue;

                int peca = tab[l][c];
                if (peca == aliada1 || peca == aliadaDama) {
                    for (int[] dir : direcoes) {
                        if (!buscarCapturas) {
                            int lDest = l + dir[0];
                            int cDest = c + dir[1];
                            boolean direcaoCerta = (peca == aliadaDama) || (turnoDaIA ? dir[0] == 1 : dir[0] == -1);

                            if (direcaoCerta && lDest >= 0 && lDest < 8 && cDest >= 0 && cDest < 8) {
                                if (tab[lDest][cDest] == 0) jogadas.add(new int[]{l, c, lDest, cDest, 0, -1, -1});
                            }
                        } else {
                            int lMeio = l + dir[0];
                            int cMeio = c + dir[1];
                            int lDest = l + (dir[0] * 2);
                            int cDest = c + (dir[1] * 2);

                            if (lDest >= 0 && lDest < 8 && cDest >= 0 && cDest < 8) {
                                int pecaMeio = tab[lMeio][cMeio];
                                if ((pecaMeio == inimigo1 || pecaMeio == inimigoDama) && tab[lDest][cDest] == 0) {
                                    jogadas.add(new int[]{l, c, lDest, cDest, 1, lMeio, cMeio});
                                }
                            }
                        }
                    }
                }
            }
        }
        return jogadas;
    }

    static int[][] simularJogada(int[][] tabOriginal, int[] jogada) {
        int[][] tabSimulado = copiarMatriz(tabOriginal);
        int lO = jogada[0], cO = jogada[1], lD = jogada[2], cD = jogada[3], isCap = jogada[4], lCap = jogada[5], cCap = jogada[6];

        int peca = tabSimulado[lO][cO];
        tabSimulado[lO][cO] = 0;
        if (peca == 1 && lD == 7) peca = 3;
        if (peca == 2 && lD == 0) peca = 4;
        tabSimulado[lD][cD] = peca;

        if (isCap == 1) tabSimulado[lCap][cCap] = 0;
        return tabSimulado;
    }

    static int minimax(int[][] tab, int profundidade, boolean isMaximizing) {
        if (profundidade == 0) {
            return avaliarTabuleiro(tab);
        }

        List<int[]> capturas = acharJogadas(tab, true, -1, -1, isMaximizing);
        List<int[]> normais = acharJogadas(tab, false, -1, -1, isMaximizing);
        List<int[]> possiveis = !capturas.isEmpty() ? capturas : normais;

        if (possiveis.isEmpty()) {
            return isMaximizing ? -999999 : 999999;
        }

        if (isMaximizing) {
            int maxEval = -999999;
            for (int[] jogada : possiveis) {
                int[][] tabSimulado = simularJogada(tab, jogada);
                int eval = minimax(tabSimulado, profundidade - 1, false);
                maxEval = Math.max(maxEval, eval);
            }
            return maxEval;
        } else {
            int minEval = 999999;
            for (int[] jogada : possiveis) {
                int[][] tabSimulado = simularJogada(tab, jogada);
                int eval = minimax(tabSimulado, profundidade - 1, true);
                minEval = Math.min(minEval, eval);
            }
            return minEval;
        }
    }

    static boolean temCapturaDisponivel(int[][] tab, int linha, int coluna, int tipoPeca) {
        boolean isPreta = (tipoPeca == 1 || tipoPeca == 3);
        int inimigoNormal = isPreta ? 2 : 1;
        int inimigoDama = isPreta ? 4 : 3;
        int[][] direcoes = {{-1, -1}, {-1, 1}, {1, -1}, {1, 1}};
        for (int i = 0; i < 4; i++) {
            int dirL = direcoes[i][0];
            int dirC = direcoes[i][1];
            int lMeio = linha + dirL;
            int cMeio = coluna + dirC;
            int lDest = linha + (dirL * 2);
            int cDest = coluna + (dirC * 2);
            if (lDest >= 0 && lDest < 8 && cDest >= 0 && cDest < 8) {
                int pecaMeio = tab[lMeio][cMeio];
                if ((pecaMeio == inimigoNormal || pecaMeio == inimigoDama) && tab[lDest][cDest] == 0) {
                    return true;
                }
            }
        }
        return false;
    }

    // =========================================================
    // CORREÇÃO DO CÉREBRO: O Plano B (Resiliência)
    // =========================================================
    static void acionarIA() {
        if (animandoIA || estadoAtual != TELA_JOGO) return;

        adicionarLog("");
        adicionarLog("Calculando matriz do futuro...");

        Timer timerPensamento = new Timer(600, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                int linFoco = modoCombo ? linhaCombo : -1;
                int colFoco = modoCombo ? colunaCombo : -1;

                List<int[]> possiveisIA = acharJogadas(memoriaTabuleiro, true, linFoco, colFoco, true);
                if (possiveisIA.isEmpty() && !modoCombo) {
                    possiveisIA = acharJogadas(memoriaTabuleiro, false, -1, -1, true);
                }

                if (!possiveisIA.isEmpty()) {

                    // O PLANO B: Se tudo der errado, a IA escolhe a primeira jogada da lista
                    int[] jogadaEscolhida = possiveisIA.get(0);

                    if (dificuldadeIA == 1) {
                        jogadaEscolhida = possiveisIA.get(new Random().nextInt(possiveisIA.size()));
                        adicionarLog("Nível Fácil: Aleatório.");
                    }
                    else if (dificuldadeIA == 2) {
                        int melhorNota = Integer.MIN_VALUE; // Correção matemática
                        for (int[] jogada : possiveisIA) {
                            int[][] tabFuturo = simularJogada(memoriaTabuleiro, jogada);
                            int nota = avaliarTabuleiro(tabFuturo) + new Random().nextInt(15);
                            if (nota > melhorNota) { melhorNota = nota; jogadaEscolhida = jogada; }
                        }
                        adicionarLog("Nível Médio: Estratégia Gulosa.");
                    }
                    else if (dificuldadeIA == 3) {
                        int melhorNotaGlobal = Integer.MIN_VALUE; // Garante que qualquer nota será aceita

                        for (int[] jogadaIA : possiveisIA) {
                            int[][] tabSimuladoIA = simularJogada(memoriaTabuleiro, jogadaIA);
                            int notaDaLinhaDoTempo = minimax(tabSimuladoIA, 3, false);

                            String movTxt = COLUNAS[jogadaIA[1]] + (8 - jogadaIA[0]) + "->" + COLUNAS[jogadaIA[3]] + (8 - jogadaIA[2]);
                            adicionarLog("Analisou " + movTxt + " | Score Futuro: " + notaDaLinhaDoTempo);

                            if (notaDaLinhaDoTempo > melhorNotaGlobal) {
                                melhorNotaGlobal = notaDaLinhaDoTempo;
                                jogadaEscolhida = jogadaIA;
                            }
                        }
                        String movFinal = COLUNAS[jogadaEscolhida[1]] + (8 - jogadaEscolhida[0]) + "->" + COLUNAS[jogadaEscolhida[3]] + (8 - jogadaEscolhida[2]);
                        adicionarLog(">>> IA GRANDMASTER ESCOLHEU: " + movFinal);
                    }

                    iniciarAnimacaoIA(jogadaEscolhida);
                } else {
                    // Prevenção extra: Se por algum milagre cair aqui vazio, chama o Juiz.
                    verificarFimDeJogo();
                    telaDoJogo.repaint();
                }
            }
        });
        timerPensamento.setRepeats(false);
        timerPensamento.start();
    }

    static void iniciarAnimacaoIA(int[] jogada) {
        jogadaPendenteIA = jogada;
        animOrigemL = jogada[0]; animOrigemC = jogada[1];
        animDestinoL = jogada[2]; animDestinoC = jogada[3];
        animPeca = memoriaTabuleiro[animOrigemL][animOrigemC];
        memoriaTabuleiro[animOrigemL][animOrigemC] = 0;
        animandoIA = true;
        progressoAnimacao = 0f;

        Timer timerAnima = new Timer(16, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                progressoAnimacao += 0.08f;
                if (progressoAnimacao >= 1.0f) {
                    ((Timer)e.getSource()).stop();
                    animandoIA = false;
                    progressoAnimacao = 1.0f;
                    finalizarJogadaIA();
                }
                telaDoJogo.repaint();
            }
        });
        timerAnima.start();
    }

    static void finalizarJogadaIA() {
        int lD = jogadaPendenteIA[2], cD = jogadaPendenteIA[3], isCap = jogadaPendenteIA[4];

        if (animPeca == 1 && lD == 7) animPeca = 3;
        memoriaTabuleiro[lD][cD] = animPeca;

        if (isCap == 1) {
            memoriaTabuleiro[jogadaPendenteIA[5]][jogadaPendenteIA[6]] = 0;
            adicionarLog("IA Destruiu sua peça!");

            if (temCapturaDisponivel(memoriaTabuleiro, lD, cD, animPeca)) {
                modoCombo = true;
                linhaCombo = lD;
                colunaCombo = cD;
                telaDoJogo.repaint();
                acionarIA();
                return;
            }
        }

        modoCombo = false;
        turnoAtual = 2;
        verificarFimDeJogo();
        telaDoJogo.repaint();
    }

    public static void main(String[] args) {

        JFrame janela = new JFrame("Damas JAVA");
        janela.setSize(1150, 750);
        janela.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        telaDoJogo = new JPanel() {

            private void pintarPeca(Graphics2D pincel, int tipo, int x, int y, int tamanho) {
                Point2D centroLuz = new Point2D.Float(x + tamanho / 3f, y + tamanho / 3f);
                float[] fracoes = {0.0f, 1.0f};
                boolean isPreta = (tipo == 1 || tipo == 3);
                boolean isDama = (tipo == 3 || tipo == 4);

                pincel.setColor(new Color(0, 0, 0, 130));
                pincel.fillOval(x + 5, y + 5, tamanho, tamanho);

                if (isPreta) {
                    pincel.setPaint(new RadialGradientPaint(centroLuz, tamanho, fracoes, new Color[]{new Color(120, 120, 120), new Color(15, 15, 15)}));
                } else {
                    pincel.setPaint(new RadialGradientPaint(centroLuz, tamanho, fracoes, new Color[]{Color.WHITE, new Color(160, 155, 145)}));
                }
                pincel.fillOval(x, y, tamanho, tamanho);

                if (isDama) {
                    pincel.setPaint(new GradientPaint(x, y, new Color(255, 215, 0), x + tamanho, y + tamanho, new Color(184, 134, 11)));
                    pincel.fillOval(x + 4, y + 4, tamanho - 8, tamanho - 8);
                    pincel.setColor(isPreta ? new Color(25, 25, 25) : new Color(240, 240, 240));
                    pincel.fillOval(x + 12, y + 12, tamanho - 24, tamanho - 24);
                    pincel.setPaint(new GradientPaint(x, y, new Color(255, 215, 0), x + tamanho, y + tamanho, new Color(218, 165, 32)));
                    pincel.setFont(new Font("SansSerif", Font.BOLD, tamanho / 2));
                    pincel.drawString("♛", x + (tamanho / 4) + 2, y + (tamanho / 2) + (tamanho / 6) + 2);
                } else {
                    pincel.setColor(isPreta ? new Color(40, 40, 40) : new Color(220, 220, 220));
                    pincel.drawOval(x + 6, y + 6, tamanho - 12, tamanho - 12);
                    pincel.setColor(new Color(150, 150, 150));
                    pincel.setFont(new Font("SansSerif", Font.BOLD, tamanho / 2));
                    pincel.drawString("★", x + (tamanho / 4) + 2, y + (tamanho / 2) + (tamanho / 6));
                }
            }

            @Override
            public void paint(Graphics pincelBasico) {
                super.paint(pincelBasico);
                Graphics2D pincel = (Graphics2D) pincelBasico;
                pincel.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                pincel.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

                int lTela = getWidth(); int aTela = getHeight();
                pincel.setPaint(new GradientPaint(0, 0, new Color(40, 25, 15), lTela, aTela, new Color(10, 5, 2)));
                pincel.fillRect(0, 0, lTela, aTela);

                if (estadoAtual == TELA_MENU) {
                    pincel.setFont(new Font("Serif", Font.BOLD, 60));
                    String titulo = "DAMAS PREMIUM";
                    int xTitulo = (lTela - pincel.getFontMetrics().stringWidth(titulo)) / 2;
                    pincel.setColor(Color.BLACK); pincel.drawString(titulo, xTitulo + 4, 154);
                    pincel.setPaint(new GradientPaint(0, 100, new Color(255, 215, 0), 0, 160, new Color(184, 134, 11)));
                    pincel.drawString(titulo, xTitulo, 150);

                    int[] yBotoes = {250, 330, 410, 490};
                    String[] textosBotoes = {"JOGADOR VS JOGADOR", "IA - NÍVEL FÁCIL", "IA - NÍVEL MÉDIO", "IA - NÍVEL DIFÍCIL (MINIMAX)"};
                    pincel.setFont(new Font("SansSerif", Font.BOLD, 18));

                    for (int i = 0; i < 4; i++) {
                        int xBotao = (lTela - 350) / 2;
                        pincel.setColor(new Color(0, 0, 0, 150)); pincel.fillRoundRect(xBotao + 5, yBotoes[i] + 5, 350, 60, 15, 15);
                        pincel.setPaint(new GradientPaint(0, yBotoes[i], new Color(90, 50, 25), 0, yBotoes[i] + 60, new Color(50, 25, 10)));
                        pincel.fillRoundRect(xBotao, yBotoes[i], 350, 60, 15, 15);
                        pincel.setColor(new Color(218, 165, 32)); pincel.drawRoundRect(xBotao, yBotoes[i], 350, 60, 15, 15);

                        int xTxt = xBotao + (350 - pincel.getFontMetrics().stringWidth(textosBotoes[i])) / 2;
                        pincel.setColor(i == 0 ? Color.WHITE : new Color(220, 220, 220));
                        pincel.drawString(textosBotoes[i], xTxt, yBotoes[i] + 36);
                    }
                }
                else if (estadoAtual == TELA_JOGO || estadoAtual == TELA_FIM) {

                    int largLog = 320;
                    int aTab = lTela - largLog;
                    int tTab = Math.min(aTab, aTela) - 120;
                    int tQuad = tTab / 8;
                    int mEsq = (aTab - (tQuad * 8)) / 2;
                    int mTop = (aTela - (tQuad * 8)) / 2;

                    int borda = 40;
                    pincel.setColor(new Color(0, 0, 0, 150)); pincel.fillRoundRect(mEsq - borda + 10, mTop - borda + 10, (tQuad * 8) + (borda * 2), (tQuad * 8) + (borda * 2), 20, 20);
                    pincel.setColor(new Color(70, 35, 15)); pincel.fillRoundRect(mEsq - borda, mTop - borda, (tQuad * 8) + (borda * 2), (tQuad * 8) + (borda * 2), 20, 20);
                    pincel.setColor(new Color(30, 15, 5)); pincel.drawRect(mEsq - 2, mTop - 2, (tQuad * 8) + 4, (tQuad * 8) + 4);

                    for (int l = 0; l < 8; l++) {
                        for (int c = 0; c < 8; c++) {
                            int pX = mEsq + (c * tQuad); int pY = mTop + (l * tQuad);
                            pincel.setColor((l + c) % 2 != 0 ? new Color(120, 70, 40) : new Color(245, 222, 179));
                            pincel.fillRect(pX, pY, tQuad, tQuad);

                            int conteudo = memoriaTabuleiro[l][c];
                            if (conteudo != 0) {
                                int margem = tQuad / 8; int tPeca = tQuad - (margem * 2);
                                pX += margem; pY += margem;

                                if (estadoAtual != TELA_FIM && (modoDeJogo != 2 || turnoAtual != 1)) {
                                    if (modoCombo && l == linhaCombo && c == colunaCombo) {
                                        pincel.setColor(new Color(255, 140, 0, 120)); pincel.fillOval(pX - 8, pY - 8, tPeca + 16, tPeca + 16);
                                    } else if (!modoCombo && (conteudo == turnoAtual || conteudo == turnoAtual + 2)) {
                                        pincel.setColor(new Color(57, 255, 20, 80)); pincel.fillOval(pX - 8, pY - 8, tPeca + 16, tPeca + 16);
                                    }
                                }
                                pintarPeca(pincel, conteudo, pX, pY, tPeca);
                            }
                        }
                    }

                    pincel.setColor(new Color(218, 165, 32)); pincel.setFont(new Font("Monospaced", Font.BOLD, 18));
                    for (int i = 0; i < 8; i++) {
                        String num = String.valueOf(8 - i);
                        int yTxt = mTop + (i * tQuad) + (tQuad / 2) + 6;
                        pincel.drawString(num, mEsq - 25, yTxt); pincel.drawString(num, mEsq + (8 * tQuad) + 10, yTxt);
                        int xTxt = mEsq + (i * tQuad) + (tQuad / 2) - 6;
                        pincel.drawString(COLUNAS[i], xTxt, mTop - 12); pincel.drawString(COLUNAS[i], xTxt, mTop + (8 * tQuad) + 25);
                    }

                    if (pecaSendoArrastada != 0) {
                        int tPeca = tQuad - ((tQuad / 8) * 2);
                        int pX = mouseX - (tPeca / 2), pY = mouseY - (tPeca / 2);
                        pincel.setColor(new Color(0, 0, 0, 100)); pincel.fillOval(pX + 12, pY + 12, tPeca, tPeca);
                        pintarPeca(pincel, pecaSendoArrastada, pX, pY, tPeca);
                    }

                    if (animandoIA) {
                        int margem = tQuad / 8; int tPeca = tQuad - (margem * 2);
                        int pOrigX = mEsq + (animOrigemC * tQuad) + margem, pOrigY = mTop + (animOrigemL * tQuad) + margem;
                        int pDestX = mEsq + (animDestinoC * tQuad) + margem, pDestY = mTop + (animDestinoL * tQuad) + margem;

                        int pX = (int) (pOrigX + (pDestX - pOrigX) * progressoAnimacao);
                        int pY = (int) (pOrigY + (pDestY - pOrigY) * progressoAnimacao);
                        int salto = (int) (Math.sin(progressoAnimacao * Math.PI) * 25);

                        pincel.setColor(new Color(0, 0, 0, 100)); pincel.fillOval(pX + 12, pY + 12, tPeca, tPeca);
                        pintarPeca(pincel, animPeca, pX, pY - salto, tPeca);
                    }

                    int xLog = lTela - largLog + 10;
                    pincel.setColor(new Color(15, 5, 0, 220)); pincel.fillRoundRect(xLog, mTop - borda, largLog - 30, (tQuad * 8) + (borda * 2), 15, 15);
                    pincel.setColor(new Color(218, 165, 32)); pincel.drawRoundRect(xLog, mTop - borda, largLog - 30, (tQuad * 8) + (borda * 2), 15, 15);
                    pincel.setFont(new Font("Monospaced", Font.BOLD, 16)); pincel.drawString("CÉREBRO DA IA", xLog + 80, mTop - borda + 30);
                    pincel.drawLine(xLog + 10, mTop - borda + 40, xLog + largLog - 40, mTop - borda + 40);
                    pincel.setFont(new Font("Monospaced", Font.PLAIN, 12)); pincel.setColor(new Color(150, 200, 150));
                    int lLogY = mTop - borda + 65;
                    for (String msg : logPensamentos) { pincel.drawString(msg, xLog + 15, lLogY); lLogY += 20; }

                    if (estadoAtual == TELA_FIM) {
                        pincel.setColor(new Color(0, 0, 0, 200));
                        pincel.fillRect(0, 0, lTela, aTela);

                        pincel.setFont(new Font("Serif", Font.BOLD, 55));
                        int xMsg = (lTela - pincel.getFontMetrics().stringWidth(mensagemFim)) / 2;

                        if (mensagemFim.contains("DERROTA")) {
                            pincel.setPaint(new GradientPaint(0, aTela/2 - 50, Color.RED, 0, aTela/2, new Color(139, 0, 0)));
                        } else {
                            pincel.setPaint(new GradientPaint(0, aTela/2 - 50, new Color(255, 215, 0), 0, aTela/2, new Color(184, 134, 11)));
                        }
                        pincel.drawString(mensagemFim, xMsg, aTela / 2);

                        int largBotaoFim = 300, altBotaoFim = 50;
                        int xBotaoFim = (lTela - largBotaoFim) / 2;
                        int yBotaoFim = (aTela / 2) + 60;

                        pincel.setColor(new Color(0, 0, 0, 150)); pincel.fillRoundRect(xBotaoFim + 5, yBotaoFim + 5, largBotaoFim, altBotaoFim, 15, 15);
                        pincel.setPaint(new GradientPaint(0, yBotaoFim, new Color(90, 50, 25), 0, yBotaoFim + altBotaoFim, new Color(50, 25, 10)));
                        pincel.fillRoundRect(xBotaoFim, yBotaoFim, largBotaoFim, altBotaoFim, 15, 15);
                        pincel.setColor(new Color(218, 165, 32)); pincel.drawRoundRect(xBotaoFim, yBotaoFim, largBotaoFim, altBotaoFim, 15, 15);

                        pincel.setFont(new Font("SansSerif", Font.BOLD, 18));
                        pincel.setColor(Color.WHITE);
                        String txtFim = "VOLTAR AO MENU";
                        pincel.drawString(txtFim, xBotaoFim + (largBotaoFim - pincel.getFontMetrics().stringWidth(txtFim)) / 2, yBotaoFim + 32);
                    }
                }
            }
        };

        MouseAdapter ouvinteDoMouse = new MouseAdapter() {
            @Override
            public void mousePressed(MouseEvent evento) {
                int cX = evento.getX(); int cY = evento.getY();

                if (estadoAtual == TELA_MENU) {
                    int[] yBotoes = {250, 330, 410, 490};
                    int xBotao = (telaDoJogo.getWidth() - 350) / 2;

                    for (int i = 0; i < 4; i++) {
                        if (cX >= xBotao && cX <= xBotao + 350 && cY >= yBotoes[i] && cY <= yBotoes[i] + 60) {
                            if (i == 0) modoDeJogo = 1;
                            else { modoDeJogo = 2; dificuldadeIA = i; }
                            iniciarNovaPartida();
                            estadoAtual = TELA_JOGO;
                            telaDoJogo.repaint();
                            return;
                        }
                    }
                }
                else if (estadoAtual == TELA_FIM) {
                    int lTela = telaDoJogo.getWidth(), aTela = telaDoJogo.getHeight();
                    int xB = (lTela - 300) / 2, yB = (aTela / 2) + 60;
                    if (cX >= xB && cX <= xB + 300 && cY >= yB && cY <= yB + 50) {
                        estadoAtual = TELA_MENU;
                        telaDoJogo.repaint();
                    }
                }
                else if (estadoAtual == TELA_JOGO) {
                    if ((modoDeJogo == 2 && turnoAtual == 1) || animandoIA) return;

                    int largLog = 320; int aTab = telaDoJogo.getWidth() - largLog;
                    int tQuad = (Math.min(aTab, telaDoJogo.getHeight()) - 120) / 8;
                    int mEsq = (aTab - (tQuad * 8)) / 2, mTop = (telaDoJogo.getHeight() - (tQuad * 8)) / 2;

                    if (cX >= mEsq && cX <= mEsq + (tQuad * 8) && cY >= mTop && cY <= mTop + (tQuad * 8)) {
                        int col = (cX - mEsq) / tQuad, lin = (cY - mTop) / tQuad;
                        int pecaNoChao = memoriaTabuleiro[lin][col];

                        if (pecaNoChao == turnoAtual || pecaNoChao == turnoAtual + 2) {
                            if (modoCombo && (lin != linhaCombo || col != colunaCombo)) return;
                            pecaSendoArrastada = pecaNoChao;
                            linhaDeOrigem = lin; colunaDeOrigem = col;
                            memoriaTabuleiro[lin][col] = 0;
                            mouseX = cX; mouseY = cY;
                            telaDoJogo.repaint();
                        }
                    }
                }
            }

            @Override
            public void mouseDragged(MouseEvent evento) {
                if (estadoAtual == TELA_JOGO && pecaSendoArrastada != 0 && !animandoIA) {
                    mouseX = evento.getX(); mouseY = evento.getY();
                    telaDoJogo.repaint();
                }
            }

            @Override
            public void mouseReleased(MouseEvent evento) {
                if (estadoAtual == TELA_JOGO && pecaSendoArrastada != 0 && !animandoIA) {
                    int largLog = 320; int aTab = telaDoJogo.getWidth() - largLog;
                    int tQuad = (Math.min(aTab, telaDoJogo.getHeight()) - 120) / 8;
                    int mEsq = (aTab - (tQuad * 8)) / 2, mTop = (telaDoJogo.getHeight() - (tQuad * 8)) / 2;
                    int cX = evento.getX(), cY = evento.getY();

                    boolean jogadaValida = false, teveCaptura = false;
                    int linCap = -1, colCap = -1;

                    if (cX >= mEsq && cX <= mEsq + (tQuad * 8) && cY >= mTop && cY <= mTop + (tQuad * 8)) {
                        int colAlvo = (cX - mEsq) / tQuad, linAlvo = (cY - mTop) / tQuad;

                        boolean isCasaEscura = (linAlvo + colAlvo) % 2 != 0;
                        boolean isCasaVazia = memoriaTabuleiro[linAlvo][colAlvo] == 0;
                        boolean isDistCorreta = false;

                        int distCol = Math.abs(colAlvo - colunaDeOrigem);
                        int distLinha = Math.abs(linAlvo - linhaDeOrigem);

                        if (pecaSendoArrastada == 1 || pecaSendoArrastada == 2) {
                            if (distCol == 1 && !modoCombo) {
                                if (pecaSendoArrastada == 1 && linAlvo - linhaDeOrigem == 1) isDistCorreta = true;
                                else if (pecaSendoArrastada == 2 && linhaDeOrigem - linAlvo == 1) isDistCorreta = true;
                            }
                            else if (distCol == 2 && distLinha == 2) {
                                int lMeio = (linhaDeOrigem + linAlvo) / 2, cMeio = (colunaDeOrigem + colAlvo) / 2;
                                int pMeio = memoriaTabuleiro[lMeio][cMeio];
                                if (pecaSendoArrastada == 1 && (pMeio == 2 || pMeio == 4)) { isDistCorreta = true; teveCaptura = true; linCap = lMeio; colCap = cMeio; }
                                else if (pecaSendoArrastada == 2 && (pMeio == 1 || pMeio == 3)) { isDistCorreta = true; teveCaptura = true; linCap = lMeio; colCap = cMeio; }
                            }
                        }
                        else if (pecaSendoArrastada == 3 || pecaSendoArrastada == 4) {
                            if (distCol == distLinha && distCol > 0) {
                                int dirLinha = (linAlvo - linhaDeOrigem) / distLinha, dirCol = (colAlvo - colunaDeOrigem) / distCol;
                                int pecasNoCaminho = 0, inimigoAchadoL = -1, inimigoAchadoC = -1;

                                for (int i = 1; i < distCol; i++) {
                                    int lAtual = linhaDeOrigem + (i * dirLinha), cAtual = colunaDeOrigem + (i * dirCol);
                                    if (memoriaTabuleiro[lAtual][cAtual] != 0) {
                                        pecasNoCaminho++; inimigoAchadoL = lAtual; inimigoAchadoC = cAtual;
                                    }
                                }

                                if (pecasNoCaminho == 0 && !modoCombo) isDistCorreta = true;
                                else if (pecasNoCaminho == 1) {
                                    int pCaminho = memoriaTabuleiro[inimigoAchadoL][inimigoAchadoC];
                                    boolean inimigoValido = (pecaSendoArrastada == 3 && (pCaminho == 2 || pCaminho == 4)) || (pecaSendoArrastada == 4 && (pCaminho == 1 || pCaminho == 3));
                                    if (inimigoValido) { isDistCorreta = true; teveCaptura = true; linCap = inimigoAchadoL; colCap = inimigoAchadoC; }
                                }
                            }
                        }

                        if (isCasaEscura && isCasaVazia && isDistCorreta) {
                            if (pecaSendoArrastada == 1 && linAlvo == 7) pecaSendoArrastada = 3;
                            if (pecaSendoArrastada == 2 && linAlvo == 0) pecaSendoArrastada = 4;

                            memoriaTabuleiro[linAlvo][colAlvo] = pecaSendoArrastada;
                            jogadaValida = true;

                            adicionarLog("Você: " + COLUNAS[colunaDeOrigem] + (8 - linhaDeOrigem) + "->" + COLUNAS[colAlvo] + (8 - linAlvo));

                            if (teveCaptura) {
                                memoriaTabuleiro[linCap][colCap] = 0;
                                boolean isPreta = (pecaSendoArrastada == 1 || pecaSendoArrastada == 3);
                                int inNormal = isPreta ? 2 : 1, inDama = isPreta ? 4 : 3;
                                boolean temMaisCaptura = false;

                                int[][] dirs = {{-1, -1}, {-1, 1}, {1, -1}, {1, 1}};
                                for (int i = 0; i < 4; i++) {
                                    int lDest = linAlvo + (dirs[i][0] * 2), cDest = colAlvo + (dirs[i][1] * 2);
                                    if (lDest >= 0 && lDest < 8 && cDest >= 0 && cDest < 8) {
                                        int pMeio = memoriaTabuleiro[linAlvo + dirs[i][0]][colAlvo + dirs[i][1]];
                                        if ((pMeio == inNormal || pMeio == inDama) && memoriaTabuleiro[lDest][cDest] == 0) { temMaisCaptura = true; break; }
                                    }
                                }

                                if (temMaisCaptura) {
                                    modoCombo = true; linhaCombo = linAlvo; colunaCombo = colAlvo;
                                    adicionarLog(">> OBRIGATÓRIO COMBAR!");
                                } else {
                                    modoCombo = false; turnoAtual = (turnoAtual == 2) ? 1 : 2;
                                }
                            } else {
                                turnoAtual = (turnoAtual == 2) ? 1 : 2;
                            }
                        }
                    }

                    if (!jogadaValida) memoriaTabuleiro[linhaDeOrigem][colunaDeOrigem] = pecaSendoArrastada;
                    pecaSendoArrastada = 0;

                    verificarFimDeJogo();
                    telaDoJogo.repaint();

                    if (jogadaValida && modoDeJogo == 2 && turnoAtual == 1 && estadoAtual != TELA_FIM) {
                        acionarIA();
                    }
                }
            }
        };

        telaDoJogo.addMouseListener(ouvinteDoMouse);
        telaDoJogo.addMouseMotionListener(ouvinteDoMouse);

        janela.add(telaDoJogo);
        janela.setVisible(true);
    }
}