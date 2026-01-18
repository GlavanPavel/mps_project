CREATE TABLE IF NOT EXISTS USERS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('MEDIC', 'ADMIN') NOT NULL
);

CREATE TABLE IF NOT EXISTS PATIENTS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cnp_internal_id VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    birth_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS PREDICTIONS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    user_id INT NOT NULL,
    prediction_result INT,
    confidence_score FLOAT,
    age INT,
    gender_val INT,
    total_bilirubin FLOAT,
    direct_bilirubin FLOAT,
    alkaline_phosphotase INT,
    alamine_aminotransferase INT,
    aspartate_aminotransferase INT,
    total_proteins FLOAT,
    albumin FLOAT,
    albumin_and_globulin_ratio FLOAT,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(id),
    FOREIGN KEY (user_id) REFERENCES USERS(id)
);
