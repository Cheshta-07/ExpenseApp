# RUNNING THE APP

import sys

from PyQt6.QtWidgets import QApplication

from app import ExpenseApp
from database import init_db

def main() :

    app = QApplication(sys.argv)

    if not init_db("expenses.db"):
        print("Database initialization failed.")
        sys.exit(-1)
    
    window = ExpenseApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
