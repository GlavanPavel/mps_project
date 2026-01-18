# ml_logic.py
import os
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

class MLHandler:
    def __init__(self, test_sizes):
        self.test_sizes = test_sizes
        self.models_data = {}

    def initialize_ml_logic(self):
        if not os.path.exists("models"): os.makedirs("models")
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
        cols = ['Age', 'Gender', 'TB', 'DB', 'Alk', 'Sgpt', 'Sgot', 'TP', 'ALB', 'AG', 'Dataset']
        try:
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
                
                if all(os.path.exists(path) for path in f_paths.values()):
                    self.models_data[size] = {
                        'SVM': joblib.load(f_paths['SVM']), 
                        'MLP': joblib.load(f_paths['MLP']), 
                        'SCALER': joblib.load(f_paths['SC'])
                    }
                else:
                    self.train_split(df, size, f_paths)
            return self.models_data
        except Exception as e:
            print(f"Eroare ML: {e}")
            return {}

    def train_split(self, df, size, f_paths):
        X = df.drop('Dataset', axis=1); Y = df['Dataset']
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)
        sc = StandardScaler(); X_tr_s = sc.fit_transform(X_train)
        
        svm = SVC(kernel='rbf', probability=True, random_state=42)
        # Am marit max_iter la 1000 pentru a evita eroarea de convergenta
        mlp = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=1000, random_state=42)
        
        svm.fit(X_tr_s, y_train); mlp.fit(X_tr_s, y_train)
        
        joblib.dump(svm, f_paths['SVM'])
        joblib.dump(mlp, f_paths['MLP'])
        joblib.dump(sc, f_paths['SC'])
        self.models_data[size] = {'SVM': svm, 'MLP': mlp, 'SCALER': sc}