import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- SQLite Connection ---
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    amount REAL NOT NULL
)
""")
conn.commit()

# --- Streamlit App ---
st.title("💰 Personal Expense Tracker (SQLite)")

menu = ["Add Expense", "View Expenses", "Delete Expense", "Category Report"]
choice = st.sidebar.selectbox("Menu", menu)

# --- Add Expense ---
if choice == "Add Expense":
    st.subheader("Add a New Expense")
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["Food", "Travel", "Entertainment", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0)

    if st.button("Add Expense"):
        cursor.execute(
            "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
            (str(date), category, description, amount)
        )
        conn.commit()
        st.success(f"Added {amount} to {category}!")

# --- View Expenses ---
elif choice == "View Expenses":
    st.subheader("All Expenses")
    df = pd.read_sql("SELECT * FROM expenses", conn)
    st.dataframe(df)

    # Export CSV
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "expenses.csv", "text/csv")

# --- Delete Expense ---
elif choice == "Delete Expense":
    st.subheader("Delete Expense by ID")
    expense_id = st.number_input("Expense ID", min_value=1, step=1)

    if st.button("Delete"):
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        st.success(f"Deleted expense with ID {expense_id}")

# --- Category-wise Report ---
elif choice == "Category Report":
    st.subheader("Category-wise Spending")
    df = pd.read_sql("SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)

    if not df.empty:
        st.dataframe(df)
        fig, ax = plt.subplots()
        ax.pie(df["total"], labels=df["category"], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No data available!")

