
import customtkinter as ctk 
from database import db_config
from ml_logic import MLHandler
import gui_frames as gui

ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue")

class App(ctk.CTk): 
    def __init__(self):
        super().__init__()
        self.title("Sistem Suport Decizional - Liver Disease 2026")
        self.geometry("1100x850")

        self.db_config = db_config
        self.logged_user_id = None
        self.logged_user_role = None
        self.test_sizes = [0.20, 0.30, 0.40, 0.50]
        self.ml_handler = MLHandler(self.test_sizes)
        self.models_data = self.ml_handler.initialize_ml_logic()

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
        frame = self.frames[name]
        if hasattr(frame, "refresh"): frame.refresh()
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()