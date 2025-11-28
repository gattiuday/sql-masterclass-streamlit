import streamlit as st
import pandas as pd
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
st.set_page_config(
    page_title="SQL MasterClass",
    page_icon="database",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MOCK DATA & DATABASE SETUP ---
def init_db():
    """Initializes the in-memory SQLite database with mock data."""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()

    # Employees Table
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            role TEXT,
            salary INTEGER,
            department TEXT,
            hired_date TEXT
        )
    ''')
    employees_data = [
        (1, "Alice Johnson", "Engineer", 85000, "Engineering", "2021-03-15"),
        (2, "Bob Smith", "Marketing", 62000, "Sales", "2020-06-01"),
        (3, "Charlie Brown", "Engineer", 90000, "Engineering", "2019-11-20"),
        (4, "Diana Prince", "Executive", 120000, "Management", "2018-01-10"),
        (5, "Evan Wright", "Support", 55000, "Customer Support", "2022-08-05"),
        (6, "Fiona Gallagher", "Marketing", 65000, "Sales", "2021-01-30"),
    ]
    cursor.executemany('INSERT INTO employees VALUES (?,?,?,?,?,?)', employees_data)

    # Products Table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER,
            category TEXT,
            stock INTEGER
        )
    ''')
    products_data = [
        (1, "Laptop Pro", 1200, "Electronics", 50),
        (2, "Wireless Mouse", 25, "Accessories", 200),
        (3, "Desk Chair", 150, "Furniture", 30),
        (4, "Monitor 4K", 400, "Electronics", 40),
        (5, "Notebook", 5, "Stationery", 500),
    ]
    cursor.executemany('INSERT INTO products VALUES (?,?,?,?,?)', products_data)

    # Customers Table
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            country TEXT
        )
    ''')
    customers_data = [
        (1, "John Doe", "john@example.com", "USA"),
        (2, "Jane Smith", "jane@test.com", "Canada"),
        (3, "Sam Wilson", "sam@demo.com", "UK"),
    ]
    cursor.executemany('INSERT INTO customers VALUES (?,?,?,?)', customers_data)

    # Orders Table
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total INTEGER,
            category TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    orders_data = [
        (101, 1, "2023-10-01", 1250, "Electronics"),
        (102, 2, "2023-10-02", 25, "Accessories"),
        (103, 1, "2023-10-05", 400, "Electronics"),
        (104, 3, "2023-10-06", 150, "Furniture"),
        (105, 2, "2023-10-07", 50, "Accessories"),
    ]
    cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders_data)

    conn.commit()
    return conn

# Initialize DB in session state to persist across reruns
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = init_db()

# --- CURRICULUM ---
LESSONS = [
    {
        "id": 1,
        "category": "01. Introduction",
        "title": "Introduction to SQL",
        "description": "SQL (Structured Query Language) is used to communicate with databases. A database contains tables, each with rows (records) and columns (fields).",
        "concept": "The SELECT statement is the starting point for all data retrieval. It tells the database which columns you want to see.",
        "task": "List all data from the table 'employees'.",
        "hint": "Use SELECT * FROM employees",
        "defaultQuery": "SELECT * FROM employees",
        "solution": "SELECT * FROM employees",
        "check_func": lambda df: len(df) == 6 and len(df.columns) == 6
    },
    {
        "id": 2,
        "category": "02. Select & Where",
        "title": "SELECT & WHERE",
        "description": "You often need to filter data to find specific records. The WHERE clause allows you to set conditions that rows must meet to be included.",
        "concept": "WHERE acts as a filter. Only rows that evaluate to TRUE are returned. Common operators: =, >, <, >=, <=, <>.",
        "task": "Show all products with a price less than 100.",
        "hint": "SELECT * FROM products WHERE price < 100",
        "defaultQuery": "SELECT * FROM products WHERE price < 100",
        "solution": "SELECT * FROM products WHERE price < 100",
        "check_func": lambda df: len(df) == 2 and (df['price'] < 100).all()
    },
    {
        "id": 3,
        "category": "03. Order & Limit",
        "title": "ORDER BY & LIMIT",
        "description": "Databases don't store data in a specific order. To rank results (e.g., top 10), you must sort them and limit the output.",
        "concept": "ORDER BY sorts the result set. LIMIT restricts the number of rows returned. Always use ORDER BY before LIMIT for consistent results.",
        "task": "Find the 3 most expensive products.",
        "hint": "SELECT * FROM products ORDER BY price DESC LIMIT 3",
        "defaultQuery": "SELECT * FROM products ORDER BY price DESC LIMIT 3",
        "solution": "SELECT * FROM products ORDER BY price DESC LIMIT 3",
        "check_func": lambda df: len(df) == 3 and df.iloc[0]['price'] >= df.iloc[1]['price']
    },
    {
        "id": 4,
        "category": "04. Distinct",
        "title": "DISTINCT Values",
        "description": "Duplicate data is common. The DISTINCT keyword is used to return only distinct (different) values.",
        "concept": "It eliminates duplicate rows from the result set, showing you a unique list of values for the selected column(s).",
        "task": "List unique product categories.",
        "hint": "SELECT DISTINCT category FROM products",
        "defaultQuery": "SELECT DISTINCT category FROM products",
        "solution": "SELECT DISTINCT category FROM products",
        "check_func": lambda df: len(df) == 4 and df['category'].is_unique
    },
    {
        "id": 5,
        "category": "05. Joins",
        "title": "SQL JOINS",
        "description": "Data is often split across multiple tables. JOINs allow you to combine rows from two or more tables based on a related column between them.",
        "concept": "INNER JOIN selects records that have matching values in both tables. We link 'orders' to 'customers' using the customer_id.",
        "task": "Show each order with the customer name.",
        "hint": "SELECT orders.id, customers.name FROM orders JOIN customers ON orders.customer_id = customers.id",
        "defaultQuery": "SELECT orders.id, customers.name FROM orders JOIN customers ON orders.customer_id = customers.id",
        "solution": "SELECT orders.id, customers.name FROM orders JOIN customers ON orders.customer_id = customers.id",
        "check_func": lambda df: len(df) == 5 and 'name' in df.columns and 'id' in df.columns
    },
    {
        "id": 6,
        "category": "06. Group By",
        "title": "GROUP BY",
        "description": "GROUP BY groups rows that have the same values into summary rows, like 'find the number of customers in each country'.",
        "concept": "It is often used with aggregate functions (COUNT, MAX, MIN, SUM, AVG) to group the result-set by one or more columns.",
        "task": "Find total sales (sum of total) per category from the orders table.",
        "hint": "SELECT category, SUM(total) FROM orders GROUP BY category",
        "defaultQuery": "SELECT category, SUM(total) FROM orders GROUP BY category",
        "solution": "SELECT category, SUM(total) FROM orders GROUP BY category",
        "check_func": lambda df: len(df) == 3 and ((df['category'] == 'Electronics') & (df.iloc[:, 1] == 1650)).any()
    },
    {
        "id": 7,
        "category": "07. Having",
        "title": "HAVING Clause",
        "description": "The HAVING clause was added to SQL because the WHERE keyword could not be used with aggregate functions.",
        "concept": "WHERE filters rows BEFORE grouping. HAVING filters groups AFTER grouping.",
        "task": "Find product categories with total sales greater than 1000.",
        "hint": "SELECT category, SUM(total) FROM orders GROUP BY category HAVING SUM(total) > 1000",
        "defaultQuery": "SELECT category, SUM(total) FROM orders GROUP BY category HAVING SUM(total) > 1000",
        "solution": "SELECT category, SUM(total) FROM orders GROUP BY category HAVING SUM(total) > 1000",
        "check_func": lambda df: len(df) == 1 and df.iloc[0]['category'] == 'Electronics'
    }
]

# --- STATE MANAGEMENT ---
if 'active_lesson_idx' not in st.session_state:
    st.session_state.active_lesson_idx = 0

if 'query_text' not in st.session_state:
    st.session_state.query_text = LESSONS[0]['defaultQuery']

if 'last_run_success' not in st.session_state:
    st.session_state.last_run_success = False

current_lesson = LESSONS[st.session_state.active_lesson_idx]

# --- SIDEBAR ---
with st.sidebar:
    st.title("SQL MasterClass")
    st.markdown("---")
    
    # Progress
    progress = (st.session_state.active_lesson_idx) / len(LESSONS)
    st.progress(progress)
    st.caption(f"Lesson {st.session_state.active_lesson_idx + 1} of {len(LESSONS)}")
    
    st.markdown("### Curriculum")
    for idx, lesson in enumerate(LESSONS):
        is_active = idx == st.session_state.active_lesson_idx
        status_icon = "🔵" if is_active else "⚪"
        if st.button(f"{status_icon} {lesson['category']}", key=f"nav_{idx}", use_container_width=True):
            st.session_state.active_lesson_idx = idx
            st.session_state.query_text = lesson['defaultQuery']
            st.session_state.last_run_success = False
            st.rerun()

    st.markdown("---")
    if st.checkbox("Show Database Schema"):
        st.subheader("Database Schema")
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", st.session_state.db_conn)
        for table_name in tables['name']:
            st.markdown(f"**{table_name}**")
            schema = pd.read_sql(f"PRAGMA table_info({table_name})", st.session_state.db_conn)
            st.dataframe(schema[['name', 'type']], hide_index=True, use_container_width=True)

# --- MAIN CONTENT ---
st.header(current_lesson['title'])

# Concept Section
with st.expander("💡 Key Concept", expanded=True):
    st.info(current_lesson['concept'])
    st.markdown(current_lesson['description'])

# Task Section
st.markdown(f"### 🎯 Your Mission")
st.markdown(f"**{current_lesson['task']}**")
with st.expander("Need a hint?"):
    st.markdown(f"Try using: `{current_lesson['hint']}`")

# Editor Section
st.markdown("### ⌨️ SQL Editor")
query = st.text_area("Write your query here:", value=st.session_state.query_text, height=150, key="editor")

col1, col2 = st.columns([1, 5])
with col1:
    run_clicked = st.button("▶ Run Query", type="primary")
with col2:
    if st.button("Show Solution"):
        st.session_state.query_text = current_lesson['solution']
        st.rerun()

# Execution Logic
if run_clicked:
    st.session_state.query_text = query # Update state with current editor content
    try:
        # Run query
        result_df = pd.read_sql_query(query, st.session_state.db_conn)
        
        # Display results
        st.markdown("### 📊 Results")
        st.dataframe(result_df, use_container_width=True)
        
        # Check correctness
        try:
            if current_lesson['check_func'](result_df):
                st.success("🎉 Correct! Great job.")
                st.session_state.last_run_success = True
                st.balloons()
            else:
                st.warning("The query ran successfully, but the result isn't quite what we're looking for. Try again!")
                st.session_state.last_run_success = False
        except Exception as e:
             st.warning(f"The query ran, but we couldn't verify the result: {e}")

    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.session_state.last_run_success = False

# Navigation Footer
st.markdown("---")
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.session_state.active_lesson_idx > 0:
        if st.button("← Previous Lesson"):
            st.session_state.active_lesson_idx -= 1
            st.session_state.query_text = LESSONS[st.session_state.active_lesson_idx]['defaultQuery']
            st.session_state.last_run_success = False
            st.rerun()

with col_next:
    if st.session_state.active_lesson_idx < len(LESSONS) - 1:
        # Enable next button if success or if user wants to skip (optional, here we allow skip)
        if st.button("Next Lesson →", type="primary" if st.session_state.last_run_success else "secondary"):
            st.session_state.active_lesson_idx += 1
            st.session_state.query_text = LESSONS[st.session_state.active_lesson_idx]['defaultQuery']
            st.session_state.last_run_success = False
            st.rerun()
