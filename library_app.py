import sqlite3
import datetime

DB_FILE = "library.db"


def _get_db_connection():
    """Helper function to create a database connection."""
    try:
        conn = sqlite3.connect(DB_FILE)
        # This line makes the 'row' object accessible by column name
        conn.row_factory = sqlite3.Row
        # Enable foreign key enforcement
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def search_books(search_term):
    """
    Searches for books by ISBN, Title, or Author.
    Supports case-insensitive substring matching.

    Returns a list of dictionaries, where each dictionary
    contains:
    - NO (a 2-digit padded string, e.g., "01")
    - Isbn
    - Title
    - Authors (comma-separated string)
    - Availability ("IN" or "OUT")
    """

    # We add '%' wildcards to the search term for substring matching
    query_param = f"%{search_term}%"

    conn = _get_db_connection()
    if conn is None:
        return []

    results = []
    try:
        cursor = conn.cursor()

        sql_query = """
        SELECT
            B.Isbn,
            B.Title,
            GROUP_CONCAT(A.Name, ', ') AS Authors,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM BOOK_LOANS BL
                    WHERE BL.Isbn = B.Isbn AND BL.Date_in IS NULL
                ) THEN 'OUT'
                ELSE 'IN'
            END AS Availability
        FROM
            BOOK B
        JOIN
            BOOK_AUTHORS BA ON B.Isbn = BA.Isbn
        JOIN
            AUTHORS A ON BA.Author_id = A.Author_id
        WHERE
            B.Title COLLATE NOCASE LIKE ?
            OR A.Name COLLATE NOCASE LIKE ?
            OR B.Isbn LIKE ?
        GROUP BY
            B.Isbn, B.Title
        ORDER BY
            B.Title;
        """

        cursor.execute(sql_query, (query_param, query_param, query_param))

        # Get all results
        rows = cursor.fetchall()

        # *** NEW: Enumerate results to add the 'NO' column ***
        # We use enumerate(rows, 1) to start counting from 1
        for i, row in enumerate(rows, 1):
            # Convert the sqlite3.Row object to a standard dict
            row_dict = dict(row)

            # Add the new 'NO' key, formatting the number as
            # a 2-digit string (e.g., 1 -> "01", 10 -> "10")
            row_dict['NO'] = f"{i:02d}"

            results.append(row_dict)

    except sqlite3.Error as e:
        print(f"An error occurred during book search: {e}")
    finally:
        if conn:
            conn.close()

    return results


def checkout_book(isbn, card_id):
    """
    Checks out a book to a borrower.
    Performs all checks required by the project spec:
    1. Book is not already checked out.
    2. Borrower does not have unpaid fines.
    3. Borrower does not have 3 active loans.

    Returns a (success, message) tuple.
    """
    conn = _get_db_connection()
    if conn is None:
        return (False, "Error: Could not connect to the database.")

    try:
        cursor = conn.cursor()

        # --- CHECK 1: Is the book already checked out? ---
        cursor.execute("""
            SELECT 1 FROM BOOK_LOANS
            WHERE Isbn = ? AND Date_in IS NULL
        """, (isbn,))

        if cursor.fetchone():
            return (False, "Error: This book is already checked out.")

        # --- CHECK 2: Does the borrower have unpaid fines? ---
        # We need to join FINES and BOOK_LOANS to link fines to the borrower
        cursor.execute("""
            SELECT SUM(F.Fine_amt)
            FROM FINES F
            JOIN BOOK_LOANS BL ON F.Loan_id = BL.Loan_id
            WHERE BL.Card_id = ? AND F.Paid = 0
        """, (card_id,))

        fine_result = cursor.fetchone()
        if fine_result and fine_result[0] and fine_result[0] > 0:
            return (False, f"Error: Borrower has ${fine_result[0]:.2f} in unpaid fines. Cannot check out.")

        # --- CHECK 3: Does the borrower have 3 active loans? ---
        cursor.execute("""
            SELECT COUNT(*) FROM BOOK_LOANS
            WHERE Card_id = ? AND Date_in IS NULL
        """, (card_id,))

        loan_count = cursor.fetchone()[0]
        if loan_count >= 3:
            return (False, "Error: Borrower has already reached the maximum of 3 active loans.")

        # --- ALL CHECKS PASSED: Proceed with checkout ---
        today = datetime.date.today()
        due_date = today + datetime.timedelta(days=14)

        # Note: We use .isoformat() to store dates as 'YYYY-MM-DD' strings
        cursor.execute("""
            INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date)
            VALUES (?, ?, ?, ?)
        """, (isbn, card_id, today.isoformat(), due_date.isoformat()))

        conn.commit()
        return (True, f"Checkout successful! Due date is {due_date.isoformat()}.")

    except sqlite3.Error as e:
        conn.rollback()
        # This 'FOREIGN KEY constraint failed' error is a good way
        # to catch non-existent ISBNs or Card_IDs.
        if "FOREIGN KEY constraint failed" in str(e):
            return (False, "Error: Invalid ISBN or Borrower Card ID.")
        return (False, f"An unexpected database error occurred: {e}")
    finally:
        if conn:
            conn.close()


def search_active_loans(search_term):
    """
    Searches for active book loans (Date_in IS NULL) by matching
    a substring against the Book's ISBN, Borrower's Card_id,
    or Borrower's Name.

    Returns a list of dictionaries, where each dictionary
    contains loan and borrower details.
    """

    query_param = f"%{search_term}%"
    conn = _get_db_connection()
    if conn is None:
        return []

    results = []
    try:
        cursor = conn.cursor()

        # This query joins BOOK_LOANS with BORROWER and BOOK
        # to search across all specified fields.
        sql_query = """
        SELECT
            BL.Loan_id,
            BL.Isbn,
            B.Title,
            BL.Card_id,
            BR.Bname,
            BL.Date_out,
            BL.Due_date
        FROM
            BOOK_LOANS BL
        JOIN
            BORROWER BR ON BL.Card_id = BR.Card_id
        JOIN
            BOOK B ON BL.Isbn = B.Isbn
        WHERE
            -- Only find books that are still checked out
            BL.Date_in IS NULL
            AND (
                BL.Isbn LIKE ?
                OR BL.Card_id LIKE ?
                OR BR.Bname COLLATE NOCASE LIKE ?
            )
        ORDER BY
            BL.Due_date;
        """

        # Pass the param 3 times, one for each '?'
        cursor.execute(sql_query, (query_param, query_param, query_param))

        for row in cursor.fetchall():
            results.append(dict(row))

    except sqlite3.Error as e:
        print(f"An error occurred during loan search: {e}")
    finally:
        if conn:
            conn.close()

    return results


def checkin_book(loan_id):
    """
    Checks in a book by setting its Date_in to today.

    Returns a (success, message) tuple.
    """
    conn = _get_db_connection()
    if conn is None:
        return (False, "Error: Could not connect to the database.")

    try:
        cursor = conn.cursor()

        today = datetime.date.today().isoformat()

        # We only update rows where Loan_id matches AND Date_in is NULL.
        # This prevents re-checking in an already returned book.
        cursor.execute("""
            UPDATE BOOK_LOANS
            SET Date_in = ?
            WHERE Loan_id = ? AND Date_in IS NULL
        """, (today, loan_id))

        # cursor.rowcount will be 1 if the UPDATE was successful
        # and 0 if no row was found (e.g., invalid ID or already returned)
        if cursor.rowcount == 0:
            conn.rollback()
            return (False, "Error: Invalid Loan ID or book is already checked in.")
        else:
            conn.commit()
            return (True, f"Book (Loan ID: {loan_id}) successfully checked in.")

    except sqlite3.Error as e:
        conn.rollback()
        return (False, f"An unexpected database error occurred: {e}")
    finally:
        if conn:
            conn.close()


def add_borrower(bname, ssn, address, phone):
    """
    Creates a new borrower in the system.

    - All fields are required.
    - SSN must be unique.
    - A new, compatible Card_id is automatically generated.

    Returns a (success, message) tuple.
    """
    # Python-side check for required fields
    if not all([bname, ssn, address, phone]):
        return (False, "Error: All fields (Name, SSN, Address, Phone) are required.")

    conn = _get_db_connection()
    if conn is None:
        return (False, "Error: Could not connect to the database.")

    try:
        cursor = conn.cursor()

        # --- 1. Generate new Card_id ---
        # We find the maximum numeric part of all existing Card_ids
        # e.g., for "ID000018", we extract 18.
        cursor.execute("""
            SELECT MAX(CAST(SUBSTR(Card_id, 3) AS INTEGER)) 
            FROM BORROWER
        """)

        max_id_num = cursor.fetchone()[0]

        if max_id_num is None:
            # Table is empty, start at 1
            new_id_num = 1
        else:
            new_id_num = max_id_num + 1

        # Format the new number as a 6-digit string with 'ID' prefix
        # e.g., 19 -> "ID000019"
        new_card_id = f"ID{new_id_num:06d}"

        # --- 2. Insert the new borrower ---
        cursor.execute("""
            INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone)
            VALUES (?, ?, ?, ?, ?)
        """, (new_card_id, ssn, bname, address, phone))

        conn.commit()
        return (True, f"Successfully created new borrower: {bname} (Card ID: {new_card_id})")

    except sqlite3.IntegrityError as e:
        # This error is raised if the UNIQUE constraint on SSN fails
        conn.rollback()
        if "UNIQUE constraint failed: BORROWER.Ssn" in str(e):
            return (False, "Error: An account with this SSN already exists.")
        else:
            return (False, f"An unexpected database error occurred: {e}")
    except sqlite3.Error as e:
        conn.rollback()
        return (False, f"An unexpected database error occurred: {e}")
    finally:
        if conn:
            conn.close()


def update_all_fines():
    """
    Updates all fines in the FINES table.
    ... (docstring is the same) ...
    """
    conn = _get_db_connection()
    if conn is None:
        return (False, "Error: Could not connect to the database.")

    try:
        cursor = conn.cursor()

        # *** THE FIX IS HERE ***
        # We now use date('now') instead of 'now' to ignore
        # the time of day and get clean day-by-day math.
        sql_upsert = """
        INSERT INTO FINES (Loan_id, Fine_amt, Paid)
        SELECT
            Loan_id,
            CAST(
                MAX(0, JULIANDAY(COALESCE(Date_in, date('now'))) - JULIANDAY(Due_date)) * 0.25
            AS NUMERIC(10, 2)) AS Calculated_Fine,
            0 AS Paid
        FROM
            BOOK_LOANS
        WHERE
            -- Also use date('now') here
            JULIANDAY(COALESCE(Date_in, date('now'))) > JULIANDAY(Due_date)

        ON CONFLICT(Loan_id) DO UPDATE SET
            Fine_amt = excluded.Fine_amt
        WHERE
            FINES.Paid = 0;
        """

        cursor.execute(sql_upsert)
        updated_count = cursor.rowcount
        conn.commit()

        return (True, f"Successfully updated/processed {updated_count} fine records.")

    except sqlite3.Error as e:
        conn.rollback()
        return (False, f"An unexpected database error occurred: {e}")
    finally:
        if conn:
            conn.close()


def get_borrower_fines(card_id, include_paid=False):
    """
    Gets fine details for a borrower.
    Returns a dictionary with 'total' and 'details' (a list).
    """
    conn = _get_db_connection()
    if conn is None:
        return {'total': 0.0, 'details': [], 'message': "DB Connection Error"}

    query_total = 0.0
    query_details = []
    try:
        cursor = conn.cursor()

        sql_filter = " AND F.Paid = 0" if not include_paid else ""

        # Query to get line-item details
        cursor.execute(f"""
            SELECT
                BL.Loan_id,
                B.Title,
                F.Fine_amt,
                F.Paid,
                (BL.Date_in IS NULL) AS Is_Still_Out
            FROM FINES F
            JOIN BOOK_LOANS BL ON F.Loan_id = BL.Loan_id
            JOIN BOOK B ON BL.Isbn = B.Isbn
            WHERE BL.Card_id = ? {sql_filter}
        """, (card_id,))

        for row in cursor.fetchall():
            query_details.append(dict(row))

        # Query to get the total
        total_amt = sum(item['Fine_amt'] for item in query_details)
        query_total = float(f"{total_amt:.2f}")

    except sqlite3.Error as e:
        return {'total': 0.0, 'details': [], 'message': str(e)}
    finally:
        if conn:
            conn.close()

    return {'total': query_total, 'details': query_details, 'message': 'Success'}


def pay_borrower_fines(card_id):
    """
    Pays all outstanding (unpaid) fines for a borrower.

    - Checks rule: "Do not allow payment... for books that are not yet returned."
      (My interpretation: Cannot pay if any *overdue* book is still out).
    - Clears all unpaid fines for the borrower.

    Returns a (success, message) tuple.
    """
    conn = _get_db_connection()
    if conn is None:
        return (False, "Error: Could not connect to the database.")

    try:
        cursor = conn.cursor()

        # --- CHECK: Does the borrower have any OVERDUE books STILL OUT? ---
        cursor.execute("""
            SELECT 1 FROM BOOK_LOANS
            WHERE Card_id = ?
              AND Date_in IS NULL
              AND date('now') > Due_date
            LIMIT 1;
        """, (card_id,))

        if cursor.fetchone():
            return (False, "Error: Cannot pay fines. Borrower has one or more overdue books still checked out.")

        # --- PROCEED: Pay all fines for this borrower ---
        # We find all Loan_ids for this borrower and update their
        # corresponding FINES entries.
        cursor.execute("""
            UPDATE FINES
            SET Paid = 1
            WHERE Paid = 0 AND Loan_id IN (
                SELECT Loan_id FROM BOOK_LOANS WHERE Card_id = ?
            )
        """, (card_id,))

        paid_count = cursor.rowcount
        conn.commit()

        if paid_count == 0:
            return (False, "No unpaid fines found for this borrower.")
        else:
            return (True, f"Successfully paid {paid_count} fine(s). All fines are cleared.")

    except sqlite3.Error as e:
        conn.rollback()
        return (False, f"An unexpected database error occurred: {e}")
    finally:
        if conn:
            conn.close()

#Simply returns current borrower if there is one
def get_borrower_for_book(isbn):
    conn = _get_db_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Card_id 
            FROM BOOK_LOANS
            WHERE Isbn = ? AND Date_in IS NULL
        """, (isbn,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        print(f"Database error in get_borrower_for_book: {e}")
        return None
    finally:
        if conn:
            conn.close()


#Added this function to be able to see what books are checked out in checkout/in page
def getBooksCheckedOut(search=""):
    conn = _get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()

        query = """
        SELECT BL.Loan_id, B.Isbn, B.Title, BL.Card_id, BL.Due_date
        FROM BOOK_LOANS BL
        JOIN BOOK B ON BL.Isbn = B.Isbn
        WHERE BL.Date_in IS NULL
        """
        params = []

        if search:
            query += " AND (B.Title LIKE ? OR B.Isbn LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        #Convert results to list of dicts
        results = []
        for row in rows:
            results.append({
                "Loan_id": row[0],
                "Isbn": str(row[1]).zfill(10),  #Preserve leading zeroes
                "Title": row[2],
                "Card_id": row[3],
                "Due_date": row[4]
            })

        return results

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Main block for testing ---
if __name__ == "__main__":

    # --- !! IMPORTANT: Change these values to valid data from your CSVs !! ---
    # Find these in your borrower.csv and book.csv
    test_fine_card_id = "ID000007"  # A valid Card_id for a borrower
    test_borrower_name = "Deborah Lawrence"  # The Bname for the Card_id above
    test_isbn_1 = "0195153445"  # An ISBN for a book
    test_isbn_2 = "1558746218"  # A different ISBN
    test_isbn_3 = "1879384493"  # A third ISBN
    test_isbn_4 = "0312970242"  # A fourth ISBN
    # ---

    # --- Test 6: Checkout with Unpaid Fines ---
    print("\n\n--- Testing Checkout With Fines ---")

    # 6a: Create a new unpaid fine
    print(f"Setting up a new unpaid fine for {test_fine_card_id}...")
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        ssn = "123-23-2323"
        cursor.execute("SELECT card_id, bname, address, phone FROM BORROWER WHERE ssn = ?", (ssn,))
        row = cursor.fetchone()

        if row:
            print(f"Card ID: {row[0]}, Name: {row[1]}, Address: {row[2]}, Phone: {row[3]}")
        else:
            print("Borrower not found.")

        # *** THIS LINE IS NOW FIXED ***
        # Changed '-1R' to '-1 day'. This is 4 days late. 4 * 0.25 = $1.00
        cursor.execute("""
            INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in)
            VALUES (?, ?, date('now', '-10 day'), date('now', '-5 day'), date('now', '-1 day'))
        """, (test_isbn_3, test_fine_card_id))
        conn.commit()
    finally:
        if conn: conn.close()

    print("Running update_all_fines()...")
    success, message = update_all_fines()
    print(f"Result: {message}")

    # 6b: Check that fine exists
    fines = get_borrower_fines(test_fine_card_id)
    print(f"  Current Unpaid: ${fines['total']:.2f} (Should be $1.00)")

    # 6c: Attempt checkout (should fail)
    print(f"\nAttempting to check out {test_isbn_4} for {test_fine_card_id} (should fail)...")
    success, message = checkout_book(test_isbn_4, test_fine_card_id)
    print(f"Result: {message}")