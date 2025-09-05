# Library Management System / سیستم مدیریت کتابخانه

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17%2B-blue)

## English Version

A comprehensive desktop application for managing library operations, built with Python and PostgreSQL. This system provides an intuitive GUI for handling books, authors, genres, publishers, borrowing records, and their relationships.

### Features

- **Entity Management**: Full CRUD operations for:
  - Books
  - Authors
  - Genres
  - Publishers
  - People (Library members/staff)
  
- **Relationship Management**:
  - Book-Author relationships
  - Book-Genre relationships
  - Book-Publisher relationships
  
- **Borrowing System**: Track book loans with status management
- **Search Functionality**: Quick search across all entities
- **Modern UI**: Clean, dark-themed interface built with ttkbootstrap

### Technology Stack

- **Backend**: Python 3.x
- **Database**: PostgreSQL
- **GUI Framework**: ttkbootstrap (Themed TKinter)
- **Database Connector**: psycopg2

### Installation

#### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

#### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd library-management-system
```

#### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt, install the packages manually:

```bash
pip install ttkbootstrap psycopg2-binary
```

#### Step 3: Database Setup

1. Ensure PostgreSQL is running on your system
2. Run the database setup script:

```bash
python setup_db.py
```

This will:
- Create the `library_db` database (if it doesn't exist)
- Create all necessary tables with proper relationships
- Set up constraints and indexes

#### Step 4: Configuration

Update the database connection settings in `Main_application.py` if needed:

```python
conn = psycopg2.connect(
    dbname="library_db",
    user="postgres",        # Change if different
    password="1384m1384_Ms", # Change to your PostgreSQL password
    host="localhost",       # Change if different
    port="5432"            # Change if different
)
```

### Usage

1. Start the application:

```bash
python Main_application.py
```

2. The application will open with a sidebar navigation and main content area
3. Use the sidebar to navigate between different management sections
4. Each section provides:
   - Add new records
   - Edit existing records
   - Delete records (with confirmation)
   - Search functionality
   - Data table with scrollable view

### Database Schema

The system uses the following tables:

- `books` - Book information
- `authors` - Author details
- `genres` - Book categories
- `publishers` - Publishing companies
- `people` - Library members and staff
- `book_authors` - Many-to-many relationship between books and authors
- `book_genres` - Many-to-many relationship between books and genres
- `book_publishers` - Many-to-many relationship between books and publishers
- `borrowings` - Book lending records

## نسخه فارسی

# سیستم مدیریت کتابخانه

یک برنامه دسکتاپ جامع برای مدیریت عملیات کتابخانه، ساخته شده با پایتون و PostgreSQL. این سیستم یک رابط گرافیکی کاربرپسند برای مدیریت کتاب‌ها، نویسندگان، ژانرها، ناشران، سوابق امانت و روابط بین آنها ارائه می‌دهد.

### ویژگی‌ها

- **مدیریت موجودیت‌ها**: عملیات CRUD کامل برای:
  - کتاب‌ها
  - نویسندگان
  - ژانرها
  - ناشران
  - افراد (اعضا و کارکنان کتابخانه)
  
- **مدیریت روابط**:
  - روابط کتاب-نویسنده
  - روابط کتاب-ژانر
  - روابط کتاب-ناشر
  
- **سیستم امانت**: رهگیری وام‌های کتاب با مدیریت وضعیت
- **قابلیت جستجو**: جستجوی سریع در تمامی موجودیت‌ها
- **رابط کاربری مدرن**: رابط تمیز با تم تیره ساخته شده با ttkbootstrap

### فناوری‌های استفاده شده

- **backend**: پایتون 3.x
- **پایگاه داده**: PostgreSQL
- **چارچوب رابط کاربری**: ttkbootstrap (TKinter با تم)
- **اتصال پایگاه داده**: psycopg2

### نصب و راه‌اندازی

#### پیش‌نیازها

- پایتون 3.8 یا بالاتر
- PostgreSQL 12 یا بالاتر
- pip (مدیریت بسته‌های پایتون)

#### مرحله 1: کلون کردن ریپوزیتوری

```bash
git clone <your-repository-url>
cd library-management-system
```

#### مرحله 2: نصب وابستگی‌های پایتون

```bash
pip install -r requirements.txt
```

اگر فایل requirements.txt ندارید، بسته‌ها را به صورت دستی نصب کنید:

```bash
pip install ttkbootstrap psycopg2-binary
```

#### مرحله 3: راه‌اندازی پایگاه داده

1. مطمئن شوید PostgreSQL روی سیستم شما در حال اجراست
2. اسکریپت راه‌اندازی پایگاه داده را اجرا کنید:

```bash
python setup_db.py
```

این اسکریپت:
- پایگاه داده `library_db` را ایجاد می‌کند (اگر وجود نداشته باشد)
- تمام جداول لازم با روابط مناسب ایجاد می‌کند
- محدودیت‌ها و ایندکس‌ها را تنظیم می‌کند

#### مرحله 4: پیکربندی

در صورت نیاز، تنظیمات اتصال پایگاه داده را در `Main_application.py` به روزرسانی کنید:

```python
conn = psycopg2.connect(
    dbname="library_db",
    user="postgres",        # در صورت متفاوت بودن تغییر دهید
    password="1384m1384_Ms", # پسورد PostgreSQL خود را وارد کنید
    host="localhost",       # در صورت متفاوت بودن تغییر دهید
    port="5432"            # در صورت متفاوت بودن تغییر دهید
)
```

### نحوه استفاده

1. برنامه را راه‌اندازی کنید:

```bash
python Main_application.py
```

2. برنامه با یک نوار کناری برای ناوبری و منطقه محتوای اصلی باز می‌شود
3. از نوار کناری برای حرکت بین بخش‌های مدیریت مختلف استفاده کنید
4. هر بخش امکانات زیر را ارائه می‌دهد:
   - افزودن رکوردهای جدید
   - ویرایش رکوردهای موجود
   - حذف رکوردها (با تایید)
   - قابلیت جستجو
   - جدول داده با قابلیت اسکرول

### ساختار پایگاه داده

سیستم از جداول زیر استفاده می‌کند:

- `books` - اطلاعات کتاب
- `authors` - اطلاعات نویسنده
- `genres` - دسته‌بندی‌های کتاب
- `publishers` - شرکت‌های انتشاراتی
- `people` - اعضا و کارکنان کتابخانه
- `book_authors` - رابطه چند-به-چند بین کتاب‌ها و نویسندگان
- `book_genres` - رابطه چند-به-چند بین کتاب‌ها و ژانرها
- `book_publishers` - رابطه چند-به-چند بین کتاب‌ها و ناشران
- `borrowings` - سوابق امانت کتاب
