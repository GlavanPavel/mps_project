##########################################################################
#                                                                        #
#  Copyright:   (c) 2026, Proiect MPS                                    #
#  Autori:      Albu A. Sorin (R.Moldova) 1409A                          #
#               Glavan P. Pavel (R.Moldova) 1409A                        #
#               Duda I.I. Andrei-Ionuț 1409A                             #
#               Jireadă C. Teodor 1409A                                  #
#               Popovici I.L. Andrei 1409A                               #
#               Noroc D. Sorin (R.Moldova) 1409A                         #
#               Timofte C. Constantin 1409A                              #
#               Matei I. Ion (R.Moldova) 1410B                           #
#                                                                        #
#  Descriere:   Sistem Expert pentru Predictia Bolilor Hepatice          #
#               Utilizand algoritmii SVM si Multilayer Perceptron (MLP)  #
#               Bazat pe setul de date ILPD (Indian Liver Patient)       #
#                                                                        #
#  Acest cod si informatiile sunt oferite "ca atare" fara nicio garantie #
#  de orice fel, exprimata sau implicita. Acest proiect este realizat    #
#  in scop didactic pentru disciplina Managementul Proiectelor Software. #
#                                                                        #
##########################################################################
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

"""
Incarcarea setului de date ILPD de la sursa externa si 
preprocesarea acestuia prin eliminarea valorilor lipsa si maparea 
variabilelor categorice in format numeric 
"""
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
column_names = ['Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin',
                'Alkaline_Phosphotase', 'Alamine_Aminotransferase',
                'Aspartate_Aminotransferase', 'Total_Protiens',
                'Albumin', 'Albumin_and_Globulin_Ratio', 'Dataset']

df = pd.read_csv(url, names=column_names, header=None)
df = df.dropna()

df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1})
df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})

X = df.drop('Dataset', axis=1)
Y = df['Dataset']

print(f"Set de date incarcat. Dimensiune: {df.shape}")

"""
Utilizarea algoritmului Isolation Forest pentru identificarea si 
vizualizarea anomaliilor din setul de date
"""
iso_forest = IsolationForest(contamination=0.05, random_state=42)
preds = iso_forest.fit_predict(X)

df['Status_Detectie'] = np.where(preds == 1, 'Normal', 'Anomalie')

plt.figure(figsize=(10, 6), num="Imagine 1: Vizualizare Anomalii")
sns.scatterplot(data=df, x='Total_Bilirubin', y='Alamine_Aminotransferase', 
                hue='Status_Detectie', 
                palette={'Normal': 'blue', 'Anomalie': 'red'}, 
                alpha=0.6)
plt.title("Detectie Anomalii (Isolation Forest - Fara eliminare)")
plt.xlabel("Bilirubina Totala")
plt.ylabel("ALT (Alamine Aminotransferase)")

num_anom = (preds == -1).sum()
print(f"# detectare anomalii: S-au identificat {num_anom} puncte atipice.")

"""
Calcularea statisticilor descriptive de baza si generarea
 matricei de corelatie pentru a evidentia dependentele liniare 
 dintre atributele clinice si a intelege mai bine structura datelor.
"""
print("\n--- Statistici Descriptive ---")
stats = X.describe().T[['mean', 'std', 'min', 'max']]
stats['variance'] = stats['std'] ** 2
print(stats)

plt.figure(figsize=(10, 8), num="Imagine 2: Matrice Corelatie")
sns.heatmap(df.drop(['Status_Detectie'], axis=1).corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Matricea de Corelatie a Caracteristicilor")

"""
Vizualizarea distributiei claselor tinta pentru 
a evalua echilibrul dintre pacientii diagnosticati cu boala hepatica si cei sanatosi.
"""
plt.figure(figsize=(6, 4), num="Imagine 3: Distributie Clase")
ax = sns.countplot(x='Dataset', data=df)
plt.title("Distributia Claselor (0=Sanatos, 1=Boala)")
for p in ax.patches:
    ax.text(p.get_x() + p.get_width() / 2., p.get_height(), '{:1.0f}'.format(p.get_height()), ha='center', va='bottom')

"""
Antrenarea comparativa a modelelor SVM si MLP pe 
diferite proportii de impartire a datelor urmata de evaluarea performantei 
prin generarea curbelor ROC si calcularea ariei de sub curba AUC.
"""
test_sizes = [0.20, 0.30, 0.40, 0.50]

svm_model = SVC(kernel='rbf', probability=True, random_state=42)
mlp_model = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
scaler = StandardScaler()

fig_roc, axes_roc = plt.subplots(2, 2, figsize=(15, 12), num="Imagine 4: Curbe ROC per Split")
axes_roc = axes_roc.flatten()

print("\n--- Performanta Modele (Antrenate pe tot setul, inclusiv anomalii) ---")

for i, size in enumerate(test_sizes):
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Antrenare SVM
    svm_model.fit(X_train_scaled, y_train)
    y_probs_svm = svm_model.predict_proba(X_test_scaled)[:, 1]
    fpr_svm, tpr_svm, _ = roc_curve(y_test, y_probs_svm)
    auc_svm = auc(fpr_svm, tpr_svm)

    # Antrenare MLP
    mlp_model.fit(X_train_scaled, y_train)
    y_probs_mlp = mlp_model.predict_proba(X_test_scaled)[:, 1]
    fpr_mlp, tpr_mlp, _ = roc_curve(y_test, y_probs_mlp)
    auc_mlp = auc(fpr_mlp, tpr_mlp)

    # Afisare rezultate in consola
    split_label = f"{int((1 - size) * 100)}% / {int(size * 100)}%"
    print(f"Split {split_label} | AUC SVM: {auc_svm:.4f} | AUC MLP: {auc_mlp:.4f}")

    # Plotare Curbe ROC
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