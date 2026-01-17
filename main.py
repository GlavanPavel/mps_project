import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem de Suport Decizional - Boală Hepatică")
        self.geometry("900x600")

        # Container pentru "ecrane"
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # --- AICI am adăugat StatisticsFrame în listă ---
        for F in (LoginFrame, DashboardFrame, PatientFormFrame,
                  PredictionFrame, StatisticsFrame, AdminFrame):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

    def set_prediction_result(self, label_text, probability, model_name, risk_level):
        """Actualizează ecranul de predicție cu valori mock."""
        frame: PredictionFrame = self.frames["PredictionFrame"]
        frame.set_result(label_text, probability, model_name, risk_level)


class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        title = ttk.Label(self, text="Autentificare utilizator",
                          font=("Segoe UI", 20, "bold"))
        title.pack(pady=40)

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Utilizator:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        ttk.Label(form, text="Parolă:").grid(row=1, column=0, sticky="e", pady=5, padx=5)

        self.username_entry = ttk.Entry(form, width=30)
        self.password_entry = ttk.Entry(form, width=30, show="*")

        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        btn_login = ttk.Button(self, text="Autentificare",
                               command=self.login)
        btn_login.pack(pady=20)

        ttk.Label(self, text="Rol: MEDIC / ADMINISTRATOR (mock)").pack()

    def login(self):
        # Logică mock – orice user/parolă este acceptat
        if not self.username_entry.get():
            messagebox.showwarning("Atenție", "Introduceți numele de utilizator.")
            return
        self.controller.show_frame("DashboardFrame")


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=10)

        ttk.Label(header, text="Dashboard principal",
                  font=("Segoe UI", 18, "bold")).pack(side="left")

        ttk.Button(header, text="Delogare",
                   command=lambda: controller.show_frame("LoginFrame")).pack(side="right")

        body = ttk.Frame(self)
        body.pack(expand=True)

        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=20)

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=20)

        ttk.Label(left, text="Meniu", font=("Segoe UI", 12, "bold")).pack(pady=10)

        ttk.Button(left, text="Introducere date pacient",
                   command=lambda: controller.show_frame("PatientFormFrame")).pack(fill="x", pady=5)

        ttk.Button(left, text="Predicție curentă",
                   command=lambda: controller.show_frame("PredictionFrame")).pack(fill="x", pady=5)

        # --- NOU: buton pentru ecranul de Analiză Statistică ---
        ttk.Button(left, text="Analiză statistică și comparații ML",
                   command=lambda: controller.show_frame("StatisticsFrame")).pack(fill="x", pady=5)

        ttk.Button(left, text="Panou administrare",
                   command=lambda: controller.show_frame("AdminFrame")).pack(fill="x", pady=5)

        ttk.Button(left, text="Ieșire",
                   command=self.quit_app).pack(fill="x", pady=5)

        # Zonă de "statistici" mock
        ttk.Label(right, text="Statistici și rezumat (mock)",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=10)

        ttk.Label(
            right,
            text=(
                "- Număr pacienți analizați: 124\n"
                "- Acuratețe medie SVM: 0.86\n"
                "- Acuratețe medie MLP: 0.88\n"
                "- Ultima re-antrenare model: 10.12.2025"
            ),
            justify="left"
        ).pack(anchor="w")

    def quit_app(self):
        self.controller.destroy()


class PatientFormFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=10)

        ttk.Label(header, text="Formular introducere date pacient",
                  font=("Segoe UI", 16, "bold")).pack(side="left")

        ttk.Button(header, text="Înapoi la Dashboard",
                   command=lambda: controller.show_frame("DashboardFrame")).pack(side="right")

        form = ttk.Frame(self)
        form.pack(pady=20)

        # câmpuri ILPD
        labels = [
            "Vârstă",
            "Gen",
            "Bilirubină totală",
            "Bilirubină directă",
            "Fosfatază alcalină",
            "Alamin-aminotransferază (ALT)",
            "Aspartat-aminotransferază (AST)",
            "Proteine totale",
            "Albumină",
            "Raport Albumină/Globulină",
        ]

        self.entries = {}

        for i, text in enumerate(labels):
            ttk.Label(form, text=text + ":").grid(row=i, column=0, sticky="e", pady=3, padx=5)

            if text == "Gen":
                combo = ttk.Combobox(form, values=["Masculin", "Feminin"], state="readonly", width=27)
                combo.current(0)
                combo.grid(row=i, column=1, pady=3, padx=5, sticky="w")
                self.entries[text] = combo
            else:
                entry = ttk.Entry(form, width=30)
                entry.grid(row=i, column=1, pady=3, padx=5, sticky="w")
                self.entries[text] = entry

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Calculează risc (mock)",
                   command=self.calc_mock).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Curăță formular",
                   command=self.clear_form).pack(side="left", padx=5)

    def clear_form(self):
        for key, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.current(0)
            else:
                widget.delete(0, tk.END)

    def calc_mock(self):
        # Nu facem ML real, doar trimitem date mock către ecranul de predicție
        self.controller.set_prediction_result(
            label_text="Risc hepatic crescut",
            probability="0.82",
            model_name="SVM_v1.0",
            risk_level="high",
        )
        self.controller.show_frame("PredictionFrame")


class PredictionFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=10)

        ttk.Label(header, text="Rezultat predicție",
                  font=("Segoe UI", 16, "bold")).pack(side="left")

        ttk.Button(header, text="Înapoi la formular",
                   command=lambda: controller.show_frame("PatientFormFrame")).pack(side="right")

        content = ttk.Frame(self)
        content.pack(pady=40)

        self.label_result = ttk.Label(content, text="Nicio predicție efectuată",
                                      font=("Segoe UI", 18, "bold"))
        self.label_result.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(content, text="Probabilitate:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
        ttk.Label(content, text="Model utilizat:").grid(row=2, column=0, sticky="e", pady=5, padx=5)

        self.label_prob = ttk.Label(content, text="-")
        self.label_prob.grid(row=1, column=1, sticky="w", pady=5, padx=5)

        self.label_model = ttk.Label(content, text="-")
        self.label_model.grid(row=2, column=1, sticky="w", pady=5, padx=5)

        # Indicator vizual de risc (culoare)
        indicator_frame = ttk.Frame(self)
        indicator_frame.pack(pady=20)

        ttk.Label(indicator_frame, text="Indicator vizual risc:").pack()

        self.risk_indicator = tk.Label(
            indicator_frame,
            text="NEUTRU",
            width=20,
            height=2,
            bg="grey",
            fg="white",
            font=("Segoe UI", 12, "bold")
        )
        self.risk_indicator.pack(pady=10)

    def set_result(self, label_text, probability, model_name, risk_level):
        self.label_result.config(text=label_text)
        self.label_prob.config(text=f"{float(probability)*100:.1f}%")
        self.label_model.config(text=model_name)

        if risk_level == "high":
            self.risk_indicator.config(text="RISC ÎNALT", bg="red")
        elif risk_level == "low":
            self.risk_indicator.config(text="RISC SCĂZUT", bg="green")
        else:
            self.risk_indicator.config(text="NEUTRU", bg="grey")


# --- NOU: Ecran de Analiză Statistică și Comparații ML ---
class StatisticsFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=10)

        ttk.Label(header, text="Analiză statistică și comparații ML",
                  font=("Segoe UI", 16, "bold")).pack(side="left")

        ttk.Button(header, text="Înapoi la Dashboard",
                   command=lambda: controller.show_frame("DashboardFrame")).pack(side="right")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Stânga: valori numerice / metrici
        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=10)

        ttk.Label(left, text="Performanțe modele (mock)",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=5)

        ttk.Label(
            left,
            text=(
                "SVM:\n"
                "  - Acuratețe: 0.86\n"
                "  - Precizie: 0.84\n"
                "  - Recall: 0.81\n"
                "  - F1-Score: 0.82\n\n"
                "MLP:\n"
                "  - Acuratețe: 0.88\n"
                "  - Precizie: 0.87\n"
                "  - Recall: 0.85\n"
                "  - F1-Score: 0.86\n"
            ),
            justify="left"
        ).pack(anchor="w")

        ttk.Label(left, text="Concluzie (mock):\nMLP depășește ușor SVM\nla toate metricile.",
                  justify="left").pack(anchor="w", pady=10)

        # Dreapta: "grafice" desenate simplu pe Canvas
        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=10)

        # Canvas 1: comparație acuratețe SVM vs MLP
        ttk.Label(right, text="Comparație acuratețe SVM vs MLP",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w")

        canvas_acc = tk.Canvas(right, width=450, height=180, bg="white", highlightthickness=1, highlightbackground="gray")
        canvas_acc.pack(pady=5, fill="x")

        # Axă simplă
        canvas_acc.create_line(50, 150, 400, 150)   # axa X
        canvas_acc.create_line(50, 150, 50, 40)     # axa Y

        # Bare (valori mock)
        # SVM accuracy 0.86
        canvas_acc.create_rectangle(100, 150 - 0.86 * 100, 160, 150, fill="#4a90e2")
        canvas_acc.create_text(130, 150 - 0.86 * 100 - 10, text="0.86")

        # MLP accuracy 0.88
        canvas_acc.create_rectangle(220, 150 - 0.88 * 100, 280, 150, fill="#50e3c2")
        canvas_acc.create_text(250, 150 - 0.88 * 100 - 10, text="0.88")

        canvas_acc.create_text(130, 160, text="SVM")
        canvas_acc.create_text(250, 160, text="MLP")

        # Canvas 2: "importanța trăsăturilor"
        ttk.Label(right, text="Importanța trăsăturilor (mock)",
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 0))

        canvas_feat = tk.Canvas(right, width=450, height=220, bg="white", highlightthickness=1, highlightbackground="gray")
        canvas_feat.pack(pady=5, fill="x")

        features = [
            ("Bilirubină totală", 0.95),
            ("Raport Alb/Glob", 0.85),
            ("Vârstă", 0.72),
            ("Albumină", 0.68),
            ("Fosfatază alcalină", 0.60),
        ]

        start_y = 40
        for name, score in features:
            bar_len = int(score * 300)
            canvas_feat.create_rectangle(120, start_y - 10, 120 + bar_len, start_y + 10, fill="#f5a623")
            canvas_feat.create_text(80, start_y, text=name, anchor="e")
            canvas_feat.create_text(120 + bar_len + 25, start_y, text=f"{score:.2f}")
            start_y += 35


class AdminFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        header = ttk.Frame(self)
        header.pack(fill="x", pady=10, padx=10)

        ttk.Label(header, text="Panou administrare",
                  font=("Segoe UI", 16, "bold")).pack(side="left")

        ttk.Button(header, text="Înapoi la Dashboard",
                   command=lambda: controller.show_frame("DashboardFrame")).pack(side="right")

        body = ttk.Frame(self)
        body.pack(pady=20, padx=20, fill="both", expand=True)

        left = ttk.Frame(body)
        left.pack(side="left", fill="y", padx=10)

        right = ttk.Frame(body)
        right.pack(side="left", fill="both", expand=True, padx=10)

        ttk.Label(left, text="Operații modele ML", font=("Segoe UI", 12, "bold")).pack(pady=5)
        ttk.Button(left, text="Re-antrenare modele (mock)",
                   command=self.mock_action).pack(fill="x", pady=3)
        ttk.Button(left, text="Încarcă versiune nouă model (mock)",
                   command=self.mock_action).pack(fill="x", pady=3)

        ttk.Label(left, text="Utilizatori sistem", font=("Segoe UI", 12, "bold")).pack(pady=15)
        ttk.Button(left, text="Gestionează utilizatori (mock)",
                   command=self.mock_action).pack(fill="x", pady=3)

        ttk.Label(right, text="Log predicții (mock)", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        log_box = tk.Text(right, height=15)
        log_box.pack(fill="both", expand=True, pady=5)

        log_box.insert("end",
                       "12.12.2025  10:23  MEDIC1  Pacient #102   Model=SVM_v1.0   Risc=ÎNALT\n"
                       "12.12.2025  11:05  MEDIC2  Pacient #103   Model=MLP_v1.0   Risc=SCĂZUT\n"
                       "12.12.2025  11:45  MEDIC1  Pacient #104   Model=MLP_v1.0   Risc=ÎNALT\n")
        log_box.config(state="disabled")

    def mock_action(self):
        messagebox.showinfo("Info", "Aceasta este doar o acțiune de test (mock).")


if __name__ == "__main__":
    app = App()
    app.mainloop()
