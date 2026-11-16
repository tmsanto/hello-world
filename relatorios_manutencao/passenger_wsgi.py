# Ponto de entrada para hospedagens cPanel ("Setup Python App" / Passenger).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application  # noqa: E402
