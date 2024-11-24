



import sqlite3
import hashlib
import time
from datetime import datetime


# Database connection
conn = sqlite3.connect('finance_manager.db', timeout=10)  # Adjust timeout to avoid "database is locked" errors
cursor = conn.cursor()

# Create necessary tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    date TEXT DEFAULT CURRENT_DATE,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    monthly_limit REAL NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    UNIQUE(user_id, category, month, year),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')
conn.commit()

def get_connection():
    conn = sqlite3.connect('finance_manager.db')  # or your actual database file
    conn.execute("PRAGMA busy_timeout = 3000;")  # Retry timeout (in milliseconds)
    conn.execute("PRAGMA journal_mode = WAL;")  # Enable Write-Ahead Logging (WAL)
    return conn

def set_budget(user_id, category, monthly_limit, month, year):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO budgets (user_id, category, monthly_limit, month, year)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, category, month, year) 
        DO UPDATE SET monthly_limit = excluded.monthly_limit
        ''', (user_id, category, monthly_limit, month, year))

        conn.commit()
        print(f"Budget for '{category}' in {month}-{year} set to {monthly_limit}.")
    except sqlite3.Error as e:
        print("Error setting budget:", e)
    finally:
        conn.close()  # Ensure the connection is always closed

# Hashing function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Registration
def register_user(username, password):
    hashed_password = hash_password(password)
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose a different username.")

# User Login
def login_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    if user:
        print(f"Login successful! Welcome, {username}")
        return user[0]  # Return user ID
    else:
        print("Invalid username or password.")
        return None

# Add Transaction
def add_transaction(user_id):
    try:
        # Prompt for transaction details
        category = input("Enter category: ")
        amount = float(input("Enter amount: "))
        transaction_type = input("Enter type (income/expense): ").lower()
        
        # Validate transaction type
        if transaction_type not in ['income', 'expense']:
            print("Invalid transaction type. Please enter 'income' or 'expense'.")
            return

        # Prompt for date (optional)
        transaction_date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        
        # If no date is entered, default to today
        if not transaction_date:
            transaction_date = datetime.now().strftime('%Y-%m-%d')
        else:
            # Validate the provided date
            try:
                datetime.strptime(transaction_date, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return

        # Insert transaction into the database
        cursor.execute('''
        INSERT INTO transactions (user_id, category, amount, type, date)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, category, amount, transaction_type, transaction_date))
        conn.commit()

        print(f"Transaction added: {category}, {amount}, {transaction_type} on {transaction_date}.")

        # Budget check only for expenses
        if transaction_type == 'expense':
            # Calculate total expense for the category for the current month
            month_start = transaction_date[:8] + '01'  # First day of the month
            cursor.execute('''
            SELECT SUM(amount) FROM transactions 
            WHERE user_id = ? AND category = ? AND type = 'expense' 
            AND date >= ? AND date <= ?
            ''', (user_id, category, month_start, transaction_date))
            total_expense = cursor.fetchone()[0] or 0

            # Fetch the budget for this category
            cursor.execute('''
            SELECT monthly_limit FROM budgets 
            WHERE user_id = ? AND category = ?
            ''', (user_id, category))
            budget_result = cursor.fetchone()

            if budget_result:
                budget_limit = budget_result[0]
                if total_expense > budget_limit:
                    print(f"⚠️ Warning: You have exceeded your budget for '{category}'. Total spent: {total_expense}, Budget: {budget_limit}.")
                else:
                    print(f"✅ You are within the budget for '{category}'. Total spent: {total_expense}, Budget: {budget_limit}.")
            else:
                print(f"No budget set for category '{category}'.")
        else:
            print("No budget check required for income transactions.")
    
    except sqlite3.Error as e:
        print("Error adding transaction:", e)
    except ValueError:
        print("Invalid input. Please enter valid numbers for amount.")



def debug_log(message):
        print(f"[DEBUG] {time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")

# Set Budget
def set_budget(user_id, category, monthly_limit, month, year):
    retries = 3  # Retry 3 times
    attempt = 0
    while attempt < retries:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO budgets (user_id, category, monthly_limit, month, year)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, category, month, year) 
            DO UPDATE SET monthly_limit = excluded.monthly_limit
            ''', (user_id, category, monthly_limit, month, year))

            conn.commit()
            print(f"Budget for '{category}' in {month}-{year} set to {monthly_limit}.")
            conn.close()  # Always close the connection
            break  # Break if successful
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                print(f"Database is locked, retrying... Attempt {attempt + 1}")
                time.sleep(1)  # Wait for 1 second before retrying
                attempt += 1
            else:
                print("Error setting budget:", e)
                break


# Generate Monthly Report
def generate_monthly_report(user_id, month, year):
    try:
        cursor.execute('''
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expense
        FROM transactions
        WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ''', (user_id, f"{int(month):02d}", str(year)))
        
        result = cursor.fetchone()
        total_income = result[0] or 0
        total_expense = result[1] or 0
        savings = total_income - total_expense
        
        print(f"Monthly Report for {month}/{year}:")
        print(f"  Total Income: {total_income}")
        print(f"  Total Expense: {total_expense}")
        print(f"  Savings: {savings}")
    except sqlite3.Error as e:
        print("Error generating monthly report:", e)


# View Budgets
def view_budgets(user_id):
    cursor.execute('SELECT category, monthly_limit FROM budgets WHERE user_id = ?', (user_id,))
    budgets = cursor.fetchall()
    print("\nBudgets:")
    for budget in budgets:
        print(f"Category: {budget[0]}, Monthly Limit: {budget[1]}")

# Backup and Restore Data
def backup_data():
    with open("backup.sql", "w") as f:
        for line in conn.iterdump():
            f.write(f"{line}\n")
    print("Data backed up to 'backup.sql'.")

def restore_data():
    with open("backup.sql", "r") as f:
        sql_script = f.read()
    conn.executescript(sql_script)
    print("Data restored from 'backup.sql'.")

# Main Program
if __name__ == "__main__":
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Add Transaction")
        print("4. Set Budget")
        print("5. Generate Monthly Report")
        print("6. View Budgets")
        print("7. Backup Data")
        print("8. Restore Data")
        print("9. Exit")
        choice = input("Choose an option: ")

        if choice == '1':  # Register
            username = input("Enter username: ")
            password = input("Enter password: ")
            register_user(username, password)

        elif choice == '2':  # Login
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_id = login_user(username, password)

        elif choice == '3':  # Add Transaction
            if 'user_id' in locals():
                # category = input("Enter category: ")
                # amount = float(input("Enter amount: "))
                # type_ = input("Enter type (income/expense): ").lower()
                add_transaction(user_id)
            else:
                print("Please login first.")

        elif choice == '4':  # Set Budget
            if 'user_id' in locals():
                category = input("Enter category: ")
                monthly_limit = float(input("Enter monthly limit: "))
                month = int(input("Enter month (1-12): "))
                year = int(input("Enter year (e.g., 2024): "))
                set_budget(user_id, category, monthly_limit, month, year)
            else:
                print("Please login first.")

        elif choice == '5':  # Generate Monthly Report
            if 'user_id' in locals():
                month = input("Enter month (MM): ")
                year = input("Enter year (YYYY): ")
                generate_monthly_report(user_id, month, year)
            else:
                print("Please login first.")

        elif choice == '6':  # View Budgets
            if 'user_id' in locals():
                view_budgets(user_id)
            else:
                print("Please login first.")

        elif choice == '7':  # Backup Data
            backup_data()

        elif choice == '8':  # Restore Data
            restore_data()

        elif choice == '9':  # Exit
            print("Exiting...")
            conn.close()
            break

        else:
            print("Invalid choice. Please try again.")
conn = sqlite3.connect('finance_manager.db', timeout=10)  # Set timeout to 10 seconds











