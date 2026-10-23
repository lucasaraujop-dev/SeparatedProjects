import csv
import os
import sys
import time

import cv2
import mediapipe as mp

from libras_utils import CSV_FILE, cabecalho, extrair_features

try:
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
except AttributeError:
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_draw

TOTAL_SAMPLES = 100
INTERVALO = 0.1  # segundos entre amostras

current_letter = input("Qual letra você vai gravar (A-Z, sem acento)? ").strip().upper()
if len(current_letter) != 1 or not ('A' <= current_letter <= 'Z'):
    sys.exit("Digite UMA letra de A a Z, sem acento.")

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                       min_detection_confidence=0.7)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(cabecalho())

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform.startswith('win') else cv2.VideoCapture(0)
if not cap.isOpened():
    sys.exit("Não foi possível abrir a webcam.")

count = 0
recording = False
last_save = 0.0
print(f"Pressione 'S' para gravar a letra {current_letter} ('Q' para sair).")
print("DURANTE a gravação, mova a mão: aproxime, afaste, incline e gire um pouco.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro ao acessar a webcam.")
        break

    frame = cv2.flip(frame, 1)
    resultado = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if resultado.multi_hand_landmarks:
        for hand_landmarks in resultado.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            now = time.time()
            if recording and count < TOTAL_SAMPLES and now - last_save >= INTERVALO:
                with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow([current_letter] + extrair_features(hand_landmarks))
                count += 1
                last_save = now

    status = f'Gravando {current_letter}: {count}/{TOTAL_SAMPLES}' if recording else "Aperte 'S' para gravar"
    cv2.putText(frame, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if count >= TOTAL_SAMPLES:
        print(f"Coleta concluída para a letra '{current_letter}'!")
        break

    cv2.imshow("LIBRAS Data Collector", frame)
    key = cv2.waitKey(1) & 0xFF
    if key in (ord('s'), ord('S')):
        recording = True
    elif key in (ord('q'), ord('Q')):
        break

cap.release()
hands.close()
cv2.destroyAllWindows()
