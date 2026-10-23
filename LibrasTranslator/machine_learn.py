import pickle
import sys

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from libras_utils import CSV_FILE, MODELO_FILE

df = pd.read_csv(CSV_FILE, encoding='utf-8')
print("Amostras por letra:")
print(df['label'].value_counts().sort_index().to_string(), "\n")

if df['label'].nunique() < 2:
    sys.exit("Você precisa de pelo menos 2 letras diferentes no dataset.")

X = df.drop('label', axis=1).values
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Acurácia do modelo: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
print(classification_report(y_test, y_pred, zero_division=0))

with open(MODELO_FILE, 'wb') as f:
    pickle.dump(model, f)
print("Modelo salvo como 'modelo_libras.p'!")
