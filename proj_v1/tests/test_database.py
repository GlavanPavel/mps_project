import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_config

def test_db_config_structure():
    """Verifica daca dictionarul de configurare DB are cheile necesare."""
    required_keys = ['host', 'port', 'user', 'password', 'database']
    for key in required_keys:
        assert key in db_config
        assert db_config[key] is not None
