import unittest
import sys
import os

# Adaugam calea catre folderul parinte pentru a putea importa modulele
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proj_v1.utils import validate_patient_data

class TestMedicalQA(unittest.TestCase):
    """
    Suita de teste QA pentru Validarea Datelor Medicale
    """

    def test_valid_data(self):
        """TC01: Verificare date valide"""
        # Date normale: 30 ani, valori biochimice standard
        is_valid, msg = validate_patient_data(30, "Male", 0.9, 0.2, 200, 20, 25, 6.8, 3.3, 0.9)
        self.assertTrue(is_valid, f"Datele valide au fost respinse: {msg}")

    def test_negative_age(self):
        """TC02: Verificare respingere varsta negativa"""
        is_valid, msg = validate_patient_data(-5, "Male", 0.9, 0.2, 200, 20, 25, 6.8, 3.3, 0.9)
        self.assertFalse(is_valid)
        self.assertIn("Vârsta introdusă", msg)

    def test_string_input(self):
        """TC03: Verificare input non-numeric (litere)"""
        is_valid, msg = validate_patient_data(30, "Male", "zece", 0.2, 200, 20, 25, 6.8, 3.3, 0.9)
        self.assertFalse(is_valid)
        self.assertIn("trebuie să fie numerică", msg)

    def test_medical_logic(self):
        """TC04: Verificare logica medicala (Directa > Totala)"""
        # Bilirubina directa (5.0) > Totala (2.0) -> Imposibil fizic
        is_valid, msg = validate_patient_data(30, "Male", 2.0, 5.0, 200, 20, 25, 6.8, 3.3, 0.9)
        self.assertFalse(is_valid)
        self.assertIn("Bilirubina Directă nu poate fi mai mare", msg)

if __name__ == '__main__':
    print("Rulare teste QA automate...")
    unittest.main()
