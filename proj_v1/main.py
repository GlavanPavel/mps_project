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

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Suport Decizional - Liver Disease 2026")
        self.geometry("1100x850")

        self.db_config = {
            'host': '127.0.0.1', 'port': 3309, 'user': 'user', 'password': 'user', 'database': 'liver_disease'
        }
        
        self.logged_user_id = None
        self.logged_user_role = None # Retinem rolul
        self.test_sizes = [0.20, 0.30, 0.40, 0.50]
        self.models_data = {}
        
        self.initialize_ml_logic()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}

        # Am adaugat AdminUserFrame si HistoryFrame
        for F in (LoginFrame, DashboardFrame, PatientFormFrame, PredictionFrame, StatisticsFrame, AdminUserFrame, HistoryFrame):
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
                if all(os.path.exists(path) for path in f.values()):
                    self.models_data[size] = {'SVM': joblib.load(f['SVM']), 'MLP': joblib.load(f['MLP']), 'SCALER': joblib.load(f['SC'])}
                else: self.train_split(df, size, f)
        except Exception as e: print(f"Eroare ML: {e}")

    def train_split(self, df, size, f):
        X = df.drop('Dataset', axis=1); Y = df['Dataset']
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size, random_state=42, stratify=Y)
        sc = StandardScaler(); X_tr_s = sc.fit_transform(X_train)
        svm = SVC(kernel='rbf', probability=True, random_state=42)
        mlp = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
        svm.fit(X_tr_s, y_train); mlp.fit(X_tr_s, y_train)
        joblib.dump(svm, f['SVM']); joblib.dump(mlp, f['MLP']); joblib.dump(sc, f['SC'])
        self.models_data[size] = {'SVM': svm, 'MLP': mlp, 'SCALER': sc}

    def show_frame(self, name):
        frame = self.frames[name]
        if hasattr(frame, "refresh"): frame.refresh() # Refresh la date cand afisam frame-ul
        frame.tkraise()

class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Autentificare Sistem", font=("Arial", 20, "bold")).pack(pady=50)
        f = ttk.Frame(self); f.pack()
        ttk.Label(f, text="Utilizator:").grid(row=0, column=0, pady=5)
        self.u = ttk.Entry(f); self.u.grid(row=0, column=1)
        ttk.Label(f, text="Parola:").grid(row=1, column=0, pady=5)
        self.p = ttk.Entry(f, show="*"); self.p.grid(row=1, column=1)
        ttk.Button(self, text="Login", command=self.login).pack(pady=20)

    def login(self):
        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            # Selectam si ROLUL
            cursor.execute("SELECT id, role FROM USERS WHERE username=%s AND password_hash=%s", (self.u.get(), self.p.get()))
            res = cursor.fetchone()
            if res:
                self.controller.logged_user_id = res[0]
                self.controller.logged_user_role = res[1]
                self.controller.show_frame("DashboardFrame")
            else: messagebox.showerror("Eroare", "Utilizator sau parola gresita!")
            conn.close()
        except Exception as e: messagebox.showerror("Eroare DB", str(e))

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        self.lbl = ttk.Label(self, text="Meniu Principal", font=("Arial", 18))
        self.lbl.pack(pady=30)
        
        ttk.Button(self, text="Adauga Pacient si Predictie", command=lambda: controller.show_frame("PatientFormFrame")).pack(pady=5)
        ttk.Button(self, text="Istoric Predictii (Log)", command=lambda: controller.show_frame("HistoryFrame")).pack(pady=5)
        ttk.Button(self, text="Statistici Performanta", command=lambda: controller.show_frame("StatisticsFrame")).pack(pady=5)
        
        # Buton vizibil doar pentru admin
        self.admin_btn = ttk.Button(self, text="Gestionare Medici (ADMIN)", command=lambda: controller.show_frame("AdminUserFrame"))
        self.admin_btn.pack(pady=5)
        
        ttk.Button(self, text="Delogare", command=lambda: controller.show_frame("LoginFrame")).pack(pady=20)

    def refresh(self):
        # Ascundem sau afisam butonul de admin in functie de cine s-a logat
        if self.controller.logged_user_role == 'ADMIN':
            self.admin_btn.pack(pady=5)
        else:
            self.admin_btn.pack_forget()

class AdminUserFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Adaugare Medic Nou", font=("Arial", 16, "bold")).pack(pady=20)
        
        f = ttk.Frame(self); f.pack(pady=10)
        ttk.Label(f, text="Username Medic:").grid(row=0, column=0, padx=5, pady=5)
        self.new_u = ttk.Entry(f); self.new_u.grid(row=0, column=1)
        ttk.Label(f, text="Parola:").grid(row=1, column=0, padx=5, pady=5)
        self.new_p = ttk.Entry(f); self.new_p.grid(row=1, column=1)
        
        ttk.Button(self, text="Creeaza Cont", command=self.create_user).pack(pady=10)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

    def create_user(self):
        u, p = self.new_u.get(), self.new_p.get()
        if not u or not p: 
            messagebox.showwarning("Atentie", "Completati ambele campuri!"); return
        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO USERS (username, password_hash, role) VALUES (%s, %s, 'MEDIC')", (u, p))
            conn.commit(); conn.close()
            messagebox.showinfo("Succes", f"Medicul {u} a fost adaugat!")
            self.new_u.delete(0, tk.END); self.new_p.delete(0, tk.END)
        except Exception as e: messagebox.showerror("Eroare", str(e))

class HistoryFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Istoric Predictii Pacienti", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Tabel pentru afisarea datelor solicitate
        columns = ("nume", "cnp", "rezultat", "conf")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.heading("nume", text="Nume Complet")
        self.tree.heading("cnp", text="CNP")
        self.tree.heading("rezultat", text="Predictie")
        self.tree.heading("conf", text="Incredere (%)")
        
        self.tree.column("nume", width=250)
        self.tree.column("cnp", width=150)
        self.tree.column("rezultat", width=150)
        self.tree.column("conf", width=100)
        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        ttk.Button(self, text="Actualizeaza Date", command=self.refresh).pack(pady=5)
        ttk.Button(self, text="Inapoi la Dashboard", command=lambda: controller.show_frame("DashboardFrame")).pack(pady=10)

    def refresh(self):
        # Curatam tabelul
        for i in self.tree.get_children(): self.tree.delete(i)
        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            # JOIN intre PATIENTS si PREDICTIONS
            query = """
                SELECT p.full_name, p.cnp_internal_id, pr.prediction_result, pr.confidence_score 
                FROM PATIENTS p
                JOIN PREDICTIONS pr ON p.id = pr.patient_id
                ORDER BY pr.id DESC
            """
            cursor.execute(query)
            for (nume, cnp, res, conf) in cursor.fetchall():
                txt_res = "RISC RIDICAT" if res == 1 else "RISC SCAZUT"
                self.tree.insert("", tk.END, values=(nume, cnp, txt_res, f"{conf*100:.2f}%"))
            conn.close()
        except Exception as e: messagebox.showerror("Eroare Log", str(e))

# ... (PatientFormFrame, PredictionFrame si StatisticsFrame raman in mare parte la fel ca in codul tau initial)
# ... Din ratiuni de spatiu am inclus doar partile modificate structural mai sus.

class PatientFormFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Formular Date Pacient", font=("Arial", 16, "bold")).pack(pady=10)
        id_f = ttk.LabelFrame(self, text="Identitate")
        id_f.pack(fill="x", padx=20, pady=5)
        self.p_ents = {}
        for t, r, c in [("CNP", 0, 0), ("Nume Complet", 0, 2), ("Data Nasterii (YYYY-MM-DD)", 1, 0)]:
            ttk.Label(id_f, text=t+":").grid(row=r, column=c, padx=5, pady=5, sticky="e")
            en = ttk.Entry(id_f, width=22); en.grid(row=r, column=c+1, padx=5, pady=5); self.p_ents[t] = en
        self.gen = ttk.Combobox(id_f, values=["Masculin", "Feminin"], state="readonly", width=19); self.gen.current(0); self.gen.grid(row=1, column=3, padx=5)
        cl_f = ttk.LabelFrame(self, text="Date Clinice"); cl_f.pack(fill="x", padx=20, pady=5)
        self.fields = ["Varsta", "Bilirubina T", "Bilirubina D", "Fosfataza", "ALT", "AST", "Proteine T", "Albumina", "Raport AG"]
        self.c_ents = {}
        for i, t in enumerate(self.fields):
            r, c = divmod(i, 2); ttk.Label(cl_f, text=t+":").grid(row=r, column=c*2, padx=5, pady=2, sticky="e")
            en = ttk.Entry(cl_f, width=15); en.grid(row=r, column=c*2+1, padx=5, pady=2); self.c_ents[t] = en
        sel_f = ttk.Frame(self); sel_f.pack(pady=10)
        self.algo = ttk.Combobox(sel_f, values=["SVM", "MLP"], state="readonly", width=10); self.algo.current(0); self.algo.grid(row=0, column=0, padx=5)
        self.split = ttk.Combobox(sel_f, values=["80% Train", "70% Train", "60% Train", "50% Train"], state="readonly", width=15); self.split.current(0); self.split.grid(row=0, column=1, padx=5)
        ttk.Button(self, text="Ruleaza Analiza", command=self.run).pack(pady=10)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

    def run(self):
        try:
            cnp = self.p_ents["CNP"].get().strip()
            if len(cnp) != 13: messagebox.showwarning("Atentie", "CNP invalid"); return
            split_map = {"80% Train": 0.20, "70% Train": 0.30, "60% Train": 0.40, "50% Train": 0.50}
            sz = split_map[self.split.get()]
            clin_data = [float(self.c_ents["Varsta"].get()), 1 if self.gen.get()=="Masculin" else 0]
            for f in self.fields[1:]: clin_data.append(float(self.c_ents[f].get()))
            dp = self.controller.models_data[sz]
            sc = dp['SCALER'].transform(np.array(clin_data).reshape(1, -1))
            res = dp[self.algo.get()].predict(sc)[0]
            prob = dp[self.algo.get()].predict_proba(sc)[0][1]
            self.save_to_db(cnp, clin_data, res, prob)
            self.controller.frames["PredictionFrame"].set_result("RISC RIDICAT" if res == 1 else "RISC SCAZUT", prob, self.algo.get(), "high" if res==1 else "low")
            self.controller.show_frame("PredictionFrame")
        except Exception as e: messagebox.showerror("Eroare", f"Date invalide: {e}")

    def save_to_db(self, cnp, cl, r, pb):
        conn = mysql.connector.connect(**self.controller.db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO PATIENTS (cnp_internal_id, full_name, gender, birth_date) VALUES (%s,%s,%s,%s)", (cnp, self.p_ents["Nume Complet"].get(), self.gen.get()[0], self.p_ents["Data Nasterii (YYYY-MM-DD)"].get()))
        cursor.execute("SELECT id FROM PATIENTS WHERE cnp_internal_id=%s", (cnp,))
        pid = cursor.fetchone()[0]
        q = "INSERT INTO PREDICTIONS (patient_id, user_id, prediction_result, confidence_score, age, gender_val, total_bilirubin, direct_bilirubin, alkaline_phosphotase, alamine_aminotransferase, aspartate_aminotransferase, total_proteins, albumin, albumin_and_globulin_ratio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(q, (pid, self.controller.logged_user_id, int(r), float(pb), cl[0], cl[1], *cl[2:]))
        conn.commit(); conn.close()

class PredictionFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        self.res_lbl = ttk.Label(self, text="-", font=("Arial", 20, "bold")); self.res_lbl.pack(pady=40)
        self.prb_lbl = ttk.Label(self, text="-", font=("Arial", 12)); self.prb_lbl.pack()
        self.box = tk.Label(self, text="STARE", width=25, height=3, fg="white", font=("Arial", 12, "bold")); self.box.pack(pady=30)
        btn_f = ttk.Frame(self); btn_f.pack(pady=20)
        ttk.Button(btn_f, text="Dashboard", command=lambda: controller.show_frame("DashboardFrame")).pack()

    def set_result(self, txt, pb, mdl, risk):
        self.res_lbl.config(text=f"{txt} ({mdl})")
        self.prb_lbl.config(text=f"Probabilitate: {pb*100:.2f}%")
        self.box.config(text=risk.upper(), bg="red" if risk=="high" else "green")

class StatisticsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Raport Performanta Modele", font=("Arial", 16, "bold")).pack(pady=10)
        self.txt = tk.Text(self, height=25, width=100, font=("Courier", 9)); self.txt.pack(padx=10, pady=10)
        ttk.Button(self, text="Genereaza", command=self.show_stats).pack(side="left", padx=20)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack(side="left")
    def show_stats(self):
        try:
            url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
            cols = ['Age', 'Gender', 'TB', 'DB', 'Alk', 'Sgpt', 'Sgot', 'TP', 'ALB', 'AG', 'Dataset']
            df = pd.read_csv(url, names=cols, header=None).dropna()
            df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1})
            df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})
            X_all = df.drop('Dataset', axis=1); Y_all = df['Dataset']
            
            report = f"{'SPLIT':<10} | {'MDL':<5} | {'ACC':<7} | {'PRE':<7} | {'REC':<7} | {'F1':<7}\n" + "-"*65 + "\n"
            cm_details = "\nMATRICE DE CONFUZIE DETALIATA (S=Sanatos, B=Bolnav):\n"

            for sz in self.controller.test_sizes:
                data = self.controller.models_data[sz]
                X_scaled = data['SCALER'].transform(X_all)
                for name in ['SVM', 'MLP']:
                    y_pred = data[name].predict(X_scaled)
                    acc = accuracy_score(Y_all, y_pred)
                    pre = precision_score(Y_all, y_pred)
                    rec = recall_score(Y_all, y_pred)
                    f1 = f1_score(Y_all, y_pred)
                    cm = confusion_matrix(Y_all, y_pred)
                    
                    split_label = f"{int((1-sz)*100)}/{int(sz*100)}"
                    report += f"{split_label:<10} | {name:<5} | {acc:.4f} | {pre:.4f} | {rec:.4f} | {f1:.4f}\n"
                    
                    cm_details += f"\n[{name} - Split {split_label}]:\n"
                    cm_details += f"        Pred:S  Pred:B\n"
                    cm_details += f"Real:S  {cm[0][0]:<8} {cm[0][1]:<8}\n"
                    cm_details += f"Real:B  {cm[1][0]:<8} {cm[1][1]:<8}\n"

            self.txt.delete("1.0", tk.END); self.txt.insert(tk.END, report + cm_details)
        except Exception as e: messagebox.showerror("Eroare", str(e))

if __name__ == "__main__":
    app = App(); app.mainloop()