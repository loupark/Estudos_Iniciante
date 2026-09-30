import arcade
import arcade.gui
import os
import random
import math

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# =====================================================================
# --- CARREGAMENTO DA FONTE CUSTOMIZADA GLOBAL ---
# =====================================================================
NOME_FONTE = "Black Clover Font"
try:
    caminho_fonte = os.path.join(DIRETORIO_ATUAL, "assets", "fonte.ttf")
    arcade.load_font(caminho_fonte)
    print("Sucesso: Fonte Black Clover carregada!")
except Exception as e:
    print("Aviso: Ficheiro fonte.ttf não encontrado.", e)

FONTES_JOGO = (NOME_FONTE, "Bookman Old Style", "Georgia", "serif")

# =====================================================================
# --- ZOOM GERAL DO JOGO ---
# =====================================================================
MULTIPLICADOR_GLOBAL = 1.25

LARGURA_TELA = int(800 * MULTIPLICADOR_GLOBAL)
ALTURA_TELA = int(800 * MULTIPLICADOR_GLOBAL)
TITULO_TELA = "Xadrez Stardew Valley"
COR_FUNDO = (30, 35, 40)

TAMANHO_CASA = 89.5 * MULTIPLICADOR_GLOBAL
INICIO_X = 42 * MULTIPLICADOR_GLOBAL
INICIO_Y = 25 * MULTIPLICADOR_GLOBAL
DESLOCAMENTO_Y_PECA = 20 * MULTIPLICADOR_GLOBAL
ESCALA_PECA = 0.15 * MULTIPLICADOR_GLOBAL

CONFIGURACOES_JOGO = {
    "volume_sfx": 1.0,
    "volume_musica": 0.3,
    "modo_ia": False,
    "dificuldade_ia": "Fácil",
    "tela_cheia": False,
    "cor_jogador": "branco",
}

# --- ESTILOS DE BOTÕES ---
ESTILO_MADEIRA = {
    "normal": {
        "font_name": FONTES_JOGO,
        "font_size": 22,
        "font_color": (255, 230, 180),
        "border_width": 4,
        "border_color": (50, 25, 15),
        "bg_color": (101, 58, 20),
    },
    "hover": {
        "font_name": FONTES_JOGO,
        "font_size": 22,
        "font_color": (255, 255, 255),
        "border_width": 4,
        "border_color": (255, 215, 0),
        "bg_color": (122, 78, 30),
    },
    "press": {
        "font_name": FONTES_JOGO,
        "font_size": 22,
        "font_color": (255, 255, 255),
        "border_width": 4,
        "border_color": (255, 215, 0),
        "bg_color": (50, 25, 15),
    },
}

ESTILO_ENGRENAGEM = {
    "normal": {
        "font_name": ("Arial",),
        "font_size": 18,
        "font_color": (255, 230, 180),
        "border_width": 2,
        "border_color": (50, 25, 15),
        "bg_color": (101, 58, 20),
    },
    "hover": {
        "font_name": ("Arial",),
        "font_size": 18,
        "font_color": (255, 255, 255),
        "border_width": 2,
        "border_color": (255, 215, 0),
        "bg_color": (122, 78, 30),
    },
    "press": {
        "font_name": ("Arial",),
        "font_size": 18,
        "font_color": (255, 255, 255),
        "border_width": 2,
        "border_color": (255, 215, 0),
        "bg_color": (50, 25, 15),
    },
}


# =====================================================================
# --- A JANELA PRINCIPAL (SISTEMA DE MÚSICA INTELIGENTE) ---
# =====================================================================
class JanelaPrincipal(arcade.Window):
    def __init__(self, largura, altura, titulo, resizable):
        super().__init__(largura, altura, titulo, resizable=resizable)
        self.media_player = None
        self.musica = None

        caminho_wav = os.path.join(DIRETORIO_ATUAL, "assets", "musica_fundo.wav")
        caminho_mp3 = os.path.join(DIRETORIO_ATUAL, "assets", "musica_fundo.mp3")

        caminho_escolhido = None

        if os.path.exists(caminho_wav):
            caminho_escolhido = caminho_wav
            print("Musica .WAV encontrada!")
        elif os.path.exists(caminho_mp3):
            caminho_escolhido = caminho_mp3
            print("Musica .MP3 encontrada! (Se não tocar, converta para .WAV)")
        else:
            print(
                "Nenhuma música de fundo (musica_fundo.wav ou musica_fundo.mp3) encontrada."
            )

        if caminho_escolhido:
            try:
                self.musica = arcade.load_sound(caminho_escolhido)
                vol = CONFIGURACOES_JOGO["volume_musica"]
                if vol > 0:
                    # CORREÇÃO AQUI: loop=True em vez de looping=True
                    self.media_player = arcade.play_sound(
                        self.musica, volume=vol, loop=True
                    )
            except Exception as e:
                print(
                    f"\n[ERRO CRÍTICO DE ÁUDIO] O Python não conseguiu decodificar o arquivo musical:\n{e}"
                )
                print(
                    ">>> DICA: Vá num site como o Convertio.co, transforme seu MP3 para WAV e tente novamente!\n"
                )

    def atualizar_volume_musica(self):
        """Ajusta o volume da música em tempo real baseado no slider."""
        vol = CONFIGURACOES_JOGO["volume_musica"]
        if self.media_player:
            self.media_player.volume = vol
            if vol == 0 and self.media_player.playing:
                self.media_player.pause()
            elif vol > 0 and not self.media_player.playing:
                self.media_player.play()
        elif vol > 0 and self.musica:
            # CORREÇÃO AQUI TAMBÉM: loop=True
            self.media_player = arcade.play_sound(self.musica, volume=vol, loop=True)


# =====================================================================
# --- CLASSES DAS PEÇAS ---
# =====================================================================
class Peca(arcade.Sprite):
    def __init__(
        self, imagem_path, cor, linha, coluna, escala=1.0, ajuste_x=0, ajuste_y=0
    ):
        super().__init__(imagem_path, scale=escala)
        self.cor = cor
        self.linha = linha
        self.coluna = coluna
        self.linha_original = linha
        self.coluna_original = coluna
        self.ajuste_x = ajuste_x
        self.ajuste_y = ajuste_y
        self.destino_x = 0
        self.destino_y = 0
        self.ja_moveu = False
        self.atualizar_posicao_tela(instantaneo=True)

    def atualizar_posicao_tela(self, instantaneo=False):
        janela = arcade.get_window()
        offset_x = (janela.width - LARGURA_TELA) // 2
        offset_y = (janela.height - ALTURA_TELA) // 2
        linha_v = (
            self.linha
            if CONFIGURACOES_JOGO["cor_jogador"] == "branco"
            else 7 - self.linha
        )
        coluna_v = (
            self.coluna
            if CONFIGURACOES_JOGO["cor_jogador"] == "branco"
            else 7 - self.coluna
        )
        self.destino_x = (
            offset_x
            + INICIO_X
            + (coluna_v * TAMANHO_CASA)
            + (TAMANHO_CASA // 2)
            + self.ajuste_x
        )
        self.destino_y = (
            offset_y
            + INICIO_Y
            + (linha_v * TAMANHO_CASA)
            + (TAMANHO_CASA // 2)
            + DESLOCAMENTO_Y_PECA
            + self.ajuste_y
        )
        if instantaneo:
            self.center_x = self.destino_x
            self.center_y = self.destino_y

    def update(self, *args, **kwargs):
        suavidade = 0.25
        if (
            abs(self.center_x - self.destino_x) > 0.5
            or abs(self.center_y - self.destino_y) > 0.5
        ):
            self.center_x += (self.destino_x - self.center_x) * suavidade
            self.center_y += (self.destino_y - self.center_y) * suavidade
        else:
            self.center_x = self.destino_x
            self.center_y = self.destino_y

    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        return []


class Peao(Peca):
    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        movimentos = []
        direcao = 1 if self.cor == "branco" else -1
        linha_inicial = 1 if self.cor == "branco" else 6
        nova_linha = self.linha + direcao
        if 0 <= nova_linha <= 7:
            if matriz[nova_linha][self.coluna] is None:
                movimentos.append((nova_linha, self.coluna))
                if (
                    self.linha == linha_inicial
                    and matriz[self.linha + (direcao * 2)][self.coluna] is None
                ):
                    movimentos.append((self.linha + (direcao * 2), self.coluna))
            for deslocamento_coluna in [-1, 1]:
                nova_coluna = self.coluna + deslocamento_coluna
                if 0 <= nova_coluna <= 7:
                    peca_alvo = matriz[nova_linha][nova_coluna]
                    if peca_alvo is not None and peca_alvo.cor != self.cor:
                        movimentos.append((nova_linha, nova_coluna))
                    elif ultimo_mov_peao and ultimo_mov_peao.cor != self.cor:
                        if self.linha == (4 if self.cor == "branco" else 3):
                            if (
                                ultimo_mov_peao.linha == self.linha
                                and ultimo_mov_peao.coluna == nova_coluna
                            ):
                                movimentos.append((nova_linha, nova_coluna))
        return movimentos


class Cavalo(Peca):
    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        movimentos = []
        saltos = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ]
        for sl, sc in saltos:
            nl, nc = self.linha + sl, self.coluna + sc
            if 0 <= nl <= 7 and 0 <= nc <= 7:
                peca_alvo = matriz[nl][nc]
                if peca_alvo is None or peca_alvo.cor != self.cor:
                    movimentos.append((nl, nc))
        return movimentos


class Torre(Peca):
    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        movimentos = []
        direcoes = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dl, dc in direcoes:
            for passo in range(1, 8):
                nl, nc = self.linha + (dl * passo), self.coluna + (dc * passo)
                if 0 <= nl <= 7 and 0 <= nc <= 7:
                    peca_alvo = matriz[nl][nc]
                    if peca_alvo is None:
                        movimentos.append((nl, nc))
                    elif peca_alvo.cor != self.cor:
                        movimentos.append((nl, nc))
                        break
                    else:
                        break
                else:
                    break
        return movimentos


class Bispo(Peca):
    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        movimentos = []
        direcoes = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dl, dc in direcoes:
            for passo in range(1, 8):
                nl, nc = self.linha + (dl * passo), self.coluna + (dc * passo)
                if 0 <= nl <= 7 and 0 <= nc <= 7:
                    peca_alvo = matriz[nl][nc]
                    if peca_alvo is None:
                        movimentos.append((nl, nc))
                    elif peca_alvo.cor != self.cor:
                        movimentos.append((nl, nc))
                        break
                    else:
                        break
                else:
                    break
        return movimentos


class Rainha(Peca):
    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        movimentos = []
        direcoes = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        for dl, dc in direcoes:
            for passo in range(1, 8):
                nl, nc = self.linha + (dl * passo), self.coluna + (dc * passo)
                if 0 <= nl <= 7 and 0 <= nc <= 7:
                    peca_alvo = matriz[nl][nc]
                    if peca_alvo is None:
                        movimentos.append((nl, nc))
                    elif peca_alvo.cor != self.cor:
                        movimentos.append((nl, nc))
                        break
                    else:
                        break
                else:
                    break
        return movimentos


class Rei(Peca):
    def movimentos_validos(self, matriz, ultimo_mov_peao=None):
        movimentos = []
        direcoes = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        for dl, dc in direcoes:
            nl, nc = self.linha + dl, self.coluna + dc
            if 0 <= nl <= 7 and 0 <= nc <= 7:
                peca_alvo = matriz[nl][nc]
                if peca_alvo is None or peca_alvo.cor != self.cor:
                    movimentos.append((nl, nc))
        if not self.ja_moveu:
            if matriz[self.linha][5] is None and matriz[self.linha][6] is None:
                torre = matriz[self.linha][7]
                if isinstance(torre, Torre) and not torre.ja_moveu:
                    movimentos.append((self.linha, self.coluna + 2))
            if (
                matriz[self.linha][1] is None
                and matriz[self.linha][2] is None
                and matriz[self.linha][3] is None
            ):
                torre = matriz[self.linha][0]
                if isinstance(torre, Torre) and not torre.ja_moveu:
                    movimentos.append((self.linha, self.coluna - 2))
        return movimentos


CONFIG_PECAS = {
    "peao_branco": {
        "img": "peao_branco.png",
        "cor": "branco",
        "classe": Peao,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "peao_preto": {
        "img": "peao_preto.png",
        "cor": "preto",
        "classe": Peao,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "cavalo_branco": {
        "img": "cavalo_branco.png",
        "cor": "branco",
        "classe": Cavalo,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "cavalo_preto": {
        "img": "cavalo_preto.png",
        "cor": "preto",
        "classe": Cavalo,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "torre_branco": {
        "img": "torre_branco.png",
        "cor": "branco",
        "classe": Torre,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "torre_preto": {
        "img": "torre_preto.png",
        "cor": "preto",
        "classe": Torre,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "bispo_branco": {
        "img": "bispo_branco.png",
        "cor": "branco",
        "classe": Bispo,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "bispo_preto": {
        "img": "bispo_preto.png",
        "cor": "preto",
        "classe": Bispo,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "rainha_branco": {
        "img": "rainha_branco.png",
        "cor": "branco",
        "classe": Rainha,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "rainha_preto": {
        "img": "rainha_preto.png",
        "cor": "preto",
        "classe": Rainha,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "rei_branco": {
        "img": "rei_branco.png",
        "cor": "branco",
        "classe": Rei,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
    "rei_preto": {
        "img": "rei_preto.png",
        "cor": "preto",
        "classe": Rei,
        "ajuste_x": 0,
        "ajuste_y": 0,
        "escala": ESCALA_PECA,
    },
}


# =====================================================================
# --- A TELA DO JOGO ---
# =====================================================================
class JogoXadrez(arcade.View):
    def __init__(self):
        super().__init__()
        self.turno_atual = "branco"
        self.matriz_tabuleiro = [[None for _ in range(8)] for _ in range(8)]
        self.tempo_espera_ia = 0.0
        self.lista_impactos = []
        self.ultimo_mov_peao = None

        self.jogo_acabou = False
        self.mensagem_tela = ""
        self.tempo_mensagem = 0.0
        self.menu_fim_criado = False

        self.aguardando_promocao = False
        self.peao_em_promocao = None

        self.mensagem_sistema = ""
        self.tempo_mensagem_sistema = 0.0
        self.cor_mensagem_sistema = "branco"

        self.manager = arcade.gui.UIManager()
        self.restaurar_interface_padrao()

        try:
            self.som_mover = arcade.load_sound(
                os.path.join(DIRETORIO_ATUAL, "assets", "som_mover.wav")
            )
            self.som_captura = arcade.load_sound(
                os.path.join(DIRETORIO_ATUAL, "assets", "som_captura.wav")
            )
        except Exception:
            self.som_mover = None
            self.som_captura = None

        self.lista_fundo = arcade.SpriteList()
        try:
            caminho_tabuleiro = os.path.join(DIRETORIO_ATUAL, "assets", "tabuleiro.png")
            escala_tabuleiro = LARGURA_TELA / 3100
            self.tabuleiro_sprite = arcade.Sprite(
                caminho_tabuleiro, scale=escala_tabuleiro
            )
            self.lista_fundo.append(self.tabuleiro_sprite)
        except Exception:
            pass

        self.lista_pecas = arcade.SpriteList()
        self.pecas_capturadas = arcade.SpriteList()
        self.peca_segurada = None
        self.configurar_pecas_iniciais()

    def restaurar_interface_padrao(self):
        self.manager.clear()
        self.btn_engrenagem = arcade.gui.UIFlatButton(
            text="⚙️", width=38, height=38, style=ESTILO_ENGRENAGEM
        )

        @self.btn_engrenagem.event("on_click")
        def on_click_engrenagem(event):
            opcoes = MenuOpcoes(jogo_em_andamento=self)
            self.window.show_view(opcoes)

        ancora = arcade.gui.UIAnchorLayout()
        ancora.add(
            child=self.btn_engrenagem,
            anchor_x="right",
            anchor_y="top",
            align_x=-15,
            align_y=-15,
        )
        self.manager.add(ancora)

    def configurar_pecas_iniciais(self):
        def criar_e_adicionar(tipo_peca, linen, col):
            config = CONFIG_PECAS[tipo_peca]
            caminho_imagem = os.path.join(DIRETORIO_ATUAL, "assets", config["img"])
            try:
                peca = config["classe"](
                    caminho_imagem,
                    config["cor"],
                    linen,
                    col,
                    config["escala"],
                    config["ajuste_x"],
                    config["ajuste_y"],
                )
                self.lista_pecas.append(peca)
                self.matriz_tabuleiro[linen][col] = peca
            except Exception:
                pass

        for coluna in range(8):
            criar_e_adicionar("peao_branco", 1, coluna)
            criar_e_adicionar("peao_preto", 6, coluna)

        for peca, linha in [
            ("torre", 0),
            ("cavalo", 1),
            ("bispo", 2),
            ("rainha", 3),
            ("rei", 4),
            ("bispo", 5),
            ("cavalo", 6),
            ("torre", 7),
        ]:
            criar_e_adicionar(f"{peca}_branco", 0, linha)
            criar_e_adicionar(f"{peca}_preto", 7, linha)

        self.atualizar_estado_partida()

    def on_show_view(self):
        arcade.set_background_color(COR_FUNDO)
        self.manager.enable()
        self.on_resize(self.window.width, self.window.height)

    def on_hide_view(self):
        self.manager.disable()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        offset_x = (width - LARGURA_TELA) // 2
        offset_y = (height - ALTURA_TELA) // 2

        if hasattr(self, "tabuleiro_sprite"):
            self.tabuleiro_sprite.center_x = (LARGURA_TELA // 2) + offset_x
            self.tabuleiro_sprite.center_y = (ALTURA_TELA // 2) + offset_y

        if hasattr(self, "lista_pecas"):
            for peca in self.lista_pecas:
                peca.atualizar_posicao_tela(instantaneo=True)

        if (
            not self.jogo_acabou
            and not self.aguardando_promocao
            and hasattr(self, "manager")
        ):
            self.restaurar_interface_padrao()

    def criar_efeito_impacto(self, x, y):
        self.lista_impactos.append(
            {
                "tipo": "anel",
                "x": x,
                "y": y,
                "raio": 4 * MULTIPLICADOR_GLOBAL,
                "alpha": 200,
                "espessura": 3,
            }
        )
        for _ in range(random.randint(6, 10)):
            angulo = random.uniform(0, math.pi * 2)
            velocidade = random.uniform(1.0, 3.0) * MULTIPLICADOR_GLOBAL
            self.lista_impactos.append(
                {
                    "tipo": "particula",
                    "x": x,
                    "y": y,
                    "dx": math.cos(angulo) * velocidade,
                    "dy": math.sin(angulo) * velocidade,
                    "raio": random.uniform(1.5, 3.5) * MULTIPLICADOR_GLOBAL,
                    "alpha": 255,
                }
            )

    def promover_peca(self, peca, tipo_escolhido):
        self.lista_pecas.remove(peca)
        classes = {"rainha": Rainha, "torre": Torre, "bispo": Bispo, "cavalo": Cavalo}
        classe = classes[tipo_escolhido]
        img = f"{tipo_escolhido}_{peca.cor}.png"
        caminho = os.path.join(DIRETORIO_ATUAL, "assets", img)
        nova_peca = classe(
            caminho, peca.cor, peca.linha, peca.coluna, escala=ESCALA_PECA
        )
        nova_peca.ja_moveu = True
        nova_peca.atualizar_posicao_tela(instantaneo=True)
        self.lista_pecas.append(nova_peca)
        self.matriz_tabuleiro[peca.linha][peca.coluna] = nova_peca

    def esta_em_xeque(self, cor):
        linha_rei, coluna_rei = -1, -1
        for l in range(8):
            for c in range(8):
                p = self.matriz_tabuleiro[l][c]
                if p and p.cor == cor and isinstance(p, Rei):
                    linha_rei, coluna_rei = l, c
                    break
        for l in range(8):
            for c in range(8):
                p = self.matriz_tabuleiro[l][c]
                if p and p.cor != cor:
                    if (linha_rei, coluna_rei) in p.movimentos_validos(
                        self.matriz_tabuleiro, None
                    ):
                        return True
        return False

    def obter_movimentos_seguros(self, peca):
        movimentos_brutos = peca.movimentos_validos(
            self.matriz_tabuleiro, self.ultimo_mov_peao
        )
        movimentos_seguros = []
        linha_orig, coluna_orig = peca.linha, peca.coluna

        for l, c in movimentos_brutos:
            if isinstance(peca, Rei) and abs(c - coluna_orig) == 2:
                if self.esta_em_xeque(peca.cor):
                    continue
                passo_coluna = 1 if c > coluna_orig else -1
                self.matriz_tabuleiro[linha_orig][coluna_orig] = None
                self.matriz_tabuleiro[linha_orig][coluna_orig + passo_coluna] = peca
                peca.coluna = coluna_orig + passo_coluna
                em_xeque_passagem = self.esta_em_xeque(peca.cor)
                self.matriz_tabuleiro[linha_orig][coluna_orig + passo_coluna] = None
                self.matriz_tabuleiro[linha_orig][coluna_orig] = peca
                peca.coluna = coluna_orig
                if em_xeque_passagem:
                    continue

            peca_destino = self.matriz_tabuleiro[l][c]
            peao_en_passant_capt = None
            if isinstance(peca, Peao) and c != coluna_orig and peca_destino is None:
                peao_en_passant_capt = self.matriz_tabuleiro[linha_orig][c]
                self.matriz_tabuleiro[linha_orig][c] = None

            self.matriz_tabuleiro[linha_orig][coluna_orig] = None
            self.matriz_tabuleiro[l][c] = peca
            peca.linha, peca.coluna = l, c

            if not self.esta_em_xeque(peca.cor):
                movimentos_seguros.append((l, c))

            self.matriz_tabuleiro[linha_orig][coluna_orig] = peca
            self.matriz_tabuleiro[l][c] = peca_destino
            peca.linha, peca.coluna = linha_orig, coluna_orig
            if peao_en_passant_capt:
                self.matriz_tabuleiro[linha_orig][c] = peao_en_passant_capt

        return movimentos_seguros

    def mostrar_menu_promocao(self):
        self.manager.clear()
        v_box = arcade.gui.UIBoxLayout(space_between=10)
        titulo = arcade.gui.UILabel(
            text="Escolha a Promoção:",
            text_color=(255, 215, 0),
            font_size=28,
            font_name=FONTES_JOGO,
            bold=True,
        )
        v_box.add(titulo)
        v_box.add(arcade.gui.UIWidget(height=10))

        opcoes = [
            ("Rainha", "rainha"),
            ("Torre", "torre"),
            ("Bispo", "bispo"),
            ("Cavalo", "cavalo"),
        ]

        for texto, tipo in opcoes:
            btn = arcade.gui.UIFlatButton(
                text=texto, width=250, height=45, style=ESTILO_MADEIRA
            )
            v_box.add(btn)

            @btn.event("on_click")
            def on_click(event, t=tipo):
                self.promover_peca(self.peao_em_promocao, t)
                self.aguardando_promocao = False
                self.peao_em_promocao = None
                self.restaurar_interface_padrao()
                self.finalizar_turno()

        ancora = arcade.gui.UIAnchorLayout()
        ancora.add(child=v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(ancora)

    def mostrar_menu_fim_jogo(self):
        if self.menu_fim_criado:
            return
        self.menu_fim_criado = True
        self.manager.clear()

        v_box = arcade.gui.UIBoxLayout(space_between=15)
        btn_jogar = arcade.gui.UIFlatButton(
            text="Jogar Novamente", width=300, height=50, style=ESTILO_MADEIRA
        )
        btn_voltar = arcade.gui.UIFlatButton(
            text="Voltar à Taverna", width=300, height=50, style=ESTILO_MADEIRA
        )

        v_box.add(btn_jogar)
        v_box.add(btn_voltar)

        @btn_jogar.event("on_click")
        def on_click_jogar(event):
            novo_jogo = JogoXadrez()
            self.window.show_view(novo_jogo)

        @btn_voltar.event("on_click")
        def on_click_voltar(event):
            menu = MenuPrincipal()
            self.window.show_view(menu)

        ancora = arcade.gui.UIAnchorLayout()
        ancora.add(child=v_box, anchor_x="center_x", anchor_y="center_y", align_y=-120)
        self.manager.add(ancora)

    def finalizar_turno(self):
        self.turno_atual = "preto" if self.turno_atual == "branco" else "branco"
        self.atualizar_estado_partida()

    def atualizar_estado_partida(self):
        cor_analisada = self.turno_atual
        tem_salvacao = False
        roque_disp = False
        en_passant_disp = False

        for peca in self.lista_pecas:
            if peca.cor == cor_analisada:
                mov_seguros = self.obter_movimentos_seguros(peca)
                if len(mov_seguros) > 0:
                    tem_salvacao = True

                if isinstance(peca, Rei):
                    for l, c in mov_seguros:
                        if abs(c - peca.coluna) == 2:
                            roque_disp = True
                elif isinstance(peca, Peao):
                    for l, c in mov_seguros:
                        if c != peca.coluna and self.matriz_tabuleiro[l][c] is None:
                            en_passant_disp = True

        cor_ia = "preto" if CONFIGURACOES_JOGO["cor_jogador"] == "branco" else "branco"
        if not (CONFIGURACOES_JOGO["modo_ia"] and cor_analisada == cor_ia):
            msgs = []
            if roque_disp:
                msgs.append("Roque Liberado!")
            if en_passant_disp:
                msgs.append("En Passant Liberado!")

            if msgs:
                self.mensagem_sistema = " | ".join(msgs)
                self.tempo_mensagem_sistema = 4.0
                self.cor_mensagem_sistema = cor_analisada
            else:
                self.mensagem_sistema = ""
                self.tempo_mensagem_sistema = 0.0

        em_xeque = self.esta_em_xeque(cor_analisada)
        if not tem_salvacao:
            self.jogo_acabou = True
            self.mensagem_sistema = ""
            if em_xeque:
                cor_vencedora = "BRANCAS" if cor_analisada == "preto" else "PRETAS"
                self.mensagem_tela = f"Vitória das {cor_vencedora}!"
                self.tempo_mensagem = 999.0
            else:
                self.mensagem_tela = "EMPATE!"
                self.tempo_mensagem = 999.0
            self.mostrar_menu_fim_jogo()
        elif em_xeque:
            self.mensagem_tela = "XEQUE!"
            self.tempo_mensagem = 2.0

    def executar_movimento(self, peca, l, c):
        peca_capturada = self.matriz_tabuleiro[l][c]
        if (
            isinstance(peca, Peao)
            and c != peca.coluna_original
            and peca_capturada is None
        ):
            peca_capturada = self.matriz_tabuleiro[peca.linha_original][c]
            self.matriz_tabuleiro[peca.linha_original][c] = None

        if peca_capturada is not None:
            self.lista_pecas.remove(peca_capturada)
            self.pecas_capturadas.append(peca_capturada)
            if self.som_captura:
                arcade.play_sound(
                    self.som_captura, volume=CONFIGURACOES_JOGO["volume_sfx"]
                )
        else:
            if self.som_mover:
                arcade.play_sound(
                    self.som_mover, volume=CONFIGURACOES_JOGO["volume_sfx"]
                )

        if isinstance(peca, Rei) and abs(c - peca.coluna_original) == 2:
            torre_col_orig = 7 if c > peca.coluna_original else 0
            torre_col_nova = 5 if c > peca.coluna_original else 3
            torre = self.matriz_tabuleiro[l][torre_col_orig]
            self.matriz_tabuleiro[l][torre_col_orig] = None
            self.matriz_tabuleiro[l][torre_col_nova] = torre
            torre.coluna, torre.coluna_original = torre_col_nova, torre_col_nova
            torre.ja_moveu = True
            torre.atualizar_posicao_tela(instantaneo=False)

        self.ultimo_mov_peao = (
            peca
            if (isinstance(peca, Peao) and abs(l - peca.linha_original) == 2)
            else None
        )

        self.matriz_tabuleiro[peca.linha_original][peca.coluna_original] = None
        self.matriz_tabuleiro[l][c] = peca
        peca.coluna, peca.linha = c, l
        peca.coluna_original, peca.linha_original = c, l
        peca.ja_moveu = True

        peca.atualizar_posicao_tela(instantaneo=False)
        self.criar_efeito_impacto(peca.destino_x, peca.destino_y)

        if isinstance(peca, Peao) and (peca.linha == 0 or peca.linha == 7):
            cor_ia = (
                "preto" if CONFIGURACOES_JOGO["cor_jogador"] == "branco" else "branco"
            )
            if CONFIGURACOES_JOGO["modo_ia"] and peca.cor == cor_ia:
                self.promover_peca(peca, "rainha")
                self.finalizar_turno()
            else:
                self.aguardando_promocao = True
                self.peao_em_promocao = peca
                self.mostrar_menu_promocao()
        else:
            self.finalizar_turno()

    def on_update(self, delta_time):
        self.lista_pecas.update()

        if self.tempo_mensagem > 0 and not self.jogo_acabou:
            self.tempo_mensagem -= delta_time
            if self.tempo_mensagem <= 0:
                self.mensagem_tela = ""

        if self.tempo_mensagem_sistema > 0 and not self.jogo_acabou:
            self.tempo_mensagem_sistema -= delta_time
            if self.tempo_mensagem_sistema <= 0:
                self.mensagem_sistema = ""

        for peca_morta in self.pecas_capturadas:
            peca_morta.alpha = max(0, peca_morta.alpha - 15)
            escala_atual = (
                peca_morta.scale[0]
                if isinstance(peca_morta.scale, (tuple, list))
                else peca_morta.scale
            )
            peca_morta.scale = max(0.001, escala_atual - 0.005)
            if peca_morta.alpha == 0:
                self.pecas_capturadas.remove(peca_morta)

        for impacto in self.lista_impactos[:]:
            if impacto["tipo"] == "anel":
                impacto["raio"] += 3 * MULTIPLICADOR_GLOBAL
                impacto["alpha"] -= 15
                impacto["espessura"] -= 0.15
                if impacto["alpha"] <= 0 or impacto["espessura"] <= 0:
                    self.lista_impactos.remove(impacto)
            elif impacto["tipo"] == "particula":
                impacto["x"] += impacto["dx"]
                impacto["y"] += impacto["dy"]
                impacto["dy"] -= 0.1 * MULTIPLICADOR_GLOBAL
                impacto["alpha"] -= 10
                if impacto["alpha"] <= 0:
                    self.lista_impactos.remove(impacto)

        cor_ia = "preto" if CONFIGURACOES_JOGO["cor_jogador"] == "branco" else "branco"

        if (
            not self.jogo_acabou
            and not self.aguardando_promocao
            and CONFIGURACOES_JOGO["modo_ia"]
            and self.turno_atual == cor_ia
        ):
            self.tempo_espera_ia += delta_time
            if self.tempo_espera_ia > 0.8:
                self.fazer_jogada_ia()
                self.tempo_espera_ia = 0.0

    def fazer_jogada_ia(self):
        cor_ia = "preto" if CONFIGURACOES_JOGO["cor_jogador"] == "branco" else "branco"
        pecas_ia = [p for p in self.lista_pecas if p.cor == cor_ia]
        jogadas_possiveis = []
        for peca in pecas_ia:
            for l, c in self.obter_movimentos_seguros(peca):
                jogadas_possiveis.append((peca, l, c))

        if not jogadas_possiveis:
            return

        peca_escolhida, linha_destino, coluna_destino = None, None, None

        if CONFIGURACOES_JOGO["dificuldade_ia"] in ["Médio", "Difícil"]:
            jogadas_de_captura = []
            for jogada in jogadas_possiveis:
                p, l, c = jogada
                if self.matriz_tabuleiro[l][c] is not None or (
                    isinstance(p, Peao) and c != p.coluna_original
                ):
                    jogadas_de_captura.append(jogada)
            if jogadas_de_captura:
                peca_escolhida, linha_destino, coluna_destino = random.choice(
                    jogadas_de_captura
                )

        if peca_escolhida is None:
            peca_escolhida, linha_destino, coluna_destino = random.choice(
                jogadas_possiveis
            )

        self.executar_movimento(peca_escolhida, linha_destino, coluna_destino)

    def on_draw(self):
        self.clear()
        self.lista_fundo.draw()

        for impacto in self.lista_impactos:
            cor = (210, 180, 140, max(0, int(impacto["alpha"])))
            if impacto["tipo"] == "anel":
                arcade.draw_circle_outline(
                    impacto["x"],
                    impacto["y"],
                    impacto["raio"],
                    color=cor,
                    border_width=max(1, int(impacto["espessura"])),
                )
            elif impacto["tipo"] == "particula":
                arcade.draw_circle_filled(
                    impacto["x"], impacto["y"], impacto["raio"], color=cor
                )

        self.pecas_capturadas.draw()

        for peca in self.lista_pecas:
            arcade.draw_ellipse_filled(
                peca.center_x,
                peca.center_y - DESLOCAMENTO_Y_PECA,
                55 * MULTIPLICADOR_GLOBAL,
                18 * MULTIPLICADOR_GLOBAL,
                (0, 0, 0, 90),
            )
            if not self.jogo_acabou and peca.cor == self.turno_atual:
                arcade.draw_ellipse_outline(
                    peca.center_x,
                    peca.center_y - DESLOCAMENTO_Y_PECA,
                    55 * MULTIPLICADOR_GLOBAL,
                    18 * MULTIPLICADOR_GLOBAL,
                    color=(255, 215, 0, 160),
                    border_width=2,
                )
        self.lista_pecas.draw()

        janela = arcade.get_window()
        centro_x, centro_y = janela.width // 2, janela.height // 2

        if self.jogo_acabou or self.aguardando_promocao:
            arcade.draw_polygon_filled(
                (
                    (0, 0),
                    (janela.width, 0),
                    (janela.width, janela.height),
                    (0, janela.height),
                ),
                (0, 0, 0, 150),
            )

        if self.mensagem_tela:
            arcade.draw_text(
                self.mensagem_tela,
                centro_x + 4,
                centro_y + 36,
                arcade.color.BLACK,
                font_size=70,
                font_name=FONTES_JOGO,
                bold=True,
                anchor_x="center",
                anchor_y="center",
                align="center",
            )
            arcade.draw_text(
                self.mensagem_tela,
                centro_x,
                centro_y + 40,
                (255, 215, 0),
                font_size=70,
                font_name=FONTES_JOGO,
                bold=True,
                anchor_x="center",
                anchor_y="center",
                align="center",
            )

        if (
            self.mensagem_sistema
            and self.tempo_mensagem_sistema > 0
            and not self.jogo_acabou
            and not self.aguardando_promocao
        ):
            alpha = int(min(255, self.tempo_mensagem_sistema * 128))
            y_pos = (
                50
                if self.cor_mensagem_sistema == CONFIGURACOES_JOGO["cor_jogador"]
                else janela.height - 50
            )
            arcade.draw_text(
                self.mensagem_sistema,
                centro_x + 3,
                y_pos - 3,
                (0, 0, 0, alpha),
                font_size=28,
                font_name=FONTES_JOGO,
                bold=True,
                anchor_x="center",
                anchor_y="center",
                align="center",
            )
            arcade.draw_text(
                self.mensagem_sistema,
                centro_x,
                y_pos,
                (255, 215, 0, alpha),
                font_size=28,
                font_name=FONTES_JOGO,
                bold=True,
                anchor_x="center",
                anchor_y="center",
                align="center",
            )

        self.manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.jogo_acabou or self.aguardando_promocao:
            return
        if button == arcade.MOUSE_BUTTON_LEFT:
            cor_ia = (
                "preto" if CONFIGURACOES_JOGO["cor_jogador"] == "branco" else "branco"
            )
            if CONFIGURACOES_JOGO["modo_ia"] and self.turno_atual == cor_ia:
                return

            pecas_clicadas = arcade.get_sprites_at_point((x, y), self.lista_pecas)
            if pecas_clicadas:
                peca_alvo = pecas_clicadas[-1]
                if peca_alvo.cor == self.turno_atual:
                    self.peca_segurada = peca_alvo
                    (
                        self.peca_segurada.linha_original,
                        self.peca_segurada.coluna_original,
                    ) = (self.peca_segurada.linha, self.peca_segurada.coluna)
                    self.lista_pecas.remove(self.peca_segurada)
                    self.lista_pecas.append(self.peca_segurada)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.peca_segurada:
            self.peca_segurada.center_x, self.peca_segurada.center_y = x, y
            self.peca_segurada.destino_x, self.peca_segurada.destino_y = x, y

    def on_mouse_release(self, x, y, button, modifiers):
        if self.aguardando_promocao:
            return

        if button == arcade.MOUSE_BUTTON_LEFT and self.peca_segurada:
            offset_x, offset_y = (self.window.width - LARGURA_TELA) // 2, (
                self.window.height - ALTURA_TELA
            ) // 2
            col_clique = int((x - offset_x - INICIO_X) // TAMANHO_CASA)
            lin_clique = int((y - offset_y - INICIO_Y) // TAMANHO_CASA)

            movimento_valido = False
            if 0 <= col_clique <= 7 and 0 <= lin_clique <= 7:
                coluna_soltou = (
                    col_clique
                    if CONFIGURACOES_JOGO["cor_jogador"] == "branco"
                    else 7 - col_clique
                )
                linha_soltou = (
                    lin_clique
                    if CONFIGURACOES_JOGO["cor_jogador"] == "branco"
                    else 7 - lin_clique
                )

                for mov_linha, mov_coluna in self.obter_movimentos_seguros(
                    self.peca_segurada
                ):
                    if linha_soltou == mov_linha and coluna_soltou == mov_coluna:
                        movimento_valido = True
                        break

            if movimento_valido:
                self.executar_movimento(self.peca_segurada, linha_soltou, coluna_soltou)
            else:
                self.peca_segurada.linha, self.peca_segurada.coluna = (
                    self.peca_segurada.linha_original,
                    self.peca_segurada.coluna_original,
                )
                self.peca_segurada.atualizar_posicao_tela(instantaneo=False)
                self.criar_efeito_impacto(
                    self.peca_segurada.destino_x, self.peca_segurada.destino_y
                )

            self.peca_segurada = None


# =====================================================================
# --- TELAS DE MENU ---
# =====================================================================
class MenuOpcoes(arcade.View):
    def __init__(self, jogo_em_andamento=None):
        super().__init__()
        self.jogo_em_andamento = jogo_em_andamento
        self.manager = arcade.gui.UIManager()

        self.lista_fundo = arcade.SpriteList()
        self.fundo_sprite = None
        try:
            caminho_tabuleiro = os.path.join(DIRETORIO_ATUAL, "assets", "tabuleiro.png")
            escala_tabuleiro = LARGURA_TELA / 3100
            self.fundo_sprite = arcade.Sprite(caminho_tabuleiro, scale=escala_tabuleiro)
            self.lista_fundo.append(self.fundo_sprite)
        except Exception:
            pass

        self.v_box = arcade.gui.UIBoxLayout(space_between=10)

        texto_titulo = "Opções da Taverna" if not jogo_em_andamento else "Jogo Pausado"
        titulo = arcade.gui.UILabel(
            text=texto_titulo,
            text_color=(255, 215, 0),
            font_size=34,
            font_name=FONTES_JOGO,
            bold=True,
        )
        self.v_box.add(titulo)
        self.v_box.add(arcade.gui.UIWidget(height=10))

        texto_tela = (
            "Tela: Modo Cheio"
            if CONFIGURACOES_JOGO["tela_cheia"]
            else "Tela: Modo Janela"
        )
        self.btn_tela = arcade.gui.UIFlatButton(
            text=texto_tela, width=320, height=45, style=ESTILO_MADEIRA
        )
        self.v_box.add(self.btn_tela)

        # --- SLIDERS DE VOLUME ---
        self.lbl_sfx = arcade.gui.UILabel(
            text=f"Efeitos Sonoros: {int(CONFIGURACOES_JOGO['volume_sfx']*100)}%",
            text_color=(255, 230, 180),
            font_size=18,
            font_name=FONTES_JOGO,
            bold=True,
        )
        self.v_box.add(self.lbl_sfx)

        self.slider_sfx = arcade.gui.UISlider(
            value=CONFIGURACOES_JOGO["volume_sfx"] * 100, width=320, height=30
        )
        self.v_box.add(self.slider_sfx)

        self.lbl_musica = arcade.gui.UILabel(
            text=f"Música de Fundo: {int(CONFIGURACOES_JOGO['volume_musica']*100)}%",
            text_color=(255, 230, 180),
            font_size=18,
            font_name=FONTES_JOGO,
            bold=True,
        )
        self.v_box.add(self.lbl_musica)

        self.slider_musica = arcade.gui.UISlider(
            value=CONFIGURACOES_JOGO["volume_musica"] * 100, width=320, height=30
        )
        self.v_box.add(self.slider_musica)

        texto_modo = (
            "Modo: VS I.A."
            if CONFIGURACOES_JOGO["modo_ia"]
            else "Modo: Player vs Player"
        )
        self.btn_modo = arcade.gui.UIFlatButton(
            text=texto_modo, width=320, height=45, style=ESTILO_MADEIRA
        )
        self.v_box.add(self.btn_modo)

        texto_cor = (
            "Jogar de: Brancas"
            if CONFIGURACOES_JOGO["cor_jogador"] == "branco"
            else "Jogar de: Pretas"
        )
        self.btn_cor = arcade.gui.UIFlatButton(
            text=texto_cor, width=320, height=45, style=ESTILO_MADEIRA
        )
        if not jogo_em_andamento:
            self.v_box.add(self.btn_cor)

        self.btn_dif = arcade.gui.UIFlatButton(
            text=f"Nível da I.A.: {CONFIGURACOES_JOGO['dificuldade_ia']}",
            width=320,
            height=45,
            style=ESTILO_MADEIRA,
        )
        self.v_box.add(self.btn_dif)

        self.v_box.add(arcade.gui.UIWidget(height=10))
        texto_voltar = (
            "Voltar para a Partida" if jogo_em_andamento else "Voltar ao Menu"
        )
        btn_voltar = arcade.gui.UIFlatButton(
            text=texto_voltar, width=320, height=45, style=ESTILO_MADEIRA
        )
        self.v_box.add(btn_voltar)

        if jogo_em_andamento:
            btn_abandonar = arcade.gui.UIFlatButton(
                text="Abandonar Partida", width=320, height=45, style=ESTILO_MADEIRA
            )
            self.v_box.add(btn_abandonar)

            @btn_abandonar.event("on_click")
            def on_click_abandonar(event):
                self.window.show_view(MenuPrincipal())

        @self.btn_tela.event("on_click")
        def on_click_tela(event):
            CONFIGURACOES_JOGO["tela_cheia"] = not CONFIGURACOES_JOGO["tela_cheia"]
            self.window.set_fullscreen(CONFIGURACOES_JOGO["tela_cheia"])
            self.btn_tela.text = (
                "Tela: Modo Cheio"
                if CONFIGURACOES_JOGO["tela_cheia"]
                else "Tela: Modo Janela"
            )

        @self.slider_sfx.event("on_change")
        def on_change_sfx(event):
            CONFIGURACOES_JOGO["volume_sfx"] = self.slider_sfx.value / 100.0
            self.lbl_sfx.text = f"Efeitos Sonoros: {int(self.slider_sfx.value)}%"

        @self.slider_musica.event("on_change")
        def on_change_musica(event):
            CONFIGURACOES_JOGO["volume_musica"] = self.slider_musica.value / 100.0
            self.lbl_musica.text = f"Música de Fundo: {int(self.slider_musica.value)}%"
            janela = arcade.get_window()
            if hasattr(janela, "atualizar_volume_musica"):
                janela.atualizar_volume_musica()

        @self.btn_modo.event("on_click")
        def on_click_modo(event):
            CONFIGURACOES_JOGO["modo_ia"] = not CONFIGURACOES_JOGO["modo_ia"]
            self.btn_modo.text = (
                "Modo: VS I.A."
                if CONFIGURACOES_JOGO["modo_ia"]
                else "Modo: Player vs Player"
            )

        @self.btn_cor.event("on_click")
        def on_click_cor(event):
            CONFIGURACOES_JOGO["cor_jogador"] = (
                "preto" if CONFIGURACOES_JOGO["cor_jogador"] == "branco" else "branco"
            )
            self.btn_cor.text = (
                "Jogar de: Brancas"
                if CONFIGURACOES_JOGO["cor_jogador"] == "branco"
                else "Jogar de: Pretas"
            )

        @self.btn_dif.event("on_click")
        def on_click_dif(event):
            d = CONFIGURACOES_JOGO["dificuldade_ia"]
            if d == "Fácil":
                d = "Médio"
            elif d == "Médio":
                d = "Difícil"
            else:
                d = "Fácil"
            CONFIGURACOES_JOGO["dificuldade_ia"] = d
            self.btn_dif.text = f"Nível da I.A.: {d}"

        @btn_voltar.event("on_click")
        def on_click_voltar(event):
            if self.jogo_em_andamento:
                self.window.show_view(self.jogo_em_andamento)
            else:
                self.window.show_view(MenuPrincipal())

        ancora = arcade.gui.UIAnchorLayout()
        ancora.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(ancora)

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        if self.fundo_sprite:
            janela = arcade.get_window()
            self.fundo_sprite.center_x = janela.width // 2
            self.fundo_sprite.center_y = janela.height // 2
            self.lista_fundo.draw()
            arcade.draw_polygon_filled(
                (
                    (0, 0),
                    (janela.width, 0),
                    (janela.width, janela.height),
                    (0, janela.height),
                ),
                (0, 0, 0, 180),
            )
        self.manager.draw()


class MenuPrincipal(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()

        self.lista_fundo = arcade.SpriteList()
        self.fundo_sprite = None
        try:
            caminho_tabuleiro = os.path.join(DIRETORIO_ATUAL, "assets", "tabuleiro.png")
            escala_tabuleiro = LARGURA_TELA / 3100
            self.fundo_sprite = arcade.Sprite(caminho_tabuleiro, scale=escala_tabuleiro)
            self.lista_fundo.append(self.fundo_sprite)
        except Exception:
            pass

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        titulo = arcade.gui.UILabel(
            text="Xadrez Stardew Valley",
            text_color=(255, 215, 0),
            font_size=46,
            font_name=FONTES_JOGO,
            bold=True,
        )
        self.v_box.add(titulo)
        self.v_box.add(arcade.gui.UIWidget(height=30))

        btn_jogar = arcade.gui.UIFlatButton(
            text="Iniciar Partida", width=320, height=60, style=ESTILO_MADEIRA
        )
        btn_opcoes = arcade.gui.UIFlatButton(
            text="Opções", width=320, height=60, style=ESTILO_MADEIRA
        )
        btn_sair = arcade.gui.UIFlatButton(
            text="Sair da Taverna", width=320, height=60, style=ESTILO_MADEIRA
        )

        self.v_box.add(btn_jogar)
        self.v_box.add(btn_opcoes)
        self.v_box.add(btn_sair)

        @btn_jogar.event("on_click")
        def on_click_jogar(event):
            jogo = JogoXadrez()
            self.window.show_view(jogo)

        @btn_opcoes.event("on_click")
        def on_click_opcoes(event):
            opcoes = MenuOpcoes()
            self.window.show_view(opcoes)

        @btn_sair.event("on_click")
        def on_click_sair(event):
            arcade.exit()

        ancora = arcade.gui.UIAnchorLayout()
        ancora.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(ancora)

    def on_show_view(self):
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        if self.fundo_sprite:
            janela = arcade.get_window()
            self.fundo_sprite.center_x = janela.width // 2
            self.fundo_sprite.center_y = janela.height // 2
            self.lista_fundo.draw()
            arcade.draw_polygon_filled(
                (
                    (0, 0),
                    (janela.width, 0),
                    (janela.width, janela.height),
                    (0, janela.height),
                ),
                (0, 0, 0, 180),
            )

        self.manager.draw()


def main():
    window = JanelaPrincipal(LARGURA_TELA, ALTURA_TELA, TITULO_TELA, resizable=True)
    menu_view = MenuPrincipal()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
