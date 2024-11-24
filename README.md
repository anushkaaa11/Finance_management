# Personal Finance Management Application

## **Objective**
The Personal Finance Management Application is a command-line program designed to help users effectively manage their personal finances. Users can track their income, expenses, set budgets, and generate detailed financial reports.

---

## **Features**

### 1. **User Registration and Authentication**
- **Register** with a unique username and password.
- **Login** to access your personal finance data securely.

### 2. **Income and Expense Tracking**
- Add, update, and delete income or expense entries.
- Categorize transactions (e.g., *Food, Rent, Salary, Entertainment*).

### 3. **Financial Reports**
- Generate **monthly** and **yearly** financial reports.
- Calculate:
  - Total income.
  - Total expenses.
  - Savings.

### 4. **Budgeting**
- Set monthly budgets for different categories.
- Receive notifications when budget limits are exceeded.

### 5. **Data Persistence**
- Store user data and transactions using **SQLite**.
- Backup and restore data with simple commands.

### 6. **Testing and Documentation**
- Includes unit tests for key functionalities.
- A comprehensive user manual with installation and usage instructions.

---

## **Installation**

### **Requirements**
- Python 3.8 or higher
- SQLite3 (comes pre-installed with Python)

### **Setup Steps**
1. Clone the repository:
   ```bash
   git clone https://github.com/anushkaaa11/Finance_management.git
   cd personal-finance-app
   ```
2. Install dependencies (if required):
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   python database.py
   ```
4. Run the application:
   ```bash
   python main.py
   ```

---

## **Usage**
### **Command-Line Options**
1. **Register**:
   - Create an account with a username and password.
2. **Login**:
   - Access your personal finance data securely.
3. **Add Transaction**:
   - Add income or expense entries with categories, amounts, and descriptions.
4. **View Transactions**:
   - List all your transactions.
5. **Generate Financial Reports**:
   - View summarized reports of income, expenses, and savings.
6. **Set Budget**:
   - Define monthly budget limits and track overspending.
7. **Backup/Restore Data**:
   - Safeguard or recover your financial data with backup functionality.

---

## **Project Structure**
```
personal-finance-app/
├── main.py           # Main entry point for the application
├── database.py       # Database initialization and connection
├── user.py           # User registration and login logic
├── transaction.py    # Manage income and expense transactions
├── report.py         # Generate financial reports
├── budget.py         # Handle budgeting features
├── backup.py         # Backup and restore functionality
└── tests/            # Unit tests for application components
    ├── test_user.py
    ├── test_transaction.py
    ├── test_budget.py
    └── test_report.py
```

---

## **Testing**
Run all unit tests using:
```bash
pytest tests/
```

---

## **Future Enhancements**
- Add a graphical user interface (GUI).
- Integrate advanced analytics for spending patterns.
- Support for multiple currencies.

---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Contributing**
Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## **Contact**
For any questions or suggestions, please contact [anushkaranjan141113@gmail.com]. 

Happy budgeting! 🎉
