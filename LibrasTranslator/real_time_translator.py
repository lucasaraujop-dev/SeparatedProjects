import pickle
import sys
import time
from collections import Counter, deque
from functools import lru_cache
 
import cv2
import mediapipe as mp
import numpy as np
 
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Falta o Pillow. Rode:  C:\\venv_libras\\Scripts\\python.exe -m pip install pillow")
 
from libras_utils import MODELO_FILE, extrair_features
 
try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except AttributeError:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw
 
# ---------------- Configuracao (ajuste aqui) ----------------
LIMIAR = 0.5               # confianca minima do modelo para aceitar uma letra
TEMPO_LETRA = 0.7          # segundos segurando para confirmar uma letra/gesto
N_AMOSTRAS_GESTO = 50      # amostras gravadas para o gesto de uma palavra
INTERVALO_GESTO = 0.05     # segundos entre amostras do gesto
CONTAGEM_GESTO = 3.0       # contagem regressiva antes de gravar o gesto
FATOR_LIMIAR_GESTO = 1.6   # tolerancia do gesto (maior = aceita mais variacao)
LIMIAR_MIN_GESTO = 0.40    # tolerancia minima do gesto
VID_W = 640                # largura do video na janela
PAINEL_W = 360             # largura do painel lateral
ALTURA_MIN = 480
SS = 2                     # supersampling do painel (suaviza bordas/texto)
JANELA = "LIBRAS Translator"
 
# Paleta estilo iOS (RGB, modo escuro)
C_FUNDO, C_CARD, C_CARD2 = (28, 28, 30), (44, 44, 46), (58, 58, 60)
C_TXT, C_TXT2, C_TXT3 = (255, 255, 255), (142, 142, 147), (99, 99, 102)
C_AZUL, C_VERDE, C_LARANJA = (10, 132, 255), (48, 209, 88), (255, 159, 10)
C_VERMELHO, C_INDIGO, C_INDIGO_CLARO = (255, 69, 58), (94, 92, 230), (140, 138, 255)
 
model = None
 
 
class Estado:
    def __init__(self):
        self.W, self.H, self.Hc = VID_W, 480, ALTURA_MIN
        self.palavras_sessao = {}   # nome -> (centro, limite)  (so nesta sessao)
        self.modo = 'normal'        # 'normal' | 'registrando' | 'gravando'
        self.nova_letras = []
        self.grav_inicio, self.grav_ultimo, self.grav_amostras = 0.0, 0.0, []
        self.mensagem, self.mensagem_ate = '', 0.0
        self.clique = None
        self.limpar_texto()
 
    def limpar_texto(self):
        self.letras_atuais, self.palavras = [], []
        self.finalizado = False
        self.resetar_candidato()
 
    def resetar_candidato(self):
        self.candidato, self.desde, self.armado = None, 0.0, True
        self.historico = deque(maxlen=7)
 
 
st = Estado()
 
 
# ---------------- Logica ----------------
def avisar(texto, dur=4.0):
    st.mensagem, st.mensagem_ate = texto, time.time() + dur
 
 
def fechar_palavra():
    if st.letras_atuais:
        st.palavras.append(''.join(st.letras_atuais))
        st.letras_atuais = []
 
 
def classificar(feats, usar_gestos):
    """Retorna (token, confianca, melhor_gesto). token: 'L:A', 'P:OI' ou '?'."""
    melhor = None
    if usar_gestos:
        for nome, (centro, lim) in st.palavras_sessao.items():
            d = float(np.linalg.norm(feats - centro))
            if melhor is None or d / lim < melhor[1] / melhor[2]:
                melhor = (nome, d, lim)
        if melhor and melhor[1] < melhor[2]:
            return 'P:' + melhor[0], 1.0, melhor
    proba = model.predict_proba(feats.reshape(1, -1))[0]
    k = int(np.argmax(proba))
    conf = float(proba[k])
    token = 'L:' + str(model.classes_[k]) if conf >= LIMIAR else '?'
    return token, conf, melhor
 
 
def confirmar(token):
    tipo, valor = token.split(':', 1)
    if st.modo == 'registrando':
        if tipo == 'L':
            st.nova_letras.append(valor)
    elif tipo == 'L':
        st.letras_atuais.append(valor)
    else:  # gesto de palavra registrada
        fechar_palavra()
        st.palavras.append(valor)
 
 
def processar_token(token, agora):
    """Suaviza (votacao dos ultimos frames) e confirma quando fica estavel."""
    st.historico.append(token)
    suave = Counter(st.historico).most_common(1)[0][0]
    if suave != st.candidato:
        st.candidato, st.desde, st.armado = suave, agora, True
    prog = 0.0
    if suave != '?':
        if st.armado:
            prog = min(1.0, (agora - st.desde) / TEMPO_LETRA)
            if prog >= 1.0 and st.modo in ('normal', 'registrando') and not st.finalizado:
                confirmar(suave)
                st.armado = False  # so confirma de novo se mudar de sinal ou tirar a mao
        else:
            prog = 1.0
    return suave, prog
 
 
def tratar_gravacao(feats, agora):
    if agora - st.grav_inicio < CONTAGEM_GESTO:
        return
    if (feats is not None and len(st.grav_amostras) < N_AMOSTRAS_GESTO
            and agora - st.grav_ultimo >= INTERVALO_GESTO):
        st.grav_amostras.append(feats)
        st.grav_ultimo = agora
    if len(st.grav_amostras) >= N_AMOSTRAS_GESTO:
        salvar_gesto()
 
 
def salvar_gesto():
    S = np.array(st.grav_amostras, dtype=np.float32)
    centro = S.mean(axis=0)
    d = np.linalg.norm(S - centro, axis=1)
    limite = max(float(np.percentile(d, 95)) * FATOR_LIMIAR_GESTO, LIMIAR_MIN_GESTO)
    nome = ''.join(st.nova_letras)
 
    avisos = []
    for outro, (c2, l2) in st.palavras_sessao.items():
        if outro != nome and np.linalg.norm(centro - c2) < max(limite, l2):
            avisos.append(f"parece o gesto de {outro}")
    proba = model.predict_proba(centro.reshape(1, -1))[0]
    k = int(np.argmax(proba))
    if proba[k] >= 0.6:
        avisos.append(f"parece a letra {model.classes_[k]}")
 
    st.palavras_sessao[nome] = (centro, limite)
    msg = f"Palavra {nome} registrada!"
    if avisos:
        msg += " Atenção: " + "; ".join(avisos) + "."
    avisar(msg, 7.0)
    print(f"[registro] {nome}: limite do gesto = {limite:.2f}")
    st.modo, st.nova_letras, st.grav_amostras = 'normal', [], []
    st.resetar_candidato()
 
 
def executar(bid, agora):
    if bid == 'proxima':
        if st.letras_atuais:
            fechar_palavra()
        else:
            avisar("Faça uma letra antes de ir para a próxima palavra.")
    elif bid == 'limpar':
        st.limpar_texto()
        avisar("Frase limpa.")
    elif bid == 'resetar':
        st.limpar_texto()
        st.palavras_sessao.clear()
        st.modo, st.nova_letras = 'normal', []
        avisar("Tudo resetado (palavras registradas apagadas).")
    elif bid == 'finalizar':
        fechar_palavra()
        if not st.palavras:
            avisar("Nada para finalizar.")
        else:
            st.finalizado = True
            print("FRASE FINAL:", ' '.join(st.palavras))
    elif bid == 'registrar':
        fechar_palavra()
        st.modo, st.nova_letras = 'registrando', []
        st.resetar_candidato()
    elif bid == 'gravar':
        if not st.nova_letras:
            avisar("Faça as letras da palavra primeiro.")
        else:
            st.modo, st.grav_inicio, st.grav_amostras, st.grav_ultimo = 'gravando', agora, [], 0.0
    elif bid == 'cancelar':
        st.modo, st.nova_letras, st.grav_amostras = 'normal', [], []
        st.resetar_candidato()
 
 
# ---------------- Botoes ----------------
def layout_botoes():
    """Lista de (id, rotulo, estilo, rect_no_painel, ativo)."""
    M = 16
    LARG = PAINEL_W - 2 * M
    itens = []
 
    def cheio(bid, rot, est, y, h, ativo=True):
        itens.append((bid, rot, est, (M, y, M + LARG, y + h), ativo))
 
    def meio(bid, rot, est, y, h, col, ativo=True):
        w = (LARG - 8) // 2
        x = M + col * (w + 8)
        itens.append((bid, rot, est, (x, y, x + w, y + h), ativo))
 
    if st.modo == 'normal' and not st.finalizado:
        cheio('proxima', 'Próxima palavra', 'azul', 204, 48, bool(st.letras_atuais))
        meio('finalizar', 'Finalizar', 'verde', 260, 44, 0, bool(st.palavras or st.letras_atuais))
        meio('limpar', 'Limpar frase', 'laranja', 260, 44, 1)
        cheio('registrar', 'Registrar nova palavra', 'indigo', 312, 44)
        cheio('resetar', 'Resetar tudo', 'vermelho', 364, 40)
    elif st.modo == 'normal':
        cheio('limpar', 'Limpar frase', 'azul', 204, 48)
        cheio('resetar', 'Resetar tudo', 'vermelho', 260, 44)
    elif st.modo == 'registrando':
        cheio('gravar', 'Gravar gesto da palavra', 'verde', 204, 48, bool(st.nova_letras))
        cheio('cancelar', 'Cancelar', 'cinza', 260, 44)
    else:
        cheio('cancelar', 'Cancelar', 'cinza', 204, 48)
    return itens
 
 
def ao_clicar(evento, x, y, flags, param):
    if evento == cv2.EVENT_LBUTTONDOWN:
        px = x - st.W  # coordenada dentro do painel
        for bid, _, _, (x1, y1, x2, y2), ativo in layout_botoes():
            if ativo and x1 <= px <= x2 and y1 <= y <= y2:
                st.clique = bid
                break
 
 
# ---------------- Desenho (Pillow) ----------------
@lru_cache(maxsize=None)
def fonte(tam, peso='regular'):
    nomes = {
        'regular': ['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf'],
        'semibold': ['seguisb.ttf', 'segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'],
    }[peso]
    for n in nomes:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            continue
    return ImageFont.load_default()
 
 
class Pintor:
    """Desenha em coordenadas 1x mesmo que a imagem esteja em escala k."""
 
    def __init__(self, img, k):
        self.d, self.k = ImageDraw.Draw(img), k
 
    def s(self, v):
        return int(round(v * self.k))
 
    def rr(self, rect, raio, fill):
        x1, y1, x2, y2 = rect
        self.d.rounded_rectangle((self.s(x1), self.s(y1), self.s(x2), self.s(y2)),
                                 radius=self.s(raio), fill=fill)
 
    def circ(self, cx, cy, r, fill):
        self.d.ellipse((self.s(cx - r), self.s(cy - r), self.s(cx + r), self.s(cy + r)), fill=fill)
 
    def tx(self, x, y, texto, tam, peso, cor, ancora='lm'):
        self.d.text((self.s(x), self.s(y)), texto, font=fonte(self.s(tam), peso), fill=cor, anchor=ancora)
 
    def larg(self, texto, tam, peso='regular'):
        return self.d.textlength(texto, font=fonte(self.s(tam), peso)) / self.k
 
 
def misturar(c1, c2, a):
    return tuple(int(c1[i] * a + c2[i] * (1 - a)) for i in range(3))
 
 
def cortar(p, texto, largura, tam, peso):
    if p.larg(texto, tam, peso) <= largura:
        return texto
    while len(texto) > 1 and p.larg(texto + '…', tam, peso) > largura:
        texto = texto[:-1]
    return texto + '…'
 
 
def quebrar(p, tokens, largura, tam, peso):
    linhas, usado = [[]], 0.0
    esp = p.larg(' ', tam, peso)
    for t, c in tokens:
        w = p.larg(t, tam, peso)
        extra = w if not linhas[-1] else w + esp
        if linhas[-1] and usado + extra > largura:
            linhas.append([])
            usado, extra = 0.0, w
        linhas[-1].append((t, c))
        usado += extra
    return linhas
 
 
CARD = (16, 16, PAINEL_W - 16, 152)
 
 
def desenhar_card(p, agora):
    x1, y1, x2, y2 = CARD
    p.rr(CARD, 16, C_CARD)
    largura = (x2 - x1) - 32
    tam, peso, alt_linha = 24, 'semibold', 30
 
    if st.modo == 'gravando':
        p.tx(x1 + 16, y1 + 20, ('GRAVANDO GESTO · ' + ''.join(st.nova_letras)).upper(), 12, 'semibold', C_VERMELHO)
        t = agora - st.grav_inicio
        if t < CONTAGEM_GESTO:
            p.tx((x1 + x2) / 2, y1 + 70, str(int(CONTAGEM_GESTO - t) + 1), 48, 'semibold', C_TXT, 'mm')
            p.tx((x1 + x2) / 2, y1 + 106, 'Prepare o gesto…', 15, 'regular', C_TXT2, 'mm')
        else:
            p.tx((x1 + x2) / 2, y1 + 70, 'Gravando…', 26, 'semibold', C_TXT, 'mm')
            frac = len(st.grav_amostras) / N_AMOSTRAS_GESTO
            bx1, bx2, by = x1 + 16, x2 - 16, y1 + 106
            p.rr((bx1, by, bx2, by + 6), 3, C_CARD2)
            if frac > 0:
                p.rr((bx1, by, bx1 + max(6, (bx2 - bx1) * frac), by + 6), 3, C_VERMELHO)
        return
 
    if st.modo == 'registrando':
        rotulo, cor_rot = 'NOVA PALAVRA', C_INDIGO_CLARO
        tokens = [(''.join(st.nova_letras), C_INDIGO_CLARO)] if st.nova_letras else []
        vazio, cursor = 'Faça as letras da palavra', True
    else:
        rotulo, cor_rot = ('FRASE FINAL', C_VERDE) if st.finalizado else ('FRASE', C_TXT2)
        cor_pal = C_VERDE if st.finalizado else C_TXT
        tokens = [(w, cor_pal) for w in st.palavras]
        if st.letras_atuais:
            tokens.append((''.join(st.letras_atuais), C_AZUL))
        vazio, cursor = 'Faça uma letra…', not st.finalizado
    p.tx(x1 + 16, y1 + 20, rotulo, 12, 'semibold', cor_rot)
 
    esp = p.larg(' ', tam, peso)
    topo = y1 + 36
    if not tokens:
        p.tx(x1 + 16, topo + alt_linha / 2, vazio, tam, 'regular', C_TXT3)
        if cursor and int(agora * 2) % 2 == 0:
            p.rr((x1 + 16 - 3, topo + 4, x1 + 16 - 1, topo + alt_linha - 4), 1, C_AZUL)
        return
 
    linhas = quebrar(p, tokens, largura, tam, peso)
    cortou = len(linhas) > 3
    linhas = linhas[-3:]
    for i, linha in enumerate(linhas):
        y = topo + i * alt_linha + alt_linha / 2
        x = x1 + 16
        if i == 0 and cortou:
            p.tx(x, y, '…', tam, peso, C_TXT3)
            x += p.larg('…', tam, peso) + esp
        for t, c in linha:
            p.tx(x, y, t, tam, peso, c)
            x += p.larg(t, tam, peso) + esp
        if i == len(linhas) - 1 and cursor and int(agora * 2) % 2 == 0:
            ultimo_atual = bool(st.letras_atuais) or st.modo == 'registrando'
            cx = x - esp + 3 if ultimo_atual else x
            p.rr((cx, y - 12, cx + 2, y + 12), 1, C_AZUL)
 
 
def desenhar_botoes(p):
    for _, rot, est, rect, ativo in layout_botoes():
        if not ativo:
            fill, cor_txt = C_CARD, C_TXT3
        elif est == 'azul':
            fill, cor_txt = C_AZUL, C_TXT
        elif est == 'verde':
            fill, cor_txt = C_VERDE, (0, 40, 10)
        elif est == 'cinza':
            fill, cor_txt = C_CARD2, C_TXT
        else:  # tinted
            cor = {'laranja': C_LARANJA, 'vermelho': C_VERMELHO, 'indigo': C_INDIGO}[est]
            fill = misturar(cor, C_FUNDO, 0.22)
            cor_txt = C_INDIGO_CLARO if est == 'indigo' else cor
        p.rr(rect, 14, fill)
        p.tx((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2, rot, 16, 'semibold', cor_txt, 'mm')
 
 
def dica_e_debug(agora, melhor):
    if st.modo == 'registrando':
        dica = 'Faça as letras e depois grave o gesto da palavra.'
    elif st.modo == 'gravando':
        dica = 'Mantenha o gesto e mexa a mão de leve.'
    elif st.finalizado:
        dica = 'Frase finalizada. Toque em Limpar frase.'
    elif st.letras_atuais:
        dica = 'Toque em Próxima palavra para fechar a palavra.'
    else:
        dica = f'Segure cada letra por {TEMPO_LETRA:.1f} s para confirmar'.replace('.', ',')
    debug = ''
    if melhor and st.modo == 'normal':
        debug = f'Gesto {melhor[0]}: distância {melhor[1]:.2f} (limite {melhor[2]:.2f})'
    return dica, debug
 
 
def render_painel(agora, melhor, altura):
    img = Image.new('RGB', (PAINEL_W * SS, altura * SS), C_FUNDO)
    p = Pintor(img, SS)
    desenhar_card(p, agora)
    dica, debug = dica_e_debug(agora, melhor)
    p.tx(20, 166, cortar(p, dica, PAINEL_W - 40, 13, 'regular'), 13, 'regular', C_TXT2)
    if debug:
        p.tx(20, 184, cortar(p, debug, PAINEL_W - 40, 12, 'regular'), 12, 'regular', C_TXT3)
    desenhar_botoes(p)
    p.tx(PAINEL_W / 2, altura - 18, 'Q: sair   ·   Espaço: próxima palavra', 11, 'regular', C_TXT3, 'mm')
    reamostra = getattr(Image, 'Resampling', Image).LANCZOS
    return img.resize((PAINEL_W, altura), reamostra)
 
 
def render_video(frame_bgr, agora, pill, tem_mao):
    base = Image.fromarray(frame_bgr[:, :, ::-1]).convert('RGBA')
    W, H = base.size
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
    p = Pintor(ov, 1)
 
    if pill and st.modo != 'gravando':
        w = p.larg(pill['principal'], 26, 'semibold') + p.larg(pill['secundario'], 13) + 36
        x = min(max(8, pill['x'] - 10), W - w - 8)
        y = max(8, pill['y'] - 58)
        p.rr((x, y, x + w, y + 42), 21, (20, 20, 22, 190))
        p.tx(x + 14, y + 21, pill['principal'], 26, 'semibold', (255, 255, 255, 255))
        p.tx(x + 22 + p.larg(pill['principal'], 26, 'semibold'), y + 23, pill['secundario'], 13, 'regular',
             (200, 200, 205, 255))
        p.rr((x, y + 48, x + w, y + 52), 2, (255, 255, 255, 70))
        if pill['prog'] > 0:
            p.rr((x, y + 48, x + max(4, w * pill['prog']), y + 52), 2, C_AZUL + (255,))
 
    if st.modo == 'gravando':
        t = agora - st.grav_inicio
        if t < CONTAGEM_GESTO:
            cx, cy = W / 2, H / 2
            p.circ(cx, cy, 64, (0, 0, 0, 150))
            p.tx(cx, cy - 4, str(int(CONTAGEM_GESTO - t) + 1), 72, 'semibold', (255, 255, 255, 255), 'mm')
            p.tx(cx, cy + 96, 'Prepare o gesto', 18, 'semibold', (255, 255, 255, 255), 'mm')
        else:
            txt = f'Gravando  {len(st.grav_amostras)}/{N_AMOSTRAS_GESTO}'
            w = p.larg(txt, 15, 'semibold') + 44
            p.rr((12, 12, 12 + w, 48), 18, (20, 20, 22, 200))
            p.circ(30, 30, 6, C_VERMELHO + (255,))
            p.tx(44, 30, txt, 15, 'semibold', (255, 255, 255, 255))
            if not tem_mao:
                aviso = 'Mostre a mão para a câmera'
                w2 = p.larg(aviso, 16, 'semibold') + 36
                p.rr((W / 2 - w2 / 2, H - 60, W / 2 + w2 / 2, H - 20), 20, C_LARANJA + (230,))
                p.tx(W / 2, H - 40, aviso, 16, 'semibold', (0, 0, 0, 255), 'mm')
 
    if agora < st.mensagem_ate:
        txt = cortar(p, st.mensagem, W - 64, 15, 'semibold')
        w = p.larg(txt, 15, 'semibold') + 32
        p.rr((W / 2 - w / 2, 12, W / 2 + w / 2, 48), 18, (28, 28, 30, 230))
        p.tx(W / 2, 30, txt, 15, 'semibold', (255, 255, 255, 255), 'mm')
 
    return Image.alpha_composite(base, ov).convert('RGB')
 
 
def renderizar(frame_bgr, agora, melhor, pill, tem_mao):
    video = render_video(frame_bgr, agora, pill, tem_mao)
    painel = render_painel(agora, melhor, st.Hc)
    canvas = Image.new('RGB', (st.W + PAINEL_W, st.Hc), C_FUNDO)
    canvas.paste(video, (0, 0))
    canvas.paste(painel, (st.W, 0))
    return np.array(canvas)[:, :, ::-1].copy()
 
 
# ---------------- Programa principal ----------------
def main():
    global model
    try:
        with open(MODELO_FILE, 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        sys.exit("modelo_libras.p não encontrado. Rode o machine_learn.py primeiro.")
 
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform.startswith('win') else cv2.VideoCapture(0)
    if not cap.isOpened():
        sys.exit("Não foi possível abrir a webcam.")
 
    espec_pontos = mp_draw.DrawingSpec(color=(255, 132, 10), thickness=-1, circle_radius=3)
    espec_linhas = mp_draw.DrawingSpec(color=(240, 240, 240), thickness=2)
 
    cv2.namedWindow(JANELA)
    cv2.setMouseCallback(JANELA, ao_clicar)
 
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h0, w0 = frame.shape[:2]
        if w0 != VID_W:
            frame = cv2.resize(frame, (VID_W, int(h0 * VID_W / w0)))
        st.H, st.W = frame.shape[:2]
        st.Hc = max(st.H, ALTURA_MIN)
        agora = time.time()
        resultado = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
 
        if st.clique:
            executar(st.clique, agora)
            st.clique = None
 
        feats, melhor, pill = None, None, None
        tem_mao = bool(resultado.multi_hand_landmarks)
        if tem_mao:
            hl = resultado.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS, espec_pontos, espec_linhas)
            feats = np.array(extrair_features(hl), dtype=np.float32)
            if st.modo != 'gravando':
                token, conf, melhor = classificar(feats, usar_gestos=(st.modo == 'normal'))
                suave, prog = processar_token(token, agora)
                if suave.startswith('L:'):
                    principal, secundario = suave[2:], f"{conf * 100:.0f}%"
                elif suave.startswith('P:'):
                    principal, secundario = suave[2:], 'gesto'
                else:
                    principal, secundario = '?', ''
                pill = dict(x=int(min(lm.x for lm in hl.landmark) * st.W),
                            y=int(min(lm.y for lm in hl.landmark) * st.H),
                            principal=principal, secundario=secundario, prog=prog)
        else:
            st.resetar_candidato()
 
        if st.modo == 'gravando':
            tratar_gravacao(feats, agora)
 
        cv2.imshow(JANELA, renderizar(frame, agora, melhor, pill, tem_mao))
 
        tecla = cv2.waitKey(1) & 0xFF
        if tecla in (ord('q'), ord('Q')):
            break
        if tecla == 32 and st.modo == 'normal' and not st.finalizado:  # ESPACO
            executar('proxima', agora)
        if cv2.getWindowProperty(JANELA, cv2.WND_PROP_VISIBLE) < 1:
            break
 
    cap.release()
    hands.close()
    cv2.destroyAllWindows()
 
 
if __name__ == '__main__':
    main()