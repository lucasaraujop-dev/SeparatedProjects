"""Funções compartilhadas: garante que coleta, conversão, treino e tradução
usem EXATAMENTE as mesmas features."""
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'dataset_libras_v2.csv')
MODELO_FILE = os.path.join(BASE_DIR, 'modelo_libras.p')


def cabecalho():
    return ['label'] + [f'pt_{i}_{c}' for i in range(21) for c in 'xyz']


def extrair_features(hand_landmarks):
    """63 números: (x, y, z) dos 21 pontos, relativos ao pulso e
    divididos pelo tamanho da mão (independe da distância da câmera)."""
    pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark],
                   dtype=np.float32)
    pts -= pts[0]
    escala = float(np.max(np.linalg.norm(pts[:, :2], axis=1)))
    if escala < 1e-6:
        escala = 1.0
    pts /= escala
    return pts.flatten().tolist()
