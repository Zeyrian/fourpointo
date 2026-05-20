import sqlite3
connection = sqlite3.connect('fourpointo.db')

cursor = connection.cursor()

def add_project(assignment_name, weightage, due_date, filepath, rubric):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO projects 
                   (assignment_name, weightage, due_date, spec, rubric) VALUES (?, ?, ?, ?, ?)""",
                   (assignment_name, weightage, due_date, filepath, rubric)
                   )
    
    connection.commit()
    connection.close()
    return cursor.lastrowid

def delete_project(project_id):
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
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

def get_projects():
    connection = sqlite3.connect('fourpointo.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()

    connection.close()

    return projects

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

cursor.execute("""CREATE TABLE IF NOT EXISTS projects (
                   id integer primary key autoincrement,
                   assignment_name text,
                   weightage integer,
                   due_date text,
                   spec text,
                   rubric text
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

print("Command executed successfully")

connection.commit()

connection.close()