# gui_frames.py

import bcrypt
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import subprocess
import os
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

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
        user_input = self.u.get()
        pass_input = self.p.get()

        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, password_hash, role FROM USERS WHERE username=%s", (user_input,))
            res = cursor.fetchone()
            conn.close()

            if res:
                user_id, stored_hash, role = res
                
                if bcrypt.checkpw(pass_input.encode('utf-8'), stored_hash.encode('utf-8')):
                    # Succes - setam datele de sesiune
                    self.controller.logged_user_id = user_id
                    self.controller.logged_user_role = role
                    self.controller.show_frame("DashboardFrame")
                else:
                    messagebox.showerror("Eroare", "Parola incorecta!")
            else:
                messagebox.showerror("Eroare", "Utilizator inexistent!")

        except Exception as e:
            messagebox.showerror("Eroare DB", f"Nu s-a putut efectua autentificarea: {str(e)}")

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Meniu Principal", font=("Arial", 18)).pack(pady=30)
        ttk.Button(self, text="Adauga Pacient si Predictie", command=lambda: controller.show_frame("PatientFormFrame")).pack(pady=5)
        ttk.Button(self, text="Istoric Predictii (Log)", command=lambda: controller.show_frame("HistoryFrame")).pack(pady=5)
        ttk.Button(self, text="Statistici Performanta", command=lambda: controller.show_frame("StatisticsFrame")).pack(pady=5)
        ttk.Button(self, text="Vizualizare Grafice Detaliate", command=self.run_learning_models).pack(pady=5)
        self.admin_btn = ttk.Button(self, text="Gestionare Medici (ADMIN)", command=lambda: controller.show_frame("AdminUserFrame"))
        ttk.Button(self, text="Delogare", command=lambda: controller.show_frame("LoginFrame")).pack(pady=20)

    def run_learning_models(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_path, "modeleInvatare.py")
            if os.path.exists(script_path):
                subprocess.Popen(["python", script_path])
            else: messagebox.showerror("Eroare", f"Fisierul nu a fost gasit la: {script_path}")
        except Exception as e: messagebox.showerror("Eroare", str(e))

    def refresh(self):
        if self.controller.logged_user_role == 'ADMIN': self.admin_btn.pack(pady=5)
        else: self.admin_btn.pack_forget()

class AdminUserFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Adaugare Medic Nou", font=("Arial", 16, "bold")).pack(pady=20)
        f = ttk.Frame(self)
        f.pack(pady=10)

       # camp Utilizator
        ttk.Label(f, text="Utilizator:").grid(row=0, column=0, pady=5, padx=5, sticky="e")
        self.new_u = ttk.Entry(f)
        self.new_u.grid(row=0, column=1, pady=5, padx=5)

        # camp parola - adaugam show="*"
        ttk.Label(f, text="Parola:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        self.new_p = ttk.Entry(f, show="*") 
        self.new_p.grid(row=1, column=1, pady=5, padx=5)

        self.var_p = tk.BooleanVar()
        self.check_p = ttk.Checkbutton(f, text="Arata parola", variable=self.var_p, command=self.toggle_p)
        self.check_p.grid(row=2, column=1, sticky="w")

        ttk.Button(self, text="Creeaza Cont", command=self.create_user).pack(pady=10)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

    def toggle_p(self):
        """functie care schimba intre show='*' si show=''"""
        if self.var_p.get():
            self.new_p.config(show="") # text normal
        else:
            self.new_p.config(show="*") # mascheaza text

    def create_user(self):
        u = self.new_u.get()
        p = self.new_p.get()
        
        if not u or not p:
            messagebox.showwarning("Atentie", "Completati toate campurile!")
            return

        # Hash-uirea parolei
        salt = bcrypt.gensalt()
        hashed_p = bcrypt.hashpw(p.encode('utf-8'), salt)

        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO USERS (username, password_hash, role) VALUES (%s, %s, 'MEDIC')", 
                        (u, hashed_p.decode('utf-8')))
            conn.commit()
            conn.close()
            messagebox.showinfo("Succes", f"Medicul {u} a fost adaugat!")
        except Exception as e:
            messagebox.showerror("Eroare DB", str(e))
            

class HistoryFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Istoric Predictii", font=("Arial", 16)).pack(pady=10)
        columns = ("nume", "cnp", "rezultat", "conf")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col.upper())
        self.tree.pack(fill="both", expand=True, padx=20)
        ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack(pady=10)

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = mysql.connector.connect(**self.controller.db_config)
        cursor = conn.cursor()

        cursor.execute("""
                    SELECT p.full_name, p.cnp_internal_id, pr.prediction_result, pr.confidence_score 
                    FROM PATIENTS p 
                    JOIN PREDICTIONS pr ON p.id = pr.patient_id 
                    ORDER BY pr.id DESC
                    """)
        for r in cursor.fetchall(): self.tree.insert("", "end", values=r)
        conn.close()

class PatientFormFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ttk.Label(self, text="Date Pacient", font=("Arial", 16)).pack(pady=10)
        self.p_ents = {"CNP": ttk.Entry(self), "Nume Complet": ttk.Entry(self), "Data Nasterii (YYYY-MM-DD)": ttk.Entry(self)}
        for k, v in self.p_ents.items():
            ttk.Label(self, text=k).pack(); v.pack()
        self.gen = ttk.Combobox(self, values=["Masculin", "Feminin"]); self.gen.pack()
        self.fields = ["Varsta", "Bilirubina T", "Bilirubina D", "Fosfataza", "ALT", "AST", "Proteine T", "Albumina", "Raport AG"]
        self.c_ents = {f: ttk.Entry(self) for f in self.fields}
        for f in self.fields: ttk.Label(self, text=f).pack(); self.c_ents[f].pack()
        self.algo = ttk.Combobox(self, values=["SVM", "MLP"]); self.algo.current(0); self.algo.pack()
        self.split = ttk.Combobox(self, values=["80% Train", "70% Train", "60% Train", "50% Train"]); self.split.current(0); self.split.pack()
        ttk.Button(self, text="Predictie", command=self.run).pack()

    def run(self):
        try:
            split_map = {"80% Train": 0.20, "70% Train": 0.30, "60% Train": 0.40, "50% Train": 0.50}
            sz = split_map[self.split.get()]
            clin_data = [float(self.c_ents["Varsta"].get()), 1 if self.gen.get()=="Masculin" else 0]
            for f in self.fields[1:]: clin_data.append(float(self.c_ents[f].get()))
            dp = self.controller.models_data[sz]
            sc = dp['SCALER'].transform(np.array(clin_data).reshape(1, -1))
            res = dp[self.algo.get()].predict(sc)[0]
            prob = dp[self.algo.get()].predict_proba(sc)[0][1]
            self.save_to_db(clin_data, res, prob)
            self.controller.frames["PredictionFrame"].set_result("RISC RIDICAT" if res == 1 else "RISC SCAZUT", prob, self.algo.get(), "high" if res==1 else "low")
            self.controller.show_frame("PredictionFrame")
        except Exception as e: messagebox.showerror("Eroare", str(e))

    def save_to_db(self, cl, r, pb):
        conn = mysql.connector.connect(**self.controller.db_config); cursor = conn.cursor()
        cnp = self.p_ents["CNP"].get()
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
        self.prb_lbl = ttk.Label(self, text="-"); self.prb_lbl.pack()
        self.box = tk.Label(self, text="STARE", width=25, height=3, fg="white"); self.box.pack(pady=30)
        ttk.Button(self, text="Dashboard", command=lambda: controller.show_frame("DashboardFrame")).pack()

    def set_result(self, txt, pb, mdl, risk):
        self.res_lbl.config(text=f"{txt} ({mdl})")
        self.prb_lbl.config(text=f"Probabilitate: {pb*100:.2f}%")
        self.box.config(text=risk.upper(), bg="red" if risk=="high" else "green")

class StatisticsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        self.txt = tk.Text(self, height=25, width=100); self.txt.pack()
        ttk.Button(self, text="Genereaza", command=self.show_stats).pack(); ttk.Button(self, text="Inapoi", command=lambda: controller.show_frame("DashboardFrame")).pack()

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