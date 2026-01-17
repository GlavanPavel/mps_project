import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Suport Decizional - Liver Disease 2026")
        self.geometry("1200x900")

        self.db_config = {
            'host': '127.0.0.1', 'port': 3309, 'user': 'user', 'password': 'user', 'database': 'liver_disease'
        }
        
        self.logged_user_id = None
        self.logged_user_role = None # Retinem daca e 'admin' sau 'medic'
        self.test_sizes = [0.20, 0.30, 0.40, 0.50]
        self.models_data = {}
        
        self.initialize_ml_logic()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}

        # Am adaugat AdminPanelFrame in lista
        for F in (LoginFrame, DashboardFrame, PatientFormFrame, PredictionFrame, 
                  StatisticsFrame, HistoryFrame, AdminPanelFrame):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

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
                f = {'SVM': f"models/svm_{suffix}.pkl", 'MLP': f"models/mlp_{suffix}.pkl", 'SC': f"models/scaler_{suffix}.pkl"}
                if not all(os.path.exists(path) for path in f.values()):
                    self.train_split(df, size, f)
                self.models_data[size] = {'SVM': joblib.load(f['SVM']), 'MLP': joblib.load(f['MLP']), 'SCALER': joblib.load(f['SC'])}
        except Exception as e: print(f"Eroare ML: {e}")

    def train_split(self, df, size, f):
        X = df.drop('Dataset', axis=1); Y = df['Dataset']
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)
        sc = StandardScaler(); X_tr_s = sc.fit_transform(X_train)
        svm = SVC(kernel='rbf', probability=True, random_state=42)
        mlp = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
        svm.fit(X_tr_s, y_train); mlp.fit(X_tr_s, y_train)
        joblib.dump(svm, f['SVM']); joblib.dump(mlp, f['MLP']); joblib.dump(sc, f['SC'])

    def show_frame(self, name):
        if name == "DashboardFrame":
            self.frames[name].update_view() # Actualizam butoanele in functie de rol
        self.frames[name].tkraise()

# --- LOGIN ---
class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Autentificare Sistem", font=("Arial", 22, "bold")).pack(pady=50)
        f = ttk.Frame(self); f.pack()
        ttk.Label(f, text="Username:").grid(row=0, column=0, pady=5)
        self.u = ttk.Entry(f); self.u.grid(row=0, column=1)
        ttk.Label(f, text="Parola:").grid(row=1, column=0, pady=5)
        self.p = ttk.Entry(f, show="*"); self.p.grid(row=1, column=1)
        ttk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            # Selectam si rolul din baza de date
            cursor.execute("SELECT id, role FROM USERS WHERE username=%s AND password_hash=%s", (self.u.get(), self.p.get()))
            res = cursor.fetchone()
            if res:
                self.controller.logged_user_id = res[0]
                self.controller.logged_user_role = res[1] # 'admin' sau 'medic'
                self.controller.show_frame("DashboardFrame")
            else: messagebox.showerror("Eroare", "Utilizator sau parola gresita!")
            conn.close()
        except Exception as e: messagebox.showerror("Eroare DB", str(e))

# --- DASHBOARD DINAMIC ---
class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        self.lbl = ttk.Label(self, text="Meniu Principal", font=("Arial", 18, "bold"))
        self.lbl.pack(pady=30)
        
        self.btn_admin = ttk.Button(self, text="Administrare Conturi", command=lambda: controller.show_frame("AdminPanelFrame"))
        ttk.Button(self, text="Predictie Pacient Nou", command=lambda: controller.show_frame("PatientFormFrame")).pack(pady=5)
        ttk.Button(self, text="Istoric si Log Pacienti", command=lambda: controller.show_frame("HistoryFrame")).pack(pady=5)
        ttk.Button(self, text="Statistici Modele", command=lambda: controller.show_frame("StatisticsFrame")).pack(pady=5)
        ttk.Button(self, text="Delogare", command=lambda: controller.show_frame("LoginFrame")).pack(pady=20)

    def update_view(self):
        # Daca utilizatorul este admin, afisam butonul de administrare
        if self.controller.logged_user_role == 'admin':
            self.btn_admin.pack(pady=5, before=self.lbl.master.children.get('!button5')) # Pozitionare buton
        else:
            self.btn_admin.pack_forget()

# --- PANOUL DE ADMINISTRARE (CREARE CONTURI) ---
class AdminPanelFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Administrare: Creare Cont Medic", font=("Arial", 16, "bold")).pack(pady=20)
        
        f = ttk.Frame(self); f.pack(pady=10)
        ttk.Label(f, text="Username Nou:").grid(row=0, column=0, pady=5, sticky="e")
        self.new_u = ttk.Entry(f); self.new_u.grid(row=0, column=1, pady=5)
        
        ttk.Label(f, text="Parola Noua:").grid(row=1, column=0, pady=5, sticky="e")
        self.new_p = ttk.Entry(f); self.new_p.grid(row=1, column=1, pady=5)
        
        ttk.Label(f, text="Rol:").grid(row=2, column=0, pady=5, sticky="e")
        self.role_sel = ttk.Combobox(f, values=["medic", "admin"], state="readonly")
        self.role_sel.current(0); self.role_sel.grid(row=2, column=1, pady=5)
        
        ttk.Button(self, text="Salveaza Cont Nou", command=self.create_user).pack(pady=20)
        ttk.Button(self, text="Inapoi la Dashboard", command=lambda: controller.show_frame("DashboardFrame")).pack()

    def create_user(self):
        u = self.new_u.get().strip()
        p = self.new_p.get().strip()
        r = self.role_sel.get()
        
        if not u or not p:
            messagebox.showwarning("Atentie", "Completati toate campurile!"); return
            
        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            # Inseram noul utilizator
            cursor.execute("INSERT INTO USERS (username, password_hash, role) VALUES (%s, %s, %s)", (u, p, r))
            conn.commit(); conn.close()
            messagebox.showinfo("Succes", f"Contul pentru {u} a fost creat cu rolul de {r}!")
            self.new_u.delete(0, tk.END); self.new_p.delete(0, tk.END)
        except Exception as e: messagebox.showerror("Eroare", f"Nu s-a putut crea contul: {e}")

# --- (RESTUL CLASELOR: PatientFormFrame, PredictionFrame, StatisticsFrame, HistoryFrame ramana la fel) ---
# ... (Se pastreaza codul anterior pentru aceste pagini) ...

class HistoryFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Istoric Log-uri", font=("Arial", 16)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("CNP", "Nume", "Status"), show='headings')
        self.tree.heading("CNP", text="CNP"); self.tree.heading("Nume", text="Nume"); self.tree.heading("Status", text="Predictie")
        self.tree.pack(fill="both", expand=True, padx=10); ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

class PatientFormFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Formular Analize", font=("Arial", 16)).pack(pady=20)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

class PredictionFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Rezultat", font=("Arial", 20)).pack(pady=50)
        ttk.Button(self, text="Dashboard", command=lambda: controller.show_frame("DashboardFrame")).pack()

class StatisticsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Statistici", font=("Arial", 16)).pack(pady=20)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

if __name__ == "__main__":
    app = App(); app.mainloop()