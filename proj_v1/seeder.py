import pandas as pd
import mysql.connector

def run_complete_seeder():
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00225/Indian%20Liver%20Patient%20Dataset%20(ILPD).csv"
    column_names = ['Age', 'Gender', 'Total_Bilirubin', 'Direct_Bilirubin',
                    'Alkaline_Phosphotase', 'Alamine_Aminotransferase',
                    'Aspartate_Aminotransferase', 'Total_Proteins',
                    'Albumin', 'Albumin_and_Globulin_Ratio', 'Dataset']

    df = pd.read_csv(url, names=column_names, header=None)
    df = df.dropna()

    db_config = {
        'host': '127.0.0.1',
        'port': 3309,
        'user': 'user',
        'password': 'user',
        'database': 'liver_disease'
    }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        parola_admin = 'admin'
        parola_medic = 'medic'
        utilizatori = [
            ('medic', parola_medic, 'MEDIC'),
            ('admin', parola_admin, 'ADMIN')
        ]

        cursor.executemany("INSERT IGNORE INTO USERS (username, password_hash, role) VALUES (%s, %s, %s)", utilizatori)
        
        cursor.execute("SELECT id FROM USERS WHERE username = 'medic'")
        medic_id = cursor.fetchone()[0]

        for index, row in df.iterrows():
            cnp_fictiv = f"UCI{index:010d}"
            
            cursor.execute("""
                INSERT IGNORE INTO PATIENTS (cnp_internal_id, full_name, gender, birth_date)
                VALUES (%s, %s, %s, %s)
            """, (cnp_fictiv, f"Pacient_UCI_{index}", row['Gender'], '1970-01-01'))

            cursor.execute("SELECT id FROM PATIENTS WHERE cnp_internal_id = %s", (cnp_fictiv,))
            patient_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM PREDICTIONS WHERE patient_id = %s AND user_id = %s", (patient_id, medic_id))
            if cursor.fetchone() is None:
                gender_val = 1 if row['Gender'] == 'Male' else 0
                cursor.execute("""
                    INSERT INTO PREDICTIONS (
                        patient_id, user_id, prediction_result, confidence_score,
                        age, gender_val, total_bilirubin, direct_bilirubin,
                        alkaline_phosphotase, alamine_aminotransferase,
                        aspartate_aminotransferase, total_proteins,
                        albumin, albumin_and_globulin_ratio
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    patient_id, medic_id, int(row['Dataset']), 1.0,
                    int(row['Age']), gender_val, row['Total_Bilirubin'], row['Direct_Bilirubin'],
                    int(row['Alkaline_Phosphotase']), int(row['Alamine_Aminotransferase']),
                    int(row['Aspartate_Aminotransferase']), row['Total_Proteins'],
                    row['Albumin'], row['Albumin_and_Globulin_Ratio']
                ))

        conn.commit()
        print("Seeding finalizat cu succes. Utilizatori: medic, admin. Date ILPD incarcate.")

    except Exception as e:
        print(f"Eroare: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    run_complete_seeder()