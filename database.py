import sqlite3
from flask_bcrypt import generate_password_hash
connection = sqlite3.connect('fourpointo.db')

cursor = connection.cursor()

def add_project(assignment_name, weightage, due_date, filepath, rubric, user_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO projects 
                   (assignment_name, weightage, due_date, spec, rubric, user_id) VALUES (?, ?, ?, ?, ?, ?)""",
                   (assignment_name, weightage, due_date, filepath, rubric, user_id)
                   )
    
    connection.commit()
    connection.close()
    return cursor.lastrowid

def delete_project(project_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))

    connection.commit()
    connection.close()
    
def add_task(project_id, title, instructions, completed):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO tasks 
                   (project_id, title, instructions, completed) VALUES (?, ?, ?, ?)""",
                   (project_id, title, instructions, completed))
    connection.commit()
    connection.close()

def get_projects(user_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM projects WHERE user_id = ?", (user_id,))
    projects = cursor.fetchall()

    connection.close()

    return projects

def get_project(project_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    connection.close()
    return project

def get_tasks(project_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE project_id = ?", (project_id,))

    tasks = cursor.fetchall()

    connection.close()
    return tasks

def complete_task(task_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))

    connection.commit()
    connection.close()

def uncomplete_task(task_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))

    connection.commit()
    connection.close()    

def get_task_counts(project_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    tasks = get_tasks(project_id)
    if len(tasks) == 0:
        return 0
    
    total_task_count = len(tasks)
    completed_count = 0

    for _, _, _, _, completed in tasks:
        if completed == 1:
            completed_count += 1

    progress = completed_count / total_task_count

    connection.close()
    return [progress, total_task_count, completed_count]

def update_task_instructions(entry, task_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()

    cursor.execute("UPDATE tasks SET instructions = ? WHERE id = ?", (entry, task_id,))

    connection.commit()
    connection.close()

def add_user(email, username, password, premium_user):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    emails = cursor.fetchall()

    if len(emails) > 0:
        return "Email already exists"
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    users = cursor.fetchall()

    if len(users) > 0:
        return "Username already exists"
    
    hashed_password = generate_password_hash(password).decode('utf-8')
    
    cursor.execute("""INSERT INTO users
                   (username, email, password, premium_user) VALUES (?, ?, ?, ?)
                   """, (username, email, hashed_password, premium_user))
    
    connection.commit()
    connection.close()
    return cursor.lastrowid

def get_user(email):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users where email = ?", (email,))

    user = cursor.fetchone()

    connection.close()
    return user

def get_user_by_id(id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users where id = ?", (id,))

    user = cursor.fetchone()

    connection.close()
    return user

def get_user_by_username(username):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users where username = ?", (username,))

    user = cursor.fetchone()

    connection.close()
    return user

cursor.execute("""CREATE TABLE IF NOT EXISTS projects (
                   id integer primary key autoincrement,
                   assignment_name text,
                   weightage integer,
                   due_date text,
                   spec text,
                   rubric text,
                   user_id integer
                   )

""")

cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tasks (
                   id integer primary key autoincrement,
                   project_id integer,
                   title text,
                   instructions text,
                   completed integer
                   )


""")

cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                    id integer primary key autoincrement,
                    username text,
                    email text,
                    password text,
                    premium_user integer
               )
""")

print("Command executed successfully")

connection.commit()

connection.close()