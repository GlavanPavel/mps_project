import sys
import os
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_logic import MLHandler

@pytest.fixture
def mock_data():
    """Creeaza un DataFrame fals care imita structura setului de date ILPD."""

    data = {
        'Age': [50, 40, 30, 45, 60, 35, 25, 55, 65, 20],
        'Gender': ['Male', 'Female', 'Male', 'Male', 'Female', 'Female', 'Male', 'Male', 'Female', 'Female'],
        'TB': [0.9, 1.0, 0.8, 0.9, 1.1, 0.7, 0.8, 1.2, 0.6, 1.0],
        'DB': [0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.2, 0.4, 0.1, 0.2],
        'Alk': [150, 200, 180, 160, 210, 140, 190, 220, 130, 175],
        'Sgpt': [20, 30, 25, 22, 35, 18, 28, 40, 15, 32],
        'Sgot': [25, 35, 30, 28, 38, 22, 33, 45, 20, 36],
        'TP': [6.8, 7.0, 6.5, 6.9, 7.2, 6.4, 6.6, 7.5, 6.2, 6.8],
        'ALB': [3.3, 3.5, 3.2, 3.4, 3.6, 3.1, 3.3, 3.8, 3.0, 3.4],
        'AG': [0.9, 1.0, 0.8, 0.9, 1.1, 0.7, 0.9, 1.2, 0.6, 1.0],
        'Dataset': [1, 2, 1, 1, 2, 2, 1, 2, 2, 1] # 1=Bolnav, 2=Sanatos
    }
    return pd.DataFrame(data)

@patch('ml_logic.pd.read_csv')
@patch('ml_logic.os.makedirs')
@patch('ml_logic.joblib.dump')
@patch('ml_logic.joblib.load')
@patch('ml_logic.os.path.exists')
def test_initialize_ml_logic_training(mock_exists, mock_load, mock_dump, mock_makedirs, mock_read_csv, mock_data):
    """Testeaza antrenarea modelelor (cand fisierele nu exista)."""
    
    # Simulam ca nu exista modele salvate
    mock_exists.return_value = False
    
    # Simulam citirea datelor
    mock_read_csv.return_value = mock_data
    
    # Initializam handler
    test_sizes = [0.20]
    handler = MLHandler(test_sizes)
    
    # Rulam logica
    models = handler.initialize_ml_logic()
    
    # Verificari
    assert 0.20 in models
    assert 'SVM' in models[0.20]
    assert 'MLP' in models[0.20]
    assert 'SCALER' in models[0.20]
    
    # Verificam ca s-a apelat read_csv
    assert mock_read_csv.called
    
    # Verificam ca s-a incercat salvarea modelelor (3 fisiere per split * 1 split = 3 apeluri)
    assert mock_dump.call_count == 3

@patch('ml_logic.os.path.exists')
@patch('ml_logic.joblib.load')
def test_initialize_ml_logic_loading(mock_load, mock_exists):
    """Testeaza incarcarea modelelor existente."""
    
    # Simulam ca fisierele exista
    mock_exists.return_value = True
    
    # Simulam obiecte incarcate
    mock_svm = MagicMock()
    mock_mlp = MagicMock()
    mock_scaler = MagicMock()
    
    # Returnam secvential pentru apelurile load
    mock_load.side_effect = [mock_svm, mock_mlp, mock_scaler]
    
    handler = MLHandler([0.20])
    models = handler.initialize_ml_logic()
    
    assert 0.20 in models
    assert models[0.20]['SVM'] == mock_svm
    assert models[0.20]['MLP'] == mock_mlp
