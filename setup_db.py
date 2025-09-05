import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import getpass

# تنظیمات دیتابیس
DB_NAME = "DB NAME"
USER = "USERNAME"
PASSWORD = "PASSWORD"
HOST = "HOST"
PORT = "PORT"

def connect_to_database(db_name):
    """اتصال به یک دیتابیس مشخص"""
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        print(f"✅ Connected to database: {db_name}")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Cannot connect to database '{db_name}': {e}")
        return None

def create_database():
    """ایجاد دیتابیس library_db اگر وجود نداشته باشه"""
    print(f"🔍 Checking for database '{DB_NAME}'...")
    conn = psycopg2.connect(
        dbname="postgres",
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        try:
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"✅ Database '{DB_NAME}' created successfully.")
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            cur.close()
            conn.close()
            return False
    else:
        print(f"🟢 Database '{DB_NAME}' already exists.")

    cur.close()
    conn.close()
    return True

def create_tables(conn):
    """ایجاد تمام جداول لازم در دیتابیس"""
    cur = conn.cursor()

    try:
        # فعال‌سازی UUID (اختیاری)
        cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

        # جدول: genres
        cur.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE
            );
        """)

        # جدول: publishers
        cur.execute("""
            CREATE TABLE IF NOT EXISTS publishers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                address TEXT
            );
        """)

        # جدول: authors
        cur.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                start_of_activity DATE,
                language VARCHAR(50)
            );
        """)

        # جدول: books
        cur.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                publish_date DATE,
                description TEXT,
                number_of_books INTEGER DEFAULT 1,
                language VARCHAR(50)
            );
        """)

        # جدول: people
        cur.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(20),
                address TEXT,
                is_staff BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)

        # جدول: book_authors
        cur.execute("""
            CREATE TABLE IF NOT EXISTS book_authors (
                id SERIAL PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
                UNIQUE(book_id, author_id)
            );
        """)

        # جدول: book_genres
        cur.execute("""
            CREATE TABLE IF NOT EXISTS book_genres (
                id SERIAL PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
                UNIQUE(book_id, genre_id)
            );
        """)

        # جدول: book_publishers
        cur.execute("""
            CREATE TABLE IF NOT EXISTS book_publishers (
                id SERIAL PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                publisher_id INTEGER NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
                UNIQUE(book_id, publisher_id)
            );
        """)

        # جدول: borrowings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS borrowings (
                id SERIAL PRIMARY KEY,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
                borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
                return_date DATE,
                status VARCHAR(50) NOT NULL DEFAULT 'borrowed'
            );
        """)

        conn.commit()
        print("✅ All tables are created or already exist.")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()

    return True

def main():
    print("🚀 Library Database Setup Script")
    print("-" * 40)

    # مرحله ۱: ایجاد دیتابیس (اگر نیست)
    if not create_database():
        print("❌ Database creation failed. Exiting.")
        return

    # مرحله ۲: اتصال به دیتابیس جدید
    conn = connect_to_database(DB_NAME)
    if not conn:
        print("❌ Could not connect to the database. Check your credentials or PostgreSQL service.")
        return

    # مرحله ۳: ایجاد جداول
    if create_tables(conn):
        print("🎉 Database setup completed successfully!")
    else:
        print("❌ Database setup failed.")

    conn.close()

if __name__ == "__main__":
    main()
