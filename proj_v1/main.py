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
import customtkinter as ctk 
from database import db_config
from ml_logic import MLHandler
import gui_frames as gui

# Configureaza tema vizuala a aplicatiei
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")

class App(ctk.CTk): 
    """
    Clasa principala a aplicatiei care gestioneaza navigarea intre ferestre si starea globala
    Actioneaza ca un controller principal
    """
    def __init__(self):
        super().__init__()
        # Initializeaza fereastra principala
        self.title("Sistem Suport Decizional - Liver Disease 2026")
        self.geometry("1100x850")

        # Incarca configuratia
        self.db_config = db_config
        self.logged_user_id = None
        self.logged_user_role = None

        # Initializeaza logica 
        self.test_sizes = [0.20, 0.30, 0.40, 0.50]
        self.ml_handler = MLHandler(self.test_sizes)
        self.models_data = self.ml_handler.initialize_ml_logic()

        # Creeaza containerul principal 
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (gui.LoginFrame, gui.DashboardFrame, gui.PatientFormFrame, 
                  gui.PredictionFrame, gui.StatisticsFrame, gui.AdminUserFrame, gui.HistoryFrame):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        """
        Afiseaza fereastra specificata prin nume si actualizeaza continutul daca este necesar
        """
        frame = self.frames[name]
        if hasattr(frame, "refresh"): frame.refresh()
        frame.tkraise()

if __name__ == "__main__":
    # Punctul de intrare in aplicatie
    app = App()
    app.mainloop()