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
import bcrypt
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk 
import mysql.connector
import subprocess
import os
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from utils import validate_patient_data, calculate_age_from_dob

# Setari pentru aspectul vizual al interfetei grafice
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LoginFrame(ctk.CTkFrame):
    """
    Gestioneaza interfata de autentificare si validarea credentialelor utilizatorilor
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Autentificare Sistem", font=("Arial", 24, "bold")).pack(pady=40)

        container = ctk.CTkFrame(self)
        container.pack(pady=10, padx=20)

        ctk.CTkLabel(container, text="Utilizator:").grid(row=0, column=0, pady=10, padx=10)
        self.u = ctk.CTkEntry(container, width=200)
        self.u.grid(row=0, column=1, pady=10, padx=10)

        ctk.CTkLabel(container, text="Parola:").grid(row=1, column=0, pady=10, padx=10)
        self.p = ctk.CTkEntry(container, show="*", width=200)
        self.p.grid(row=1, column=1, pady=10, padx=10)

        ctk.CTkButton(self, text="Login", command=self.login).pack(pady=30)

    def login(self):
        """
        Verifica utilizatorul si parola in baza de date si initiaza sesiunea
        Returneaza: None, dar schimba frame-ul curent daca autentificarea reuseste
        """
        user_input = self.u.get()
        pass_input = self.p.get()
        try:
            # Se conecteaza la baza de date si cauta hash-ul parolei
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT id, password_hash, role FROM USERS WHERE username=%s", (user_input,))
            res = cursor.fetchone()
            conn.close()

            if res:
                user_id, stored_hash, role = res
                if bcrypt.checkpw(pass_input.encode('utf-8'), stored_hash.encode('utf-8')):
                    self.controller.logged_user_id = user_id
                    self.controller.logged_user_role = role
                    self.controller.show_frame("DashboardFrame")
                else: messagebox.showerror("Eroare", "Parola incorecta!")
            else: messagebox.showerror("Eroare", "Utilizator inexistent!")
        except Exception as e: messagebox.showerror("Eroare DB", str(e))

class DashboardFrame(ctk.CTkFrame):
    """
    Ecranul principal de navigare care ofera acces la functionalitatile aplicatiei in functie de rol
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Meniu Principal", font=("Arial", 22, "bold")).pack(pady=30)

        # Butoane stilizate
        btn_style = {"width": 300, "height": 40}
        ctk.CTkButton(self, text="Adauga Pacient si Predictie", command=lambda: controller.show_frame("PatientFormFrame"), **btn_style).pack(pady=10)
        ctk.CTkButton(self, text="Istoric Predictii (Log)", command=lambda: controller.show_frame("HistoryFrame"), **btn_style).pack(pady=10)
        ctk.CTkButton(self, text="Statistici Performanta", command=lambda: controller.show_frame("StatisticsFrame"), **btn_style).pack(pady=10)
        ctk.CTkButton(self, text="Vizualizare Grafice Detaliate", command=self.run_learning_models, **btn_style).pack(pady=10)

        self.admin_btn = ctk.CTkButton(self, text="Gestionare Medici (ADMIN)", fg_color="darkred", hover_color="red", command=lambda: controller.show_frame("AdminUserFrame"), **btn_style)

        ctk.CTkButton(self, text="Delogare", fg_color="gray", command=lambda: controller.show_frame("LoginFrame"), **btn_style).pack(pady=30)

    def refresh(self):
        """
        Actualizeaza interfata pentru a afisa butonul de admin doar daca utilizatorul are drepturi
        """
        if self.controller.logged_user_role == 'ADMIN': self.admin_btn.pack(pady=10)
        else: self.admin_btn.pack_forget()

    def run_learning_models(self):
        """
        Lanseaza scriptul extern pentru vizualizarea graficelor de invatare
        """
        try:
            # Executa scriptul modeleInvatare.py intr-un proces separat
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modeleInvatare.py")
            if os.path.exists(script_path): subprocess.Popen(["python", script_path])
            else: messagebox.showerror("Eroare", "Fisierul nu a fost gasit!")
        except Exception as e: messagebox.showerror("Eroare", str(e))

class AdminUserFrame(ctk.CTkFrame):
    """
    Interfata dedicata administratorilor pentru crearea conturilor noi de medici
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text="Adaugare Medic Nou", font=("Arial", 20)).pack(pady=20)

        f = ctk.CTkFrame(self)
        f.pack(pady=10, padx=20)

        self.new_u = ctk.CTkEntry(f, placeholder_text="Utilizator")
        self.new_u.pack(pady=10, padx=10)
        self.new_p = ctk.CTkEntry(f, placeholder_text="Parola", show="*")
        self.new_p.pack(pady=10, padx=10)

        ctk.CTkButton(self, text="Creeaza Cont", command=self.create_user).pack(pady=20)
        ctk.CTkButton(self, text="Inapoi", fg_color="transparent", border_width=2, command=lambda: controller.show_frame("DashboardFrame")).pack()

    def create_user(self):
        """
        Preia datele din formular si introduce un nou medic in baza de date cu parola criptata
        """
        u, p = self.new_u.get(), self.new_p.get()
        if not u or not p: return
        # Genereaza un hash securizat pentru parola inainte de stocare
        hashed_p = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt())
        try:
            conn = mysql.connector.connect(**self.controller.db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO USERS (username, password_hash, role) VALUES (%s, %s, 'MEDIC')", (u, hashed_p.decode('utf-8')))
            conn.commit(); conn.close()
            messagebox.showinfo("Succes", f"Medicul {u} adaugat!")
        except Exception as e: messagebox.showerror("Eroare DB", str(e))

class PatientFormFrame(ctk.CTkFrame): 
    """
    Formular complex pentru colectarea datelor clinice si rularea predictiei
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Introducere Date Pacient", font=("Arial", 22, "bold")).pack(pady=20)

        # Container pentru inputuri
        form_container = ctk.CTkFrame(self)
        form_container.pack(fill="both", expand=True, padx=40, pady=10)

        # Date Personale
        self.p_ents = {
            "CNP": ctk.CTkEntry(form_container, placeholder_text="CNP (13 cifre)", width=250),
            "Nume": ctk.CTkEntry(form_container, placeholder_text="Nume Complet", width=250),
            "Data": ctk.CTkEntry(form_container, placeholder_text="Data Nasterii (YYYY-MM-DD)", width=250)
        }
        for e in self.p_ents.values(): e.pack(pady=5)

        self.gen = ctk.CTkOptionMenu(form_container, values=["Masculin", "Feminin"], width=250)
        self.gen.pack(pady=5)

        # Date Clinice
        self.fields = ["Bilirubina T", "Bilirubina D", "Fosfataza", "ALT", "AST", "Proteine T", "Albumina", "Raport AG"]
        self.c_ents = {f: ctk.CTkEntry(form_container, placeholder_text=f, width=250) for f in self.fields}
        for f in self.fields: self.c_ents[f].pack(pady=2)

        # Selectie Model
        self.algo = ctk.CTkOptionMenu(self, values=["SVM", "MLP"])
        self.algo.pack(pady=5)
        self.split = ctk.CTkOptionMenu(self, values=["80% Train", "70% Train", "60% Train", "50% Train"])
        self.split.pack(pady=5)

        # Butoane
        ctk.CTkButton(self, text="Ruleaza Predictie", fg_color="green", hover_color="darkgreen", command=self.run).pack(pady=10)
        ctk.CTkButton(self, text="Inapoi la Meniu", fg_color="gray", command=lambda: controller.show_frame("DashboardFrame")).pack(pady=5)

    def run(self):
        """
        Orchestreaza fluxul de predictie validare date preprocesare si interogare model ML
        Returneaza: None, actualizeaza GUI cu rezultatul
        """
        try:
            # Calculeaza varsta pe baza datei nasterii pentru a fi folosita in algoritm
            dob_str = self.p_ents["Data"].get()
            calculated_age = calculate_age_from_dob(dob_str)
            
            if calculated_age is None:
                messagebox.showerror("Eroare Validare", "Formatul datei de naștere este invalid (trebuie YYYY-MM-DD)!")
                return

            raw_age = str(calculated_age) 

            # Colectare restul datelor din interfata
            raw_gen = self.gen.get()
            raw_tb = self.c_ents["Bilirubina T"].get()
            raw_db = self.c_ents["Bilirubina D"].get()
            raw_alk = self.c_ents["Fosfataza"].get()
            raw_alt = self.c_ents["ALT"].get()
            raw_ast = self.c_ents["AST"].get()
            raw_tp = self.c_ents["Proteine T"].get()
            raw_alb = self.c_ents["Albumina"].get()
            raw_ag = self.c_ents["Raport AG"].get()

            # Valideaza datele pacientului inainte de a le trimite la modelul ML
            is_valid, message = validate_patient_data(
                raw_age, raw_gen, raw_tb, raw_db, raw_alk,
                raw_alt, raw_ast, raw_tp, raw_alb, raw_ag
            )

            if not is_valid:
                messagebox.showerror("Eroare Validare", message)
                return

            # Procesare daca datele sunt valide
            split_map = {"80% Train": 0.20, "70% Train": 0.30, "60% Train": 0.40, "50% Train": 0.50}
            sz = split_map[self.split.get()]

            clin_data = [float(raw_age), 1 if raw_gen == "Masculin" else 0]
            for val in [raw_tb, raw_db, raw_alk, raw_alt, raw_ast, raw_tp, raw_alb, raw_ag]:
                clin_data.append(float(val))

            # Normalizeaza datele folosind scalerul antrenat si obtine predictia
            dp = self.controller.models_data[sz]
            sc = dp['SCALER'].transform(np.array(clin_data).reshape(1, -1))
            res = dp[self.algo.get()].predict(sc)[0]
            prob = dp[self.algo.get()].predict_proba(sc)[0][1]

            self.save_to_db(clin_data, res, prob)

            self.controller.frames["PredictionFrame"].set_result(
                "RISC RIDICAT" if res == 1 else "RISC SCAZUT",
                prob, self.algo.get(), "high" if res==1 else "low"
            )
            self.controller.show_frame("PredictionFrame")
        except Exception as e:
            messagebox.showerror("Eroare Date", f"A aparut o eroare: {str(e)}")

    def save_to_db(self, cl, r, pb):
        """
        Salveaza datele pacientului si rezultatul predictiei in baza de date MySQL
        """
        conn = mysql.connector.connect(**self.controller.db_config); cursor = conn.cursor()
        cnp = self.p_ents["CNP"].get()
        cursor.execute("INSERT IGNORE INTO PATIENTS (cnp_internal_id, full_name, gender, birth_date) VALUES (%s,%s,%s,%s)",
                       (cnp, self.p_ents["Nume"].get(), self.gen.get()[0], self.p_ents["Data"].get()))
        cursor.execute("SELECT id FROM PATIENTS WHERE cnp_internal_id=%s", (cnp,))
        pid = cursor.fetchone()[0]
        q = "INSERT INTO PREDICTIONS (patient_id, user_id, prediction_result, confidence_score, age, gender_val, total_bilirubin, direct_bilirubin, alkaline_phosphotase, alamine_aminotransferase, aspartate_aminotransferase, total_proteins, albumin, albumin_and_globulin_ratio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(q, (pid, self.controller.logged_user_id, int(r), float(pb), cl[0], cl[1], *cl[2:]))
        conn.commit(); conn.close()

class PredictionFrame(ctk.CTkFrame):
    """
    Afiseaza rezultatul clasificarii riscului si probabilitatea asociata
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.res_lbl = ctk.CTkLabel(self, text="-", font=("Arial", 28, "bold"))
        self.res_lbl.pack(pady=40)
        self.prb_lbl = ctk.CTkLabel(self, text="-", font=("Arial", 16))
        self.prb_lbl.pack()

        self.box = ctk.CTkLabel(self, text="STARE", width=200, height=60, corner_radius=10, text_color="white")
        self.box.pack(pady=40)

        ctk.CTkButton(self, text="Inapoi la Dashboard", command=lambda: controller.show_frame("DashboardFrame")).pack(pady=10)
        ctk.CTkButton(self, text="Adauga alt Pacient", fg_color="transparent", border_width=2, command=lambda: controller.show_frame("PatientFormFrame")).pack()

    def set_result(self, txt, pb, mdl, risk):
        """
        Actualizeaza elementele vizuale cu datele obtinute in urma predictiei
        """
        self.res_lbl.configure(text=f"{txt}\n({mdl})")
        self.prb_lbl.configure(text=f"Probabilitate: {pb*100:.2f}%")
        color = "#e74c3c" if risk=="high" else "#2ecc71" 
        self.box.configure(text=risk.upper(), fg_color=color)

class HistoryFrame(ctk.CTkFrame):
    """
    Vizualizeaza istoricul predictiilor efectuate sub forma tabelara
    """
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ctk.CTkLabel(self, text="Istoric Predictii", font=("Arial", 20)).pack(pady=10)

        # Treeview ramane din tkinter normal, dar il punem intrun frame ctk
        columns = ("nume", "cnp", "rezultat", "conf")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col.upper())
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkButton(self, text="Inapoi la Meniu", command=lambda: controller.show_frame("DashboardFrame")).pack(pady=10)

    def refresh(self):
        """
        Incarca ultimele inregistrari din baza de date in tabelul Treeview
        """
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = mysql.connector.connect(**self.controller.db_config); cursor = conn.cursor()
        cursor.execute("SELECT p.full_name, p.cnp_internal_id, pr.prediction_result, pr.confidence_score FROM PATIENTS p JOIN PREDICTIONS pr ON p.id = pr.patient_id ORDER BY pr.id DESC")
        for r in cursor.fetchall(): self.tree.insert("", "end", values=r)
        conn.close()

class StatisticsFrame(ctk.CTkFrame):
    """
    Genereaza rapoarte statistice despre setul de date si performanta modelelor
    """
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller
        ctk.CTkLabel(self, text="Statistici si Performanta", font=("Arial", 20)).pack(pady=10)

        self.txt = ctk.CTkTextbox(self, width=800, height=400)
        self.txt.pack(padx=20, pady=10, fill="both", expand=True)

        btn_f = ctk.CTkFrame(self, fg_color="transparent")
        btn_f.pack(pady=10)
        ctk.CTkButton(btn_f, text="Genereaza Raport", command=self.show_stats).pack(side="left", padx=10)
        ctk.CTkButton(btn_f, text="Inapoi", fg_color="gray", command=lambda: controller.show_frame("DashboardFrame")).pack(side="left", padx=10)

    def show_stats(self):
        """
        Descarca setul de date calculeaza statistici descriptive si evalueaza acuratetea modelelor
        """
        try:
            url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
            cols = ['Age', 'Gender', 'TB', 'DB', 'Alk', 'Sgpt', 'Sgot', 'TP', 'ALB', 'AG', 'Dataset']
            df = pd.read_csv(url, names=cols, header=None).dropna()
            # Transforma etichetele text in valori numerice pentru analiza
            df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1})
            df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})
            X_all = df.drop('Dataset', axis=1); Y_all = df['Dataset']
            
            #Sectiunea A: Statistici Descriptive
            # Calculeaza media varianta minimul si maximul pentru fiecare atribut
            desc = X_all.describe().T[['mean', 'std', 'min', 'max']]
            desc['variance'] = desc['std'] ** 2
            report = "A. STATISTICI DESCRIPTIVE\n"
            report += f"{'Atribut':<15} | {'Media':<8} | {'Var':<8} | {'Min':<6} | {'Max':<6}\n" + "-"*55 + "\n"
            for idx, row in desc.iterrows():
                report += f"{idx:<15} | {row['mean']:.2f} | {row['variance']:.2f} | {row['min']:.1f} | {row['max']:.1f}\n"

            #Sectiunea B: Performanta
            report += "\nB. PERFORMANTA MODELE\n"
            report += f"{'SPLIT':<10} | {'MDL':<5} | {'ACC':<7} | {'F1':<7}\n" + "-"*40 + "\n"
            for sz in self.controller.test_sizes:
                data = self.controller.models_data[sz]
                X_scaled = data['SCALER'].transform(X_all)
                for name in ['SVM', 'MLP']:
                    y_pred = data[name].predict(X_scaled)
                    acc, f1 = accuracy_score(Y_all, y_pred), f1_score(Y_all, y_pred)
                    report += f"{int((1-sz)*100)}/{(int(sz*100)):<5} | {name:<5} | {acc:.4f} | {f1:.4f}\n"

            self.txt.delete("1.0", tk.END); self.txt.insert(tk.END, report)
        except Exception as e: messagebox.showerror("Eroare", str(e))