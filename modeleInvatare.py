#from tkinter.tix import COLUMN

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer


url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
column_names = ['Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin',
                'Alkaline_Phosphotase', 'Alamine_Aminotransferase',
                'Aspartate_Aminotransferase', 'Total_Protiens',
                'Albumin', 'Albumin_and_Globulin_Ratio', 'Dataset']

df = pd.read_csv(url, names=column_names, header=None)

print(f"Dimensiunea inițiala a setului de date: {df.shape}")


print("\n--- Valori lipsa pe coloane ---")
print(df.isnull().sum())

df = df.dropna()
# drop unde nu avem valori

print(f"Dimensiunea dupa eliminarea valorilor lipsa: {df.shape}")

#Female = 0, Male = 1
df['Gender'] = df['Gender'].map({'Female': 0, 'Male' : 1})


# INITIAL: 1(BOLNAV) -> 1 ; 2(SANATOS) -> 0
df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})

#Separare in intrari si tinta, drop la ultima coloana
X = df.drop('Dataset', axis=1)
Y = df['Dataset']

#Calcul statistici(Media, Dispersia, Min, Max)

print("\n--- Statistici Descriptive ---")

stats = X.describe().T[['mean', 'std', 'min', 'max']]
stats['variance'] = stats['std'] ** 2
print(stats)


#Corelatie intre valorile de intrare

plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Matricea de Corelație a Caracteristicilor")
plt.show()

# Vizualizare distributiei target (sanatos/boala)
plt.figure(figsize=(6, 4))
ax = sns.countplot(x='Dataset', data=df)
plt.title("Distribuția Claselor (0=Sanatos, 1=Boala) cu numar fix")

for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2.,
            p.get_height(),
            '{:1.0f}'.format(p.get_height()),
            ha = 'center' ,
            va = 'bottom')

plt.show()

# Partitionare, clasificare Support vector machine (SVM) si A multi-layer perceptron (MLP)

# Definim rapoartele de testare
test_sizes = [0.20, 0.30, 0.40, 0.50]

# Modele
svm_model = SVC(kernel='rbf', random_state=42)
mlp_model = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)

# Scalare (Esentiala pentru SVM și MLP)
scaler = StandardScaler()

results = []

print("\n--- Analiza Comparativă SVM vs MLP pe diverse partiții ---")

for size in test_sizes:
    # Partitionare
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)

    # Verificare distribuție
    dist_train = y_train.value_counts(normalize=True).iloc[0] # normalizam datele si dupa luam informatia din clasa majoritara
    dist_test = y_test.value_counts(normalize=True).iloc[0]

    # Scalare date
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. SVM
    svm_model.fit(X_train_scaled, y_train)
    y_pred_svm = svm_model.predict(X_test_scaled)
    acc_svm = accuracy_score(y_test, y_pred_svm)

    # 2. MLP
    mlp_model.fit(X_train_scaled, y_train)
    y_pred_mlp = mlp_model.predict(X_test_scaled)
    acc_mlp = accuracy_score(y_test, y_pred_mlp)

    print(f"\nSplit Train/Test: {int((1 - size) * 100)}% / {int(size * 100)}%")
    print(f"   Distributie clasa majoritara (Train/Test): {dist_train:.2f} / {dist_test:.2f}")
    print(f"   Acuratete SVM: {acc_svm:.4f}")
    print(f"   Acuratete MLP: {acc_mlp:.4f}")

