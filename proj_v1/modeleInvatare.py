import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, roc_curve, auc
from sklearn.ensemble import IsolationForest

# =========================================
# 1. INCARCARE SI PREPROCESARE DATE
# =========================================
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
column_names = ['Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin',
                'Alkaline_Phosphotase', 'Alamine_Aminotransferase',
                'Aspartate_Aminotransferase', 'Total_Protiens',
                'Albumin', 'Albumin_and_Globulin_Ratio', 'Dataset']

df = pd.read_csv(url, names=column_names, header=None)

# Eliminare valori lipsa (NA)
df = df.dropna()

# Mapari: Female = 0, Male = 1 | 1 (Bolnav) -> 1, 2 (Sanatos) -> 0
df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1})
df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})

# Separare intrari (X) si tinta (Y)
X = df.drop('Dataset', axis=1)
Y = df['Dataset']

print(f"Set de date incarcat. Dimensiune: {df.shape}")

# =========================================
# 2. DETECTARE ANOMALII (Vizualizare, fara eliminare)
# =========================================
# detectare anomalii
iso_forest = IsolationForest(contamination=0.05, random_state=42)
preds = iso_forest.fit_predict(X)

# Cream o coloana speciala cu nume clare pentru legenda
df['Status_Detectie'] = np.where(preds == 1, 'Normal', 'Anomalie')

plt.figure(figsize=(10, 6), num="Imagine 1: Vizualizare Anomalii")
# Folosim culori explicite: Albastru pentru Normal, Rosu pentru Anomalie
sns.scatterplot(data=df, x='Total_Bilirubin', y='Alamine_Aminotransferase', 
                hue='Status_Detectie', 
                palette={'Normal': 'blue', 'Anomalie': 'red'}, 
                alpha=0.6)
plt.title("Detectie Anomalii (Isolation Forest - Fara eliminare)")
plt.xlabel("Bilirubina Totala")
plt.ylabel("ALT (Alamine Aminotransferase)")

num_anom = (preds == -1).sum()
print(f"# detectare anomalii: S-au identificat {num_anom} puncte atipice.")

# =========================================
# 3. STATISTICI SI MATRICE DE CORELATIE
# =========================================
print("\n--- Statistici Descriptive ---")
stats = X.describe().T[['mean', 'std', 'min', 'max']]
stats['variance'] = stats['std'] ** 2
print(stats)

plt.figure(figsize=(10, 8), num="Imagine 2: Matrice Corelatie")
# Excludem coloana de tag-uri de anomalii din corelatie
sns.heatmap(df.drop(['Status_Detectie'], axis=1).corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Matricea de Corelatie a Caracteristicilor")

# =========================================
# 4. DISTRIBUTIA CLASELOR
# =========================================
plt.figure(figsize=(6, 4), num="Imagine 3: Distributie Clase")
ax = sns.countplot(x='Dataset', data=df)
plt.title("Distributia Claselor (0=Sanatos, 1=Boala)")
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2., p.get_height(), '{:1.0f}'.format(p.get_height()), ha='center', va='bottom')

# =========================================
# 5. ANTRENARE MODELE SI CURBE ROC (Imaginea 4)
# =========================================
test_sizes = [0.20, 0.30, 0.40, 0.50]

# Configurare modele (probability=True este necesar pentru ROC)
svm_model = SVC(kernel='rbf', probability=True, random_state=42)
mlp_model = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
scaler = StandardScaler()

fig_roc, axes_roc = plt.subplots(2, 2, figsize=(15, 12), num="Imagine 4: Curbe ROC per Split")
axes_roc = axes_roc.flatten()

print("\n--- Performanta Modele (Antrenate pe tot setul, inclusiv anomalii) ---")

for i, size in enumerate(test_sizes):
    # Partitionare stratificata
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)

    # Scalare (Esentiala pentru performanta)
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # --- SVM ---
    svm_model.fit(X_train_scaled, y_train)
    y_probs_svm = svm_model.predict_proba(X_test_scaled)[:, 1]
    fpr_svm, tpr_svm, _ = roc_curve(y_test, y_probs_svm)
    auc_svm = auc(fpr_svm, tpr_svm)

    # --- MLP ---
    mlp_model.fit(X_train_scaled, y_train)
    y_probs_mlp = mlp_model.predict_proba(X_test_scaled)[:, 1]
    fpr_mlp, tpr_mlp, _ = roc_curve(y_test, y_probs_mlp)
    auc_mlp = auc(fpr_mlp, tpr_mlp)

    # Output Consola
    split_label = f"{int((1 - size) * 100)}% / {int(size * 100)}%"
    print(f"Split {split_label} | AUC SVM: {auc_svm:.4f} | AUC MLP: {auc_mlp:.4f}")

    # Desenare ROC
    ax = axes_roc[i]
    ax.plot(fpr_svm, tpr_svm, label=f'SVM (AUC = {auc_svm:.3f})', color='blue', lw=2)
    ax.plot(fpr_mlp, tpr_mlp, label=f'MLP (AUC = {auc_mlp:.3f})', color='red', lw=2)
    ax.plot([0, 1], [0, 1], color='gray', linestyle='--')
    ax.set_title(f"Curba ROC - Split {split_label}")
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()