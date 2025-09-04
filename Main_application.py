import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2


# --- اتصال به دیتابیس ---
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="library_db",
            user="postgres",
            password="1384m1384_Ms",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return None


# --- کلاس پایه CRUDFrame ---
class CRUDFrame(tb.Frame):
    def __init__(self, parent, title, columns, table_name):
        super().__init__(parent)
        self.title = title
        self.columns = columns
        self.table_name = table_name
        self.selected_item = None
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # عنوان صفحه
        tb.Label(self, text=self.title, font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)

        # فریم دکمه‌ها
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=5)

        tb.Button(btn_frame, text="Add", bootstyle=SUCCESS, command=self.open_add_form).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Edit", bootstyle=INFO, command=self.open_edit_form).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Delete", bootstyle=DANGER, command=self.delete_item).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="Refresh", bootstyle=WARNING, command=self.refresh_table).pack(side=LEFT, padx=5)

        # فرم ورودی
        self.form_frame = tb.Frame(self)
        self.form_frame.pack(fill=X, padx=10, pady=5)
        self.form_fields = {}

        for i, col in enumerate(self.columns[1:]):  # ID رو نمی‌گذاریم توی فرم
            tb.Label(self.form_frame, text=f"{col}:", width=15).grid(row=i, column=0, sticky=W, padx=5, pady=2)
            entry = tb.Entry(self.form_frame)
            entry.grid(row=i, column=1, sticky=EW, padx=5, pady=2)
            self.form_fields[col] = entry

        tb.Button(self.form_frame, text="Submit", bootstyle=SUCCESS, command=self.submit_form).grid(
            row=len(self.columns), columnspan=2, pady=5)

        # جدول داده
        table_frame = tb.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=W)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)

        # جستجو
        search_frame = tb.Frame(self)
        search_frame.pack(fill=X, padx=10, pady=5)

        tb.Label(search_frame, text="Search:", width=8).pack(side=LEFT, padx=5)
        self.search_entry = tb.Entry(search_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        tb.Button(search_frame, text="🔍", width=3, bootstyle=INFO, command=self.on_search).pack(side=LEFT, padx=2)
        tb.Button(search_frame, text="✖", width=3, bootstyle=SECONDARY, command=self.clear_search).pack(side=LEFT, padx=2)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_from_db(self, query=None, params=None):
        self.tree.delete(*self.tree.get_children())
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            if query:
                cur.execute(query, params or ())
            else:
                cur.execute(f"SELECT * FROM {self.table_name}")
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def refresh_table(self, query=None, params=None):
        self.load_from_db(query, params)

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_item = self.tree.item(selected[0])['values']
        else:
            self.selected_item = None

    def submit_form(self):
        values = [entry.get() for entry in self.form_fields.values()]
        if not all(values):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            if self.selected_item:
                new_values = (self.selected_item[0], *values)
                self.update_item(self.selected_item, new_values)
            else:
                self.add_item(tuple(values))
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def add_item(self, item_data):
        raise NotImplementedError("Implement add_item")

    def update_item(self, old_data, new_data):
        raise NotImplementedError("Implement update_item")

    def delete_item(self):
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            conn = connect_db()
            if not conn:
                return
            cur = conn.cursor()
            try:
                cur.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (self.selected_item[0],))
                conn.commit()
                self.refresh_table()
                self.selected_item = None
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                cur.close()
                conn.close()

    def open_add_form(self, edit_mode=False, item=None):
        self.clear_form()
        if edit_mode and item:
            for (field, entry), value in zip(self.form_fields.items(), item[1:]):
                entry.delete(0, tk.END)
                entry.insert(0, str(value))

    def open_edit_form(self):
        if not self.selected_item:
            messagebox.showwarning("Warning", "Please select an item first!")
            return
        self.open_add_form(edit_mode=True, item=self.selected_item)

    def clear_form(self):
        for entry in self.form_fields.values():
            entry.delete(0, tk.END)

    def on_search(self):
        keyword = self.search_entry.get()
        if keyword:
            self.perform_search(keyword)
        else:
            self.refresh_table()

    def perform_search(self, keyword):
        raise NotImplementedError("Implement perform_search")

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_table()


class BooksPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Books Management",
                        ("ID", "Name", "Publish Date", "Description", "Number of Books", "Language"), "books")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO books (name, publish_date, description, number_of_books, language)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE books SET name=%s, publish_date=%s, description=%s, number_of_books=%s, language=%s
                WHERE id=%s
            """, (*new_data[1:], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT id, name, publish_date, description, number_of_books, language 
        FROM books
        WHERE name ILIKE %s OR description ILIKE %s OR language ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)


class AuthorsPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Authors Management",
                        ("ID", "First Name", "Last Name", "Start of Activity", "Language"), "authors")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO authors (first_name, last_name, start_of_activity, language)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE authors SET first_name=%s, last_name=%s, start_of_activity=%s, language=%s
                WHERE id=%s
            """, (*new_data[1:], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT id, first_name, last_name, start_of_activity, language 
        FROM authors
        WHERE first_name ILIKE %s OR last_name ILIKE %s OR language ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)


class PublishersPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Publishers Management", ("ID", "Name", "Address"), "publishers")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO publishers (name, address)
                VALUES (%s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE publishers SET name=%s, address=%s
                WHERE id=%s
            """, (*new_data[1:], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT id, name, address FROM publishers
        WHERE name ILIKE %s OR address ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)

class GenresPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Genres Management", ("ID", "Name"), "genres")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO genres (name)
                VALUES (%s) RETURNING id
            """, (item_data[0],))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE genres SET name=%s WHERE id=%s
            """, (new_data[1], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = "SELECT * FROM genres WHERE name ILIKE %s"
        params = (f"%{keyword}%",)
        self.refresh_table(query, params)


class PeoplePage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "People Management",
                        ("ID", "First Name", "Last Name", "Is_Staff", "Address", "Is_active"), "people")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO people (first_name, last_name, email, phone, address)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE people SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s
                WHERE id=%s
            """, (*new_data[1:], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT id, first_name, last_name, email, phone, address 
        FROM people
        WHERE first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s OR phone ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)


class BookAuthorsPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Book-Authors Relationships", ("ID", "Book ID", "Author ID"), "book_authors")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO book_authors (book_id, author_id)
                VALUES (%s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE book_authors SET book_id=%s, author_id=%s
                WHERE id=%s
            """, (new_data[1], new_data[2], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT ba.id, b.name, a.first_name || ' ' || a.last_name AS author
        FROM book_authors ba
        JOIN books b ON ba.book_id = b.id
        JOIN authors a ON ba.author_id = a.id
        WHERE b.name ILIKE %s OR a.first_name ILIKE %s OR a.last_name ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)

class BookGenresPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Book-Genres Relationships", ("ID", "Book ID", "Genre ID"), "book_genres")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO book_genres (book_id, genre_id)
                VALUES (%s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE book_genres SET book_id=%s, genre_id=%s
                WHERE id=%s
            """, (new_data[1], new_data[2], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT bg.id, b.name, g.name
        FROM book_genres bg
        JOIN books b ON bg.book_id = b.id
        JOIN genres g ON bg.genre_id = g.id
        WHERE b.name ILIKE %s OR g.name ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)


class BookPublishersPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Book-Publishers Relationships", ("ID", "Book ID", "Publisher ID"), "book_publishers")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO book_publishers (book_id, publisher_id)
                VALUES (%s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE book_publishers SET book_id=%s, publisher_id=%s
                WHERE id=%s
            """, (new_data[1], new_data[2], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT bp.id, b.name, p.name
        FROM book_publishers bp
        JOIN books b ON bp.book_id = b.id
        JOIN publishers p ON bp.publisher_id = p.id
        WHERE b.name ILIKE %s OR p.name ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)

class BorrowingsPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Borrowings Management",
                        ("ID", "Book ID", "Person ID", "Borrow Date", "Return Date", "Status"), "borrowings")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO borrowings (book_id, person_id, borrow_date, return_date, status)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE borrowings SET book_id=%s, person_id=%s, borrow_date=%s, return_date=%s, status=%s
                WHERE id=%s
            """, (*new_data[1:], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT id, book_id, person_id, borrow_date, return_date, status 
        FROM borrowings
        WHERE book_id::TEXT ILIKE %s OR person_id::TEXT ILIKE %s OR status ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)


class BorrowingsPage(CRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Borrowings Management",
                        ("ID", "Book ID", "Person ID", "Borrow Date", "Return Date", "Status"), "borrowings")

    def add_item(self, item_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO borrowings (book_id, person_id, borrow_date, return_date, status)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, item_data)
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def update_item(self, old_data, new_data):
        conn = connect_db()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE borrowings SET book_id=%s, person_id=%s, borrow_date=%s, return_date=%s, status=%s
                WHERE id=%s
            """, (*new_data[1:], new_data[0]))
            conn.commit()
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def perform_search(self, keyword):
        query = """
        SELECT id, book_id, person_id, borrow_date, return_date, status 
        FROM borrowings
        WHERE book_id::TEXT ILIKE %s OR person_id::TEXT ILIKE %s OR status ILIKE %s
        """
        params = (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        self.refresh_table(query, params)


class MainApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Library Admin Panel")
        self.geometry("1200x700")
        self.create_ui()

    def create_ui(self):
        main_container = tb.Frame(self)
        main_container.pack(fill=BOTH, expand=True)

        sidebar = tb.Frame(main_container, width=200, bootstyle="secondary")
        sidebar.pack(side=LEFT, fill=Y)

        content_area = tb.Frame(main_container)
        content_area.pack(side=LEFT, fill=BOTH, expand=True)

        categories = {
            "Entities": ["Books", "Authors", "Genres", "People", "Publishers"],
            "Relationships": ["Book-Authors", "Book-Genres", "Book-Publishers"],
            "Operations": ["Borrowings"]
        }

        for category, items in categories.items():
            lbl = tb.Label(sidebar, text=category, font=("Arial", 10, "bold"), bootstyle="inverse-secondary")
            lbl.pack(pady=(10, 5), padx=5, fill=X)
            for item in items:
                tb.Button(sidebar, text=item, command=lambda name=item: self.show_page(name)).pack(
                    pady=2, padx=5, fill=X)

        self.pages = {
            "Books": BooksPage(content_area),
            "Authors": AuthorsPage(content_area),
            "Genres": GenresPage(content_area),
            "People": PeoplePage(content_area),
            "Publishers": PublishersPage(content_area),
            "Book-Authors": BookAuthorsPage(content_area),
            "Book-Genres": BookGenresPage(content_area),
            "Book-Publishers": BookPublishersPage(content_area),
            "Borrowings": BorrowingsPage(content_area),
        }

        self.show_page("Books")

    def show_page(self, name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[name].pack(fill=BOTH, expand=True)


if __name__ == '__main__':
    app = MainApp()
    app.mainloop()