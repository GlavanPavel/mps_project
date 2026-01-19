##########################################################################
#                                                                        #
#  Copyright:   (c) 2026, Proiect MPS                                    #
#  Autori:      Albu A. Sorin (R.Moldova) 1409A                          #
#               Glavan P. Pavel (R.Moldova) 1409A                        #
#               Duda I.I. Andrei-Ionuț 1409A                             #
#               Jireadă C. Teodor 1409A                                  #
#               Popovici I.L. Andrei 1409A                               #
#               Noroc D. Sorin (R.Moldova) 1409A                         #
#               Timofte C. Constantin 1409A                              #
#               Matei I. Ion (R.Moldova) 1410B                           #
#                                                                        #
#  Descriere:   Sistem Expert pentru Predictia Bolilor Hepatice          #
#               Utilizand algoritmii SVM si Multilayer Perceptron (MLP)  #
#               Bazat pe setul de date ILPD (Indian Liver Patient)       #
#                                                                        #
#  Acest cod si informatiile sunt oferite "ca atare" fara nicio garantie #
#  de orice fel, exprimata sau implicita. Acest proiect este realizat    #
#  in scop didactic pentru disciplina Managementul Proiectelor Software. #
#                                                                        #
##########################################################################
import os
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

class MLHandler:
    """
    Gestioneaza intregul flux de lucru ML de la incarcarea datelor la antrenare si salvare
    """
    def __init__(self, test_sizes):
        self.test_sizes = test_sizes
        self.models_data = {}

    def initialize_ml_logic(self):
        """
        Pregateste mediul de lucru si asigura disponibilitatea modelelor antrenate
        Returneaza dictionar cu modelele incarcate sau nou antrenate
        """
        # Verifica daca directorul pentru modele exista si il creeaza daca e necesar
        if not os.path.exists("models"): os.makedirs("models")
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
        cols = ['Age', 'Gender', 'TB', 'DB', 'Alk', 'Sgpt', 'Sgot', 'TP', 'ALB', 'AG', 'Dataset']
        try:
            # Incarca setul
            df = pd.read_csv(url, names=cols, header=None).dropna()
            df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1})
            df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})
            
            for size in self.test_sizes:
                suffix = str(int(size * 100))
                f_paths = {
                    'SVM': f"models/svm_{suffix}.pkl", 
                    'MLP': f"models/mlp_{suffix}.pkl", 
                    'SC': f"models/scaler_{suffix}.pkl"
                }
                # Verifica daca modelele exista deja pe disc
                if all(os.path.exists(path) for path in f_paths.values()):
                    self.models_data[size] = {
                        'SVM': joblib.load(f_paths['SVM']), 
                        'MLP': joblib.load(f_paths['MLP']), 
                        'SCALER': joblib.load(f_paths['SC'])
                    }
                else:
                    # Antreneaza modelele de la zero daca fisierele nu sunt gasite
                    self.train_split(df, size, f_paths)
            return self.models_data
        except Exception as e:
            print(f"Eroare ML: {e}")
            return {}

    def train_split(self, df, size, f_paths):
        """
        Realizeaza impartirea datelor scalarea si antrenarea a algoritmilor
        """
        X = df.drop('Dataset', axis=1); Y = df['Dataset']
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)
    
        sc = StandardScaler(); X_tr_s = sc.fit_transform(X_train)
        
        #SVM si MLP 
        svm = SVC(kernel='rbf', probability=True, random_state=42)
        mlp = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=1000, random_state=42)
        
        # Antreneaza ambele modele 
        svm.fit(X_tr_s, y_train); mlp.fit(X_tr_s, y_train)
        
        # salveaza modelele 
        joblib.dump(svm, f_paths['SVM'])
        joblib.dump(mlp, f_paths['MLP'])
        joblib.dump(sc, f_paths['SC'])
        self.models_data[size] = {'SVM': svm, 'MLP': mlp, 'SCALER': sc}