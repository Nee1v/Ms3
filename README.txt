Library Management System - Team Magnesium
Team members:  Quan Nguyen, Sebastian Sarinana, A Rahman Gulaid, Vavilapalli Vavilapalli, Rishik Yechuri

DEPENDENCIES:
- Python
- sqlite3
- Tkinter (included with standard Python)
- No third party packages required

FIlES:
create_db.py                Builds database schema
load_data.py                Loads CSV data into tables
library_app.py              Backend logic - queries, fines calculation, transactions
gui.py                      Tkinter graphical interface
theme.py                    Shared styling definitions
library.db                  SQLite database (generated)
*.csv                       source datasets

HOW TO RUN:
1. Run: python3 create_db.py
2. Run: python3 load_data.py
3. Launch app: python gui.py

SYSTEM OVERVIEW:
Supports searching books, managing loans, creating borrowers, paying fines.
Uses layered architectures: GUI -> Logic -> database
SQLite database
Fines calculations with logic

