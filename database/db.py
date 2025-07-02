# database/db.py

import sqlite3
from datetime import datetime

DB_NAME = "extracted_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create projects table
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_url TEXT,
            repo_path TEXT,
            created_at TEXT
        )
    ''')

    # Create features table
    c.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            feature TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    ''')

    # Create tech_stack table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tech_stack (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            stack_item TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_project(repo_url, repo_path):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute(
        "INSERT INTO projects (repo_url, repo_path, created_at) VALUES (?, ?, ?)",
        (repo_url, repo_path, datetime.now().isoformat())
    )

    project_id = c.lastrowid
    conn.commit()
    conn.close()
    return project_id

def insert_features(project_id, features):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for feature in features:
        c.execute("INSERT INTO features (project_id, feature) VALUES (?, ?)", (project_id, feature))
    conn.commit()
    conn.close()

def insert_tech_stack(project_id, stack_items):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for item in stack_items:
        c.execute("INSERT INTO tech_stack (project_id, stack_item) VALUES (?, ?)", (project_id, item))
    conn.commit()
    conn.close()
