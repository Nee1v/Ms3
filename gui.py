import tkinter as tk
from tkinter import ttk, messagebox
import library_app as library  #Backend functions

class MainApp(tk.Tk): #Initialize tkinter window
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("900x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container = tk.Frame(self)
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
        super().__init__(parent)

        #Main frame that will center its child
        content_frame = tk.Frame(self)
        content_frame.pack(expand=True)  #Center vertically and horizontally

        #All the pages for functional requirements
        tk.Label(content_frame, text="Library Management System", font=("Arial", 24)).pack(pady=20)
        tk.Button(content_frame, text="Search Books", width=25,
                  command=lambda: controller.show_frame(SearchPage)).pack(pady=10)
        tk.Button(content_frame, text="Manage Loans", width=25,
                  command=lambda: controller.show_frame(LoansPage)).pack(pady=10)
        tk.Button(content_frame, text="Manage Borrowers", width=25,
                  command=lambda: controller.show_frame(BorrowersPage)).pack(pady=10)
        tk.Button(content_frame, text="Fines", width=25,
                  command=lambda: controller.show_frame(FinesPage)).pack(pady=10)

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

class BorrowersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Borrower Management", font=("Arial", 18)).pack(pady=10)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=10)
        #TODO: Add GUI for adding new borrowers

class FinesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Fines Management", font=("Arial", 18)).pack(pady=10)
        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=10)
        #TODO: Add GUI for viewing and paying fines


# -------------------- Run the App --------------------

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
