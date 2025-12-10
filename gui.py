import tkinter as tk
from tkinter import ttk, messagebox
import library_app as library  #Backend functions
import theme #Theme module

class MainApp(tk.Tk): #Initialize tkinter window
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("900x600")

        theme.apply_theme(self)  #Apply dark theme from theme.py

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ttk.Frame(self, style = "TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #Dictionary to hold pages / frames
        self.frames = {}
        for F in (HomePage, SearchPage, LoansPage, BorrowersPage, FinesPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

#-------------------- Pages --------------------

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg = theme.BG_COLOR)

        #Main frame that will center its child
        content_frame = tk.Frame(self, bg = theme.CARD_BG, padx = 20, pady = 20)
        content_frame.pack(expand=True)  #Center vertically and horizontally

        #All the pages for functional requirements
        tk.Label(content_frame, text="Library Management System", font=("Arial", 24)).pack(pady=20)

        def nav_button(text, page):
            return ttk.Button(
                content_frame,
                text = text,
                style = "Accent.TButton",
                command = lambda: controller.show_frame(page)
            )

        nav_button("Search Books", SearchPage).pack(fill="x", pady=10)
        nav_button("Manage Loans", LoansPage).pack(fill="x", pady=10)
        nav_button("Manage Borrowers", BorrowersPage).pack(fill="x", pady=10)
        nav_button("Manage Fines", FinesPage).pack(fill="x", pady=10)

class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        #Title
        tk.Label(self, text="Search Books", font=("Arial", 18)).pack(pady=10)

        #Single text search entry
        self.search_entry = tk.Entry(self, width=50)
        self.search_entry.pack(pady=5)

        #Search and Back buttons
        tk.Button(self, text="Search", command=self.perform_search).pack(pady=5)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=10)

        #Table to show search results
        self.tree = ttk.Treeview(self, columns=("ISBN", "Title", "Authors", "Availability", "BorrowerID"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")  
        self.tree.pack(fill="both", expand=True)

    #Function that actually performs search is in library_app.py
    def perform_search(self):
        term = self.search_entry.get()
        results = library.search_books(term)  #Call search_books from library_app.py

        #Clear previous results
        for row in self.tree.get_children():
            self.tree.delete(row)

        #Insert new search results
        for item in results:
            borrower_id = library.get_borrower_for_book(item["Isbn"])
            self.tree.insert(
                "",
                "end",
                values=(item["Isbn"], item["Title"], item["Authors"], item["Availability"], borrower_id)
            )

class LoansPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Manage Loans (Checkout/Checkin)", font=("Arial", 18)).pack(pady=10)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=10)

        #Checkout section
        checkout_frame = tk.LabelFrame(self, text="Checkout Book")
        checkout_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(checkout_frame, text="ISBN:").grid(row=0, column=0, padx=5, pady=5)
        self.isbn_entry = tk.Entry(checkout_frame)
        self.isbn_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(checkout_frame, text="Borrower Card ID:").grid(row=0, column=2, padx=5, pady=5)
        self.card_entry = tk.Entry(checkout_frame)
        self.card_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(checkout_frame, text="Checkout by ISBN", command=self.checkout_by_isbn).grid(row=0, column=4, padx=5, pady=5)

        #Table of available books to select
        self.available_tree = ttk.Treeview(self, columns=("ISBN", "Title", "Authors"), show="headings", selectmode="browse")
        for col in self.available_tree["columns"]:
            self.available_tree.heading(col, text=col)
        self.available_tree.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Button(self, text="Checkout Selected Book", command=self.checkout_selected_book).pack(pady=5)

        #Check in section
        checkin_frame = tk.LabelFrame(self, text="Check-in Books")
        checkin_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.checked_out_tree = ttk.Treeview(checkin_frame, columns=("Loan ID", "ISBN", "Title", "Borrower ID", "Due Date"), show="headings", selectmode="browse")
        for col in self.checked_out_tree["columns"]:
            self.checked_out_tree.heading(col, text=col)
        self.checked_out_tree.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Button(checkin_frame, text="Check-in Selected Book", command=self.checkin_selected_book).pack(pady=5)

        self.load_available_books()
        self.load_checked_out_books()

    #Helper functions
    def load_available_books(self):
        for row in self.available_tree.get_children():
            self.available_tree.delete(row)
        results = library.search_books("")  
        for item in results:
            if item["Availability"] == "IN":
                self.available_tree.insert("", "end", values=(str(item["Isbn"]), item["Title"], item["Authors"]))

    def load_checked_out_books(self):
        for row in self.checked_out_tree.get_children():
            self.checked_out_tree.delete(row)
        results = library.getBooksCheckedOut("")  #Get all checked out books
        for item in results:
            self.checked_out_tree.insert("", "end", values=(item["Loan_id"], item["Isbn"], item["Title"], item["Card_id"], item["Due_date"]))

    #Checkout methods
    #Checkout by isbn requires you to enter a valid isbn and borrower id to checkout a max of 3 books
    def checkout_by_isbn(self):
        isbn = self.isbn_entry.get().strip()
        card_id = self.card_entry.get().strip()
        if not isbn or not card_id:
            messagebox.showerror("Error", "Please enter both ISBN and Borrower Card ID")
            return
        success, msg = library.checkout_book(isbn, card_id)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.load_available_books()
        self.load_checked_out_books()

    #Click / select a book to highlight it then enter a valid borrower id and select checkout button to checkout
    def checkout_selected_book(self):
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book from the table")
            return

        isbn = str(self.available_tree.item(selected[0])["values"][0])
        card_id = self.card_entry.get().strip()
        isbn = isbn.replace("-", "").replace(" ", "").zfill(10) #When retrieving values from tree it removes leading zeroes, add them back (All isbns are 10 chars)

        if not card_id:
            messagebox.showerror("Error", "Please enter Borrower Card ID")
            return

        success, msg = library.checkout_book(isbn, card_id)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

        self.load_available_books()
        self.load_checked_out_books()

    #Checkin methods
    def checkin_selected_book(self):
        selected = self.checked_out_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to check-in")
            return
        loan_id = self.checked_out_tree.item(selected[0])["values"][0]
        success, msg = library.checkin_book(loan_id)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)
        self.load_available_books()
        self.load_checked_out_books()

#4 my tr maan
class BorrowersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Borrower Management", font=("Arial", 18)).pack(pady=10)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        # --- Input Fields ---
        tk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky="e")
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="SSN:").grid(row=1, column=0, sticky="e")
        self.ssn_entry = tk.Entry(form_frame)
        self.ssn_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Address:").grid(row=2, column=0, sticky="e")
        self.address_entry = tk.Entry(form_frame)
        self.address_entry.grid(row=2, column=1)

        tk.Label(form_frame, text="Phone:").grid(row=3, column=0, sticky="e")
        self.phone_entry = tk.Entry(form_frame)
        self.phone_entry.grid(row=3, column=1)

        # --- Buttons ---
        tk.Button(self, text="Create Borrower", command=self.create_borrower).pack(pady=10)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=5)

        # --- Status Message ---
        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=5)

    def create_borrower(self):
        name = self.name_entry.get().strip()
        ssn = self.ssn_entry.get().strip()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()

        #1. Validate required fields (NOT NULL)
        if not name or not ssn or not address:
            self.status_label.config(
                text="Error: Name, SSN, and Address are required.",
                fg="red"
            )
            return

        try:
            import sqlite3
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()

            #2. Enforce ONE borrower per SSN
            cur.execute("SELECT card_id FROM BORROWER WHERE ssn = ?", (ssn,))
            if cur.fetchone():
                self.status_label.config(
                    text="Error: A borrower with this SSN already exists.",
                    fg="red"
                )
                conn.close()
                return

            #3. Auto-generate new card_id in the format ID000001
            cur.execute("SELECT MAX(CAST(SUBSTR(card_id, 3) AS INTEGER)) FROM BORROWER")
            result = cur.fetchone()[0]
            new_number = int(result) + 1 if result else 1
            new_card_id = f"ID{new_number:06d}"  # ID + 6-digit zero-padded number

            #4. Insert new borrower
            cur.execute("""
                INSERT INTO BORROWER (card_id, bname, address, phone, ssn)
                VALUES (?, ?, ?, ?, ?)
            """, (new_card_id, name, address, phone, ssn))

            conn.commit()
            conn.close()

            # 5. Success message + clear form
            self.status_label.config(
                text=f"Borrower created successfully. Card No: {new_card_id}",
                fg="green"
            )

            self.name_entry.delete(0, tk.END)
            self.ssn_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)

        except Exception as e:
            self.status_label.config(
                text=f"Database Error: {str(e)}",
                fg="red"
            )



#-------------------- Fines Page --------------------
class FinesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Fines Management", font=("Arial", 18)).pack(pady=10)

        search_frame = tk.Frame(self)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Borrower ID:").grid(row=0, column=0)
        self.card_entry = tk.Entry(search_frame)
        self.card_entry.grid(row=0, column=1)

        tk.Label(search_frame, text="Borrower Name:").grid(row=0, column=2)
        self.name_entry = tk.Entry(search_frame)
        self.name_entry.grid(row=0, column=3)

        tk.Button(search_frame, text="Search Fines", command=self.search_fines).grid(row=0, column=4, padx=5)
        tk.Button(search_frame, text="Refresh Fines", command=self.refresh_fines).grid(row=0, column=5, padx=5)

        # --- Table ---
        self.tree = ttk.Treeview(self, columns=("card", "name", "total"), show="headings")
        self.tree.heading("card", text="Card ID")
        self.tree.heading("name", text="Borrower Name")
        self.tree.heading("total", text="Total Fine ($)")
        self.tree.pack(pady=10)

        tk.Button(self, text="Pay Selected Fine", command=self.pay_fine).pack(pady=5)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=5)

        self.message = tk.Label(self, text="", fg="red")
        self.message.pack(pady=5)

    # ---------------- REFRESH FINES ----------------
    def refresh_fines(self):
        import sqlite3, datetime
        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        today = datetime.date.today()

        cur.execute("""
            SELECT loan_id, due_date, date_in 
            FROM BOOK_LOANS
            WHERE due_date IS NOT NULL
        """)
        loans = cur.fetchall()

        for loan_id, due, returned in loans:
            due_date = datetime.date.fromisoformat(due)

            if returned:
                returned_date = datetime.date.fromisoformat(returned)
                late_days = (returned_date - due_date).days
            else:
                late_days = (today - due_date).days

            if late_days > 0:
                fine_amt = round(late_days * 0.25, 2)

                cur.execute("SELECT paid FROM FINES WHERE loan_id = ?", (loan_id,))
                row = cur.fetchone()

                if row:
                    if row[0] == 0:                     # unpaid → update only
                        cur.execute("""
                            UPDATE FINES SET fine_amt = ?
                            WHERE loan_id = ?
                        """, (fine_amt, loan_id))
                else:
                    cur.execute("""
                        INSERT INTO FINES (loan_id, fine_amt, paid)
                        VALUES (?, ?, 0)
                    """, (loan_id, fine_amt))

        conn.commit()
        conn.close()
        self.message.config(text="Fines refreshed successfully.", fg="green")
        self.search_fines()

    # ---------------- SEARCH FINES ----------------
    def search_fines(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        import sqlite3
        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        card = self.card_entry.get().strip()
        name = self.name_entry.get().strip()

        query = """
            SELECT B.card_id, B.bname, SUM(F.fine_amt)
            FROM BORROWER B
            JOIN BOOK_LOANS L ON B.card_id = L.card_id
            JOIN FINES F ON L.loan_id = F.loan_id
            WHERE F.paid = 0
        """

        params = []

        if card:
            query += " AND B.card_id = ?"
            params.append(card)

        if name:
            query += " AND B.bname LIKE ?"
            params.append(f"%{name}%")

        query += " GROUP BY B.card_id, B.bname"

        cur.execute(query, params)
        results = cur.fetchall()
        conn.close()

        for card_id, bname, total in results:
            self.tree.insert("", "end", values=(card_id, bname, f"{total:.2f}"))

    # ---------------- PAY FINE ----------------
    def pay_fine(self):
        selected = self.tree.selection()
        if not selected:
            self.message.config(text="Select a borrower to pay fine.")
            return

        card_id = self.tree.item(selected[0])["values"][0]

        import sqlite3
        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        #Do not allow paying if book not returned
        cur.execute("""
            SELECT 1 FROM BOOK_LOANS L
            JOIN FINES F ON L.loan_id = F.loan_id
            WHERE L.card_id = ? AND L.date_in IS NULL AND F.paid = 0
        """, (card_id,))
        if cur.fetchone():
            self.message.config(text="Error: Cannot pay fine for books not yet returned.")
            conn.close()
            return

        # Mark all unpaid fines as paid
        cur.execute("""
            UPDATE FINES SET paid = 1
            WHERE loan_id IN (
                SELECT L.loan_id FROM BOOK_LOANS L
                JOIN FINES F ON L.loan_id = F.loan_id
                WHERE L.card_id = ? AND F.paid = 0
            )
        """, (card_id,))

        conn.commit()
        conn.close()
        self.message.config(text="Fine paid successfully.", fg="green")
        self.search_fines()


# -------------------- Run the App --------------------

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
