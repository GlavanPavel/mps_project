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
from datetime import datetime

def calculate_age_from_dob(dob_str):
    """
    Calculeaza varsta pe baza datei de nastere (format YYYY-MM-DD).
    Returneaza: int (varsta) sau None daca formatul e gresit.
    """
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        # Calcul varsta scazand anul si ajustand daca nu a trecut ziua de nastere anul acesta
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return None

def validate_patient_data(age, gender, total_bilirubin, direct_bilirubin, 
                          alkaline_phosphotase, alamine_aminotransferase, 
                          aspartate_aminotransferase, total_proteins, 
                          albumin, albumin_and_globulin_ratio):
    """
    Valideaza datele pacientului inainte de a le trimite la modelul ML.
    Returneaza: (bool, string) -> (Status Validare, Mesaj Eroare)
    """
    try:
        # 1. Validare Vârstă
        try:
            age_val = float(age)
        except ValueError:
            return False, "Vârsta trebuie să fie un număr."
        
        if age_val < 0 or age_val > 120:
            return False, f"Vârsta introdusă ({age_val}) este invalidă. Trebuie să fie între 0 și 120."

        # 2. Validare Valori Numerice Clinice
        # Lista cu etichete pentru mesaje de eroare clare
        checks = {
            "Bilirubina Totală": total_bilirubin,
            "Bilirubina Directă": direct_bilirubin,
            "Fosfataza Alcalină": alkaline_phosphotase,
            "ALT": alamine_aminotransferase,
            "AST": aspartate_aminotransferase,
            "Proteine Totale": total_proteins,
            "Albumina": albumin,
            "Raport A/G": albumin_and_globulin_ratio
        }

        for label, value in checks.items():
            try:
                val_float = float(value)
                if val_float < 0:
                    return False, f"Valoarea pentru '{label}' nu poate fi negativă."
            except ValueError:
                return False, f"Valoarea pentru '{label}' trebuie să fie numerică."

        # 3. Validare logica medicala simpla (Exemplu: Bilirubina Directa < Totala)
        # Nota: Aceasta este o regula generala, nu absoluta, dar utila pentru QA
        if float(direct_bilirubin) > float(total_bilirubin):
            return False, "Bilirubina Directă nu poate fi mai mare decât Bilirubina Totală."

        return True, "Validare cu succes"

    except Exception as e:
        return False, f"Eroare neașteptată la validare: {str(e)}"
