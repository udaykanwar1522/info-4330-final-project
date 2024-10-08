import streamlit as st
import sqlite3
from hashlib import sha256
from datetime import date

# Function to create a database connection
def get_db_connection():
    conn = sqlite3.connect('todo_app.db')
    return conn, conn.cursor()

# Function to hash passwords
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Function to authenticate user
def authenticate_user(username, password):
    conn, c = get_db_connection()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

# Function to add user
def add_user(username, password):
    conn, c = get_db_connection()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
    conn.commit()
    conn.close()

# Function to add task
def add_task(username, task, priority, due_date):
    conn, c = get_db_connection()
    c.execute('INSERT INTO tasks (username, task, priority, due_date, completed) VALUES (?, ?, ?, ?, ?)', (username, task, priority, due_date, False))
    conn.commit()
    conn.close()

# Function to get tasks
def get_tasks(username):
    conn, c = get_db_connection()
    c.execute('SELECT * FROM tasks WHERE username = ?', (username,))
    tasks = c.fetchall()
    conn.close()
    return tasks

# Function to remove task
def remove_task(task_id):
    conn, c = get_db_connection()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# Function to toggle task completion
def toggle_task(task_id, completed):
    conn, c = get_db_connection()
    c.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
    conn.commit()
    conn.close()

# Initialize the database and create tables if they don't exist
def initialize_db():
    conn, c = get_db_connection()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            username TEXT,
            task TEXT,
            priority TEXT,
            due_date DATE,
            completed BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
initialize_db()

# Login/Register system
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""

if st.session_state['logged_in']:
    st.markdown(f"<h1 style='text-align: center; color: #FF5733;'>Welcome, {st.session_state['username']}</h1>", unsafe_allow_html=True)
    
    # To-Do List functionality
    task = st.text_input("Enter a new task:")
    priority = st.selectbox("Priority Level:", ["Low", "Medium", "High"])
    due_date = st.date_input("Due Date:", date.today())

    if st.button("Add Task"):
        add_task(st.session_state['username'], task, priority, due_date)
        st.experimental_rerun()

    tasks = get_tasks(st.session_state['username'])

    st.write("Your tasks:")
    for task in tasks:
        col1, col2, col3, col4, col5 = st.columns([0.1, 0.4, 0.2, 0.1, 0.2])
        with col1:
            st.checkbox("", value=task[5], key=f"check_{task[0]}", on_change=toggle_task, args=(task[0], not task[5]))
        with col2:
            if task[5]:
                st.markdown(f"~~{task[2]}~~")
            else:
                st.write(task[2])
        with col3:
            st.write(task[3])
        with col4:
            st.write(task[4])
        with col5:
            if st.button("Delete", key=f"delete_{task[0]}"):
                remove_task(task[0])
                st.experimental_rerun()

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.experimental_rerun()
else:
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>To-Do List with Login</h1>", unsafe_allow_html=True)

    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success(f"Welcome {username}")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    elif menu == "Register":
        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if new_password == confirm_password:
                try:
                    add_user(new_username, new_password)
                    st.success("User registered successfully")
                except sqlite3.IntegrityError:
                    st.error("Username already exists")
            else:
                st.error("Passwords do not match")
