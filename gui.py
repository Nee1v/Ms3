import tkinter as tk
from tkinter import ttk, messagebox
import library_app as library  #Backend functions
import theme #Theme module

def validate_digits_with_limit(new_value: str, max_len_str: str) -> bool:
    """
    Allow only digits (or empty string) and enforce a maximum length.
    new_value: value of the entry if the change is allowed
    max_len_str: max length passed in from validatecommand ("9", "10", etc.)
    """
    if not (new_value.isdigit() or new_value == ""):
        return False

    max_len = int(max_len_str)
    return len(new_value) <= max_len



class MainApp(tk.Tk): #Initialize tkinter window
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("900x600")

         # track logged-in user
        self.current_user = None
        self.current_card_id = None
        self.is_librarian = False

        theme.apply_theme(self)  #Apply dark theme from theme.py

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ttk.Frame(self, style = "TFrame")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #Dictionary to hold pages / frames
        self.frames = {}
        for F in (LoginPage, SignUpPage, HomePage, SearchPage, LoansPage, BorrowersPage, FinesPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        # Allow pages to refresh based on user context
        if hasattr(frame, "refresh_for_user"):
            frame.refresh_for_user()
        frame.tkraise()

#-------------------- Pages --------------------

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG_COLOR)
        self.controller = controller

        # Centering container
        outer = tk.Frame(self, bg=theme.BG_COLOR)
        outer.pack(expand=True)

        # Card container
        card = tk.Frame(
            outer,
            bg=theme.CARD_BG,
            padx=30,
            pady=30,
            highlightthickness=2,
            highlightbackground=theme.OUTLINE_COLOR
        )
        card.pack()

        tk.Label(
            card,
            text="Login",
            font=theme.FONT_TITLE,
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tk.Label(
            card,
            text="Username:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30
        )
        self.username_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            card,
            text="Password:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30,
            show="*"
        )
        self.password_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # press enter to go to pass word entry, then press enter to login
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

        ttk.Button(
            card,
            text="Login",
            style="Accent.TButton",
            command=self.handle_login
        ).grid(row=3, column=0, columnspan=2, pady=(15, 5), sticky="ew")

        ttk.Button(
            card,
            text="Sign Up",
            style="Accent.TButton",
            command=lambda: controller.show_frame(SignUpPage)
        ).grid(row=4, column=0, columnspan=2, pady=(5, 0), sticky="ew")

    def handle_login(self):
        import sqlite3

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.", parent=self)
            return

        try:
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT username, password, card_id, is_librarian
                FROM USERS
                WHERE username = ?
            """, (username,))
            row = cur.fetchone()
            conn.close()

            if row is None:
                messagebox.showerror("Error", "Incorrect username or password.", parent=self)
                return

            db_username, db_password, db_card_id, is_librarian = row

            if password != db_password:
                messagebox.showerror("Error", "Incorrect username or password.", parent=self)
                return

            self.controller.current_user = db_username
            self.controller.current_card_id = db_card_id
            self.controller.is_librarian = bool(is_librarian)
            self.controller.show_frame(HomePage)

        except Exception as e:
            messagebox.showerror("Error", f"Database error during login:\n{e}", parent=self)


class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG_COLOR)
        self.controller = controller

        vcmd_ssn = (self.register(validate_digits_with_limit), "%P", "9")
        vcmd_phone = (self.register(validate_digits_with_limit), "%P", "10")

        outer = tk.Frame(self, bg=theme.BG_COLOR)
        outer.pack(expand=True)

        card = tk.Frame(
            outer,
            bg=theme.CARD_BG,
            padx=30,
            pady=30,
            highlightthickness=2,
            highlightbackground=theme.OUTLINE_COLOR
        )
        card.pack()

        tk.Label(
            card,
            text="Sign Up",
            font=theme.FONT_TITLE,
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        tk.Label(
            card,
            text="Enter the following:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MUTED,
            font=theme.FONT_BODY
        ).grid(row=1, column=0, columnspan=2, pady=(0, 10))

        tk.Label(
            card,
            text="Full Name:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.fullname_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30
        )
        self.fullname_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            card,
            text="SSN:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.ssn_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30,
            validate="key",
            validatecommand=vcmd_ssn
        )
        self.ssn_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            card,
            text="Address:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.address_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30
        )
        self.address_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            card,
            text="Phone:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.phone_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30,
            validate="key",
            validatecommand=vcmd_phone
        )
        self.phone_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            card,
            text="Username:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.username_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30
        )
        self.username_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        tk.Label(
            card,
            text="Password:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.password_entry = tk.Entry(
            card,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            width=30,
            show="*"
        )
        self.password_entry.grid(row=7, column=1, sticky="w", padx=5, pady=5)

        # press enter to go to next entry field
        self.fullname_entry.bind("<Return>", lambda event: self.ssn_entry.focus_set())
        self.ssn_entry.bind("<Return>", lambda event: self.address_entry.focus_set())
        self.address_entry.bind("<Return>", lambda event: self.phone_entry.focus_set())
        self.phone_entry.bind("<Return>", lambda event: self.username_entry.focus_set())
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus_set())

        ttk.Button(
            card,
            text="Create Account",
            style="Accent.TButton",
            command=self.handle_signup
        ).grid(row=8, column=0, columnspan=2, pady=(15, 5), sticky="ew")

        ttk.Button(
            card,
            text="← Back to Login",
            style="Accent.TButton",
            command=lambda: controller.show_frame(LoginPage)
        ).grid(row=9, column=0, columnspan=2, pady=(5, 0), sticky="ew")

    def handle_signup(self):
        import sqlite3

        fullname = self.fullname_entry.get().strip()
        ssn = self.ssn_entry.get().strip()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not (fullname and ssn and address and phone and username and password):
            messagebox.showerror("Error", "Please fill out all fields.", parent=self)
            return

        try:
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM USERS WHERE username = ?", (username,))
            if cur.fetchone():
                conn.close()
                messagebox.showerror("Error", "Username is already taken.", parent=self)
                return

            cur.execute("SELECT card_id FROM BORROWER WHERE ssn = ?", (ssn,))
            if cur.fetchone():
                conn.close()
                messagebox.showerror("Error", "An account with this SSN already exists.", parent=self)
                return

            cur.execute("SELECT MAX(CAST(SUBSTR(card_id, 3) AS INTEGER)) FROM BORROWER")
            result = cur.fetchone()[0]
            new_number = int(result) + 1 if result else 1
            new_card_id = f"ID{new_number:06d}"

            cur.execute("""
                INSERT INTO BORROWER (card_id, Ssn, Bname, Address, Phone)
                VALUES (?, ?, ?, ?, ?)
            """, (new_card_id, ssn, fullname, address, phone))

            cur.execute("""
                INSERT INTO USERS (username, password, card_id, is_librarian)
                VALUES (?, ?, ?, 0)
            """, (username, password, new_card_id))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Account created.\nYour Card ID: {new_card_id}",
                parent=self
            )

            login_page = self.controller.frames[LoginPage]
            login_page.username_entry.delete(0, tk.END)
            login_page.username_entry.insert(0, username)
            login_page.password_entry.delete(0, tk.END)
            login_page.password_entry.insert(0, password)

            self.controller.show_frame(LoginPage)

        except Exception as e:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass
            messagebox.showerror("Error", f"Database error during sign up:\n{e}", parent=self)

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG_COLOR)
        self.controller = controller

        top_bar = tk.Frame(self, bg="#2e1a47", height=60)
        top_bar.pack(fill="x")

        tk.Label(
            top_bar,
            text=" 📖 Magnesium Library 📖 ",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#2e1a47"
        ).pack(pady=10)

        # Centering container
        outer = tk.Frame(self, bg=theme.BG_COLOR)
        outer.pack(expand=True)

        # Card-style container
        content_frame = tk.Frame(
            outer,
            bg=theme.CARD_BG,
            padx=30,
            pady=30,
            highlightthickness=2,
            highlightbackground=theme.OUTLINE_COLOR
        )
        content_frame.pack()

        # Title
        tk.Label(
            content_frame,
            text="Library Management System",
            font=theme.FONT_TITLE,
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN
        ).pack(pady=(0, 5))

        # Helper to create buttons (we will pack them later in refresh_for_user)
        def nav_button(text, page):
            return ttk.Button(
                content_frame,
                text=text,
                style="Accent.TButton",
                command=lambda: controller.show_frame(page)
            )

        # Store button references
        self.btn_search = nav_button("🔍  Search Books", SearchPage)
        self.btn_loans = nav_button("📚  Manage Loans", LoansPage)
        self.btn_borrowers = nav_button("👤  Manage Borrowers", BorrowersPage)
        self.btn_fines = nav_button("💸  Manage Fines", FinesPage)

        # Logout button – clears user context and returns to Login page
        self.btn_logout = ttk.Button(
            content_frame,
            text="Logout",
            style="Accent.TButton",
            command=self._handle_logout
        )

        # Initial layout based on current user (at app start)
        self.refresh_for_user()

    def _handle_logout(self):
        """Clear user context and go back to login."""
        self.controller.current_user = None
        self.controller.current_card_id = None
        self.controller.is_librarian = False
        self.controller.show_frame(LoginPage)

    def refresh_for_user(self):
        for btn in (
            self.btn_search,
            self.btn_loans,
            self.btn_borrowers,
            self.btn_fines,
            self.btn_logout,
        ):
            btn.pack_forget()

        # Search is always visible
        self.btn_search.pack(fill="x", pady=6, ipady=3)
        self.btn_search.state(["!disabled", "!active"])

        # Only librarians see these
        if self.controller.is_librarian:
            for btn in (self.btn_loans, self.btn_borrowers, self.btn_fines):
                btn.pack(fill="x", pady=6, ipady=3)
                btn.state(["!disabled", "!active"])

        # Logout always visible
        self.btn_logout.pack(fill="x", pady=(12, 0), ipady=3)
        self.btn_logout.state(["!disabled", "!active"])

        # Force redraw
        self.update_idletasks()

def fix_button_state(btn):
    btn.state(["!disabled", "!active"])



        

class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg = theme.BG_COLOR)

        self.controller = controller 

        #Title
        topBar = tk.Frame(self, bg = theme.BG_COLOR)
        topBar.pack(fill="x")

        tk.Label(
            topBar,
            text="Search Books",
            font = theme.FONT_TITLE,
            bg = theme.BG_COLOR,
            fg = "white"
        ).pack(side = "left")

        ttk.Button(
            topBar,
            text="← Back to Home",
            style="Accent.TButton",
            command=lambda: controller.show_frame(HomePage)
        ).pack(side="right")

        # Search bar
        search_frame = tk.Frame(self, bg=theme.CARD_BG, padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            search_frame,
            text = "Search by Title, Author, or ISBN:",
            bg = theme.CARD_BG,
            fg = theme.TEXT_MAIN,
            font = theme.FONT_BODY  
        ).grid(row = 0, column = 0, sticky = "w")

        self.search_entry = tk.Entry(
            search_frame,
            width=50,
            bg=theme.INPUT_BG,          # light pastel background
            fg=theme.TEXT_MAIN,         # dark plum or near-black text
            insertbackground=theme.TEXT_MAIN,
            relief="flat",
            highlightthickness=2,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.search_entry.grid(row = 1, column = 0, pady = 5, sticky = "w")
        # enable pressing Enter to search
        self.search_entry.bind("<Return>", lambda event: self.perform_search())

        #Search button
        ttk.Button(
            search_frame,
            text="Search",
            style="Accent.TButton",
            command=self.perform_search
        ).grid(row =1, column=1, padx=10)

        #Table to show search results
        table_frame = tk.Frame(self, bg=theme.BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ISBN", "Title", "Authors", "Availability", "BorrowerID"),
            show="headings",
            style="Treeview",
            selectmode="browse"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")  
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_book_selected)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

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

    def on_book_selected(self, event):
        """When a book is selected in the search results, autofill ISBN in LoansPage."""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        if not values:
            return

        raw_isbn = str(values[0]).strip()
        isbn_str = raw_isbn.zfill(10)  # keep leading zeros

        # get the LoansPage instance from the controller and set its ISBN entry
        try:
            loans_page = self.controller.frames[LoansPage]
            loans_page.isbn_entry.delete(0, tk.END)
            loans_page.isbn_entry.insert(0, isbn_str)
        except Exception:
            # if LoansPage isn't available for some reason, just ignore
            pass
    def copy_isbn_from_row(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        if not values:
            return

        raw_isbn = str(values[0]).strip()
        isbn_str = raw_isbn.zfill(10)

        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(isbn_str)

        # Give small visual feedback in title bar
        self.controller.title(f"Copied ISBN: {isbn_str}")
        self.after(1200, lambda: self.controller.title("Library Management System"))

    def on_tree_double_click(self, event):
        """Double-click copies the ISBN and jumps to the Loans page."""
        self.send_to_loans()

    def send_to_loans(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])["values"]
        if not values:
            return
        
        raw_isbn = str(values[0]).strip()
        borrower_id = values[4]  # BorrowerID column

        normalized_isbn = raw_isbn.replace("-", "").replace(" ", "").zfill(10)
        loans_page = self.controller.frames[LoansPage]

        # Autofill ISBN field
        loans_page.isbn_entry.delete(0, tk.END)
        loans_page.isbn_entry.insert(0, normalized_isbn)

        # If the book is currently checked out, also prefill card ID
        if borrower_id:
            loans_page.card_entry.delete(0, tk.END)
            loans_page.card_entry.insert(0, borrower_id)

        # Try to highlight it in Available Books (iff Availability == IN)
        loans_page.focus_available_book(raw_isbn)

        #Switch to Loans page
        self.controller.show_frame(LoansPage)

class LoansPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg = theme.BG_COLOR)

        topBar = tk.Frame(self, bg=theme.BG_COLOR)
        topBar.pack(fill="x", pady=10, padx=10)

        tk.Label(
            topBar,
            text="Manage Loans (Checkout / Check-in)",
            font=theme.FONT_TITLE,
            bg=theme.BG_COLOR,
            fg="white"
        ).pack(side="left")

        ttk.Button(
            topBar,
            text="← Back to Home",
            style="Accent.TButton",
            command=lambda: controller.show_frame(HomePage)
        ).pack(side="right")

        #Checkout section
        checkout_frame = tk.LabelFrame(
            self,
            text="Checkout Book",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            padx=10,
            pady=10
        )
        checkout_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            checkout_frame,
            text="ISBN:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.isbn_entry = tk.Entry(
            checkout_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.isbn_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            checkout_frame,
            text="Borrower Card ID:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.card_entry = tk.Entry(
            checkout_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.card_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Button(
            checkout_frame,
            text="Checkout by ISBN",
            style="Accent.TButton",
            command=self.checkout_by_isbn
        ).grid(row=0, column=4, padx=5, pady=5)

        #Table of available books to select
        avail_frame = tk.Frame(self, bg=theme.BG_COLOR)
        avail_frame.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        tk.Label(
            avail_frame,
            text="Available Books",
            bg=theme.BG_COLOR,
            fg="white",
            font= theme.FONT_SUBTITLE
        ).pack(anchor="w", pady=(0, 3))

        self.available_tree = ttk.Treeview(
            avail_frame,
            columns=("ISBN", "Title", "Authors"),
            show="headings",
            selectmode="browse",
            style="Treeview"
        )
        for col in self.available_tree["columns"]:
            self.available_tree.heading(col, text=col)
            self.available_tree.column(col, width=200, anchor="w")
        self.available_tree.pack(fill="both", expand=True, padx=0, pady=0)

        # autofill ISBN when selecting a book
        self.available_tree.bind("<<TreeviewSelect>>", self.on_available_book_select)

        ttk.Button(
            self,
            text="Checkout Selected Book",
            style="Accent.TButton",
            command=self.checkout_selected_book
        ).pack(pady=5)

        #Check in section
        checkin_frame = tk.LabelFrame(
            self,
            text="Check-in Books",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            padx=10,
            pady=10
        )
        checkin_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.checked_out_tree = ttk.Treeview(
            checkin_frame,
            columns=("Loan ID", "ISBN", "Title", "Borrower ID", "Due Date"),
            show="headings",
            selectmode="browse",
            style="Treeview"
        )
        for col in self.checked_out_tree["columns"]:
            self.checked_out_tree.heading(col, text=col)
            self.checked_out_tree.column(col, width=150, anchor="w")
        self.checked_out_tree.pack(fill="both", expand=True, padx=0, pady=5)

        ttk.Button(
            checkin_frame,
            text="Check-in Selected Book",
            style="Accent.TButton",
            command=self.checkin_selected_book
        ).pack(pady=5)

        self.load_available_books()
        self.load_checked_out_books()

    #Helper functions
    def load_available_books(self):
        for row in self.available_tree.get_children():
            self.available_tree.delete(row)
        results = library.search_books("")  
        for item in results:
            if item["Availability"] == "IN":
                isbn = str(item["Isbn"]).strip().zfill(10)
                self.available_tree.insert(
                    "",
                    "end",
                    values=(isbn, item["Title"], item["Authors"])
                )
    
    def focus_available_book(self, isbn_raw):
        """
        Focus and select a book in the available books tree by its raw ISBN.
        """
        target = str(isbn_raw).replace("-", "").replace(" ", "").strip().zfill(10)

        for item_id in self.available_tree.get_children():
            row_isbn = str(self.available_tree.item(item_id)["values"][0])
            row_isbn_norm = row_isbn.replace("-", "").replace(" ", "").strip().zfill(10)

            if row_isbn_norm == target:
                self.available_tree.selection_set(item_id)
                self.available_tree.focus(item_id)
                self.available_tree.see(item_id)
                break


    def load_checked_out_books(self):
        for row in self.checked_out_tree.get_children():
            self.checked_out_tree.delete(row)
        results = library.getBooksCheckedOut("")  #Get all checked out books
        for item in results:
            self.checked_out_tree.insert("", "end", values=(item["Loan_id"], item["Isbn"], item["Title"], item["Card_id"], item["Due_date"]))

    def on_available_book_select(self, event):
        selected = self.available_tree.selection()
        if not selected:
            return

        raw = str(self.available_tree.item(selected[0])["values"][0]).strip()
        isbn_str = raw.zfill(10)

        self.isbn_entry.delete(0, tk.END)
        self.isbn_entry.insert(0, isbn_str)


    #Checkout methods
    #Checkout by isbn requires you to enter a valid isbn and borrower id to checkout a max of 3 books
    def checkout_by_isbn(self):
        isbn = self.isbn_entry.get().strip()
        card_id = self.card_entry.get().strip()
        if not isbn or not card_id:
            messagebox.showerror("Error", "Please enter both ISBN and Borrower Card ID", parent=self)
            return
        success, msg = library.checkout_book(isbn, card_id)
        if success:
            messagebox.showinfo("Success", msg, parent = self)
        else:
            messagebox.showerror("Error", msg, parent = self)
        self.load_available_books()
        self.load_checked_out_books()

    #Click / select a book to highlight it then enter a valid borrower id and select checkout button to checkout
    def checkout_selected_book(self):
        selected = self.available_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book from the table", parent=self)
            return

        isbn = str(self.available_tree.item(selected[0])["values"][0])
        card_id = self.card_entry.get().strip()
        isbn = isbn.replace("-", "").replace(" ", "").zfill(10) #When retrieving values from tree it removes leading zeroes, add them back (All isbns are 10 chars)

        if not card_id:
            messagebox.showerror("Error", "Please enter Borrower Card ID", parent=self)
            return

        success, msg = library.checkout_book(isbn, card_id)
        if success:
            messagebox.showinfo("Success", msg, parent = self)
        else:
            messagebox.showerror("Error", msg, parent = self)

        self.load_available_books()
        self.load_checked_out_books()

    #Checkin methods
    def checkin_selected_book(self):
        selected = self.checked_out_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a book to check-in", parent=self)
            return
        loan_id = self.checked_out_tree.item(selected[0])["values"][0]
        success, msg = library.checkin_book(loan_id)
        if success:
            messagebox.showinfo("Success", msg, parent = self)
        else:
            messagebox.showerror("Error", msg, parent= self)
        self.load_available_books()
        self.load_checked_out_books()

#4 my tr maan
class BorrowersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG_COLOR)

        self.controller = controller
        self.last_card_id = None # To track last created borrower

        # validation commands for SSN (9 digits) and Phone (10 digits)
        vcmd_ssn = (self.register(validate_digits_with_limit), "%P", "9")
        vcmd_phone = (self.register(validate_digits_with_limit), "%P", "10")

        # Top bar
        topBar = tk.Frame(self, bg=theme.BG_COLOR)
        topBar.pack(fill="x", pady=10, padx=10)

        tk.Label(
            topBar,
            text="Borrower Management",
            font=theme.FONT_TITLE,
            bg=theme.BG_COLOR,
            fg="white"
        ).pack(side="left")

        ttk.Button(
            topBar,
            text="← Back to Home",
            style="Accent.TButton",
            command=lambda: controller.show_frame(HomePage)
        ).pack(side="right")

        card = tk.Frame(self, bg=theme.CARD_BG, padx=20, pady=20)
        card.pack(pady=20, padx=20)

        form_frame = tk.Frame(card, bg=theme.CARD_BG)
        form_frame.pack(pady=10)

        # --- Input Fields ---
        tk.Label(
            form_frame,
            text="Full Name:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = tk.Entry(
            form_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(
            form_frame,
            text="SSN:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.ssn_entry = tk.Entry(
            form_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            validate="key",
            validatecommand=vcmd_ssn
        )
        self.ssn_entry.grid(row=1, column=1, pady=5)

        tk.Label(
            form_frame,
            text="Address:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.address_entry = tk.Entry(
            form_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.address_entry.grid(row=2, column=1, pady=5)

        tk.Label(
            form_frame,
            text="Phone:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.phone_entry = tk.Entry(
            form_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR,
            validate="key",
            validatecommand=vcmd_phone
        )
        self.phone_entry.grid(row=3, column=1, pady=5)

        # press enter to go to next entry field
        self.name_entry.bind("<Return>", lambda event: self.ssn_entry.focus_set())
        self.ssn_entry.bind("<Return>", lambda event: self.address_entry.focus_set())
        self.address_entry.bind("<Return>", lambda event: self.phone_entry.focus_set())

        # --- Buttons ---
        ttk.Button(
            card,
            text="Create Borrower",
            style="Accent.TButton",
            command=self.create_borrower
        ).pack(pady=10)

        # --- Status Message ---
        self.status_label = tk.Label(
            card,
            text="",
            bg=theme.CARD_BG,
            fg="red",
            font=theme.FONT_BODY,
            cursor="hand2"   # hand cursor to indicate clickable
        )
        self.status_label.pack(pady=5)
        self.status_label.bind("<Button-1>", self.copy_card_to_clipboard)

    def create_borrower(self):
        name = self.name_entry.get().strip()
        ssn = self.ssn_entry.get().strip()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()

        # 1. Validate required fields (NOT NULL)
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

            # 2. Enforce ONE borrower per SSN
            cur.execute("SELECT card_id FROM BORROWER WHERE ssn = ?", (ssn,))
            if cur.fetchone():
                self.status_label.config(
                    text="Error: A borrower with this SSN already exists.",
                    fg="red"
                )
                conn.close()
                return

            # 3. Auto-generate new card_id in the format ID000001
            cur.execute("SELECT MAX(CAST(SUBSTR(card_id, 3) AS INTEGER)) FROM BORROWER")
            result = cur.fetchone()[0]
            new_number = int(result) + 1 if result else 1
            new_card_id = f"ID{new_number:06d}"  # ID + 6-digit zero-padded number

            # 4. Insert new borrower
            cur.execute("""
                INSERT INTO BORROWER (card_id, bname, address, phone, ssn)
                VALUES (?, ?, ?, ?, ?)
            """, (new_card_id, name, address, phone, ssn))

            # 5. Also create a login in USERS:
            #    username = card_id, password = SSN, is_librarian = 0
            cur.execute("""
                INSERT INTO USERS (username, password, card_id, is_librarian)
                VALUES (?, ?, ?, 0)
            """, (new_card_id, ssn, new_card_id))

            conn.commit()
            conn.close()

            # 6. Success message + clear form
            self.last_card_id = new_card_id

            self.status_label.config(
                text=(
                    f"Borrower created successfully. Card No: {new_card_id} (click to copy). "
                    f"Login Username: {new_card_id}, Password: {ssn}"
                ),
                fg="green"
            )

            # prefill card id in LoansPage if possible
            try:
                loans_page = self.controller.frames[LoansPage]
                loans_page.card_entry.delete(0, tk.END)
                loans_page.card_entry.insert(0, new_card_id)
            except Exception:
                pass
            
            # prefill card id in FinesPage if possible
            try:
                fines_page = self.controller.frames[FinesPage]
                fines_page.card_entry.delete(0, tk.END)
                fines_page.card_entry.insert(0, new_card_id)
            except Exception:
                pass

            self.name_entry.delete(0, tk.END)
            self.ssn_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)

        except Exception as e:
            self.status_label.config(
                text=f"Database Error: {str(e)}",
                fg="red"
            )


    def copy_card_to_clipboard(self, event=None):
        """Copy the last created Card ID to the clipboard when the status label is clicked."""
        if not self.last_card_id:
            # nothing to copy yet
            return

        # copy to system clipboard
        self.clipboard_clear()
        self.clipboard_append(self.last_card_id)

        # small visual feedback
        self.status_label.config(
            text=f"Card No: {self.last_card_id} copied to clipboard!",
            fg="green"
        )
    
#-------------------- Fines Page --------------------
class FinesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=theme.BG_COLOR)

        # Top bar
        topBar = tk.Frame(self, bg=theme.BG_COLOR)
        topBar.pack(fill="x", pady=10, padx=10)

        tk.Label(
            topBar,
            text="Fines Management",
            font=theme.FONT_TITLE,
            bg=theme.BG_COLOR,
            fg="white"
        ).pack(side="left")

        ttk.Button(
            topBar,
            text="← Back to Home",
            style="Accent.TButton",
            command=lambda: controller.show_frame(HomePage)
        ).pack(side="right")

        # Card container
        card = tk.Frame(self, bg=theme.CARD_BG, padx=20, pady=15)
        card.pack(fill="both", expand=True, padx=15, pady=10)

        search_frame = tk.Frame(card, bg=theme.CARD_BG)
        search_frame.pack(pady=5, fill="x")

        tk.Label(
            search_frame,
            text="Borrower ID:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.card_entry = tk.Entry(
            search_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.card_entry.grid(row=0, column=1, pady=5)
        self.card_entry.bind("<Return>", lambda event: self.search_fines())

        tk.Label(
            search_frame,
            text="Borrower Name:",
            bg=theme.CARD_BG,
            fg=theme.TEXT_MAIN,
            font=theme.FONT_BODY
        ).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(
            search_frame,
            bg=theme.INPUT_BG,
            fg=theme.INPUT_FG,
            insertbackground=theme.INPUT_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.OUTLINE_COLOR
        )
        self.name_entry.grid(row=0, column=3, pady=5)
        self.name_entry.bind("<Return>", lambda event: self.search_fines())

        ttk.Button(
            search_frame,
            text="Search Fines",
            style="Accent.TButton",
            command=self.search_fines
        ).grid(row=0, column=4, padx=5)

        ttk.Button(
            search_frame,
            text="Refresh Fines",
            style="Accent.TButton",
            command=self.refresh_fines
        ).grid(row=0, column=5, padx=5)

        # --- Table ---
        self.tree = ttk.Treeview(
            card,
            columns=("card", "name", "total"),
            show="headings",
            style="Treeview"
        )
        self.tree.heading("card", text="Card ID")
        self.tree.heading("name", text="Borrower Name")
        self.tree.heading("total", text="Total Fine ($)")
        self.tree.column("card", width=120, anchor="center")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("total", width=120, anchor="center")
        self.tree.pack(pady=10, fill="both", expand=True)

        ttk.Button(
            card,
            text="Pay Selected Fine",
            style="Accent.TButton",
            command=self.pay_fine
        ).pack(pady=5)

        self.message = tk.Label(
            card,
            text="",
            bg=theme.CARD_BG,
            fg="red",
            font=theme.FONT_BODY
        )
        self.message.pack(pady=5)
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
        # clear old rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        import sqlite3
        conn = sqlite3.connect("library.db")
        cur = conn.cursor()

        card = self.card_entry.get().strip()
        name = self.name_entry.get().strip()

        # base SELECT
        base = """
            SELECT B.card_id, B.bname, SUM(F.fine_amt)
            FROM BORROWER B
            JOIN BOOK_LOANS L ON B.card_id = L.card_id
            JOIN FINES F ON L.loan_id = F.loan_id
        """

        params = []

        # build WHERE depending on which fields are filled
        if card and name:
            # match EITHER the card OR the name
            where_clause = "WHERE F.paid = 0 AND (B.card_id = ? OR B.bname LIKE ?)"
            params = [card, f"%{name}%"]
        elif card:
            where_clause = "WHERE F.paid = 0 AND B.card_id = ?"
            params = [card]
        elif name:
            where_clause = "WHERE F.paid = 0 AND B.bname LIKE ?"
            params = [f"%{name}%"]
        else:
            # no filters → all unpaid fines
            where_clause = "WHERE F.paid = 0"

        group_by = " GROUP BY B.card_id, B.bname"

        query = base + " " + where_clause + group_by

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
