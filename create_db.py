import sqlite3
import os

DB_FILE = "library.db"

def create_database():
    """
    Creates the library database and all required tables
    based on the project schema.
    """
    # Delete the old database file if it exists, to start fresh
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Set up foreign key enforcement (off by default in SQLite)
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- Create Tables ---

        # BOOK table
        cursor.execute("""
        CREATE TABLE BOOK (
            Isbn TEXT PRIMARY KEY,
            Title TEXT
        );
        """)

        # AUTHORS table
        cursor.execute("""
        CREATE TABLE AUTHORS (
            Author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT
        );
        """)

        # BOOK_AUTHORS table (Junction table)
        cursor.execute("""
        CREATE TABLE BOOK_AUTHORS (
            Author_id INTEGER,
            Isbn TEXT,
            PRIMARY KEY (Author_id, Isbn),
            FOREIGN KEY (Author_id) REFERENCES AUTHORS(Author_id)
                ON DELETE CASCADE,
            FOREIGN KEY (Isbn) REFERENCES BOOK(Isbn)
                ON DELETE CASCADE
        );
        """)

        # BORROWER table
        # Per spec: All attributes NOT NULL
        # Per spec: SSN must be unique
        cursor.execute("""
        CREATE TABLE BORROWER (
            Card_id TEXT PRIMARY KEY,
            Ssn TEXT NOT NULL UNIQUE,
            Bname TEXT NOT NULL,
            Address TEXT NOT NULL,
            Phone TEXT NOT NULL
        );
        """)

        # BOOK_LOANS table
        cursor.execute("""
        CREATE TABLE BOOK_LOANS (
            Loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            Isbn TEXT NOT NULL,
            Card_id TEXT NOT NULL,
            Date_out TEXT NOT NULL,
            Due_date TEXT NOT NULL,
            Date_in TEXT,
            FOREIGN KEY (Isbn) REFERENCES BOOK(Isbn)
                ON DELETE RESTRICT,
            FOREIGN KEY (Card_id) REFERENCES BORROWER(Card_id)
                ON DELETE RESTRICT
        );
        """)

        # FINES table
        # Per spec: Fine_amt is fixed-decimal (NUMERIC(10, 2))
        # Per spec: Paid is boolean (INTEGER 0 or 1)
        cursor.execute("""
        CREATE TABLE FINES (
            Loan_id INTEGER PRIMARY KEY,
            Fine_amt NUMERIC(10, 2) NOT NULL,
            Paid INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (Loan_id) REFERENCES BOOK_LOANS(Loan_id)
                ON DELETE CASCADE
        );
        """)

        conn.commit()
        print(f"Success! Database '{DB_FILE}' and all tables created.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()