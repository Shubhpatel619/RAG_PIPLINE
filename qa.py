import sys
import os

# Redirect execution to project/qa.py
sys.path.insert(0, os.path.abspath("."))
from project.qa import main

if __name__ == "__main__":
    main()
