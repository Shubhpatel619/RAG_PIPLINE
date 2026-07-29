import sys
import os

# Ensure workspace root is in sys.path for pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
