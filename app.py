from flask import Flask, render_template, request
import fitz
from groq import Groq
import database
from flask import redirect
import json
from datetime import date
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

def extract_text(file):
    filename = file.filename
    if filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif filename.endswith('.docx'):
        import docx
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        return None

def generate_tasks(pdf_text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""You are helping a student break down an assignment specification into clear, actionable tasks.

Read the following assignment specification. If it is not an assignment specification, return []. Else, generate a numbered list of specific tasks the student needs to complete.
Be concrete and specific. Each task should be a single actionable item. Return only a JSON array, no intro text, each item has a title (short, 3-5 words) and instructions (full detail)

Assignment specification:
{pdf_text}

Generate the task list:"""
            }
        ]
    )
    
    return response.choices[0].message.content

@app.route("/")
def index():
    projects = database.get_projects()
    project_data = []
    for project in projects:
        counts = database.get_task_counts(project[0])

        due_date_formatted = datetime.strptime(project[3], "%Y-%m-%d").strftime("%d %B %Y")
        project_data.append({
            "id": project[0],
            "name": project[1],
            "weightage": project[2],
            "due_date": due_date_formatted,
            "progress": round(counts[0] * 100) if counts != 0 else 0
        })
    return render_template("index.html", projects=project_data)

@app.route("/add_project", methods=["POST"])
def add_project():
    assignment_name = request.form["assignment_name"]
    weightage = request.form["weightage"]
    due_date = request.form["due_date"]
    pdf = request.files["pdf"]
    
    project_id = database.add_project(assignment_name, weightage, due_date)
    
    text = extract_text(pdf)
    if text is None:
        return "Unsupported file type", 400
    tasks_text = generate_tasks(text)

    print(tasks_text)
    
    tasks_json = json.loads(tasks_text)
    if len(tasks_json) == 0:
        database.delete_project(project_id)
        return "Document does not appear to be an assignment specification", 400
    
    for task in tasks_json:
        database.add_task(project_id, task["title"], task["instructions"], 0)

    due_date_obj = date.fromisoformat(due_date)
    if due_date_obj < date.today():
        return "Invalid date", 400
    
    return redirect(f"/project/{project_id}")

@app.route("/project/<int:project_id>")
def project(project_id):
    projects = database.get_projects()
    project_data = []
    for p in projects:
        counts = database.get_task_counts(p[0])

        due_date_formatted = datetime.strptime(p[3], "%Y-%m-%d").strftime("%d %B %Y")
        project_data.append({
            "id": p[0],
            "name": p[1],
            "weightage": p[2],
            "due_date": due_date_formatted,
            "progress": round(counts[0] * 100) if counts != 0 else 0
        })
    
    tasks = database.get_tasks(project_id)
    current_project = next((p for p in project_data if p["id"] == project_id), None)
    counts = database.get_task_counts(project_id)
    outstanding = [t for t in tasks if t[4] == 0]
    completed = [t for t in tasks if t[4] == 1]
    
    return render_template("index.html", 
    projects=project_data, 
    outstanding=outstanding, 
    completed=completed, 
    active_project=project_id,
    current_project=current_project,
    counts=counts)

@app.route("/complete_task/<int:task_id>/<int:project_id>")
def complete_task(task_id, project_id):
    database.complete_task(task_id)
    return redirect(f"/project/{project_id}")

@app.route("/uncomplete_task/<int:task_id>/<int:project_id>")
def uncomplete_task(task_id, project_id):
    database.uncomplete_task(task_id)
    return redirect(f"/project/{project_id}")

@app.route("/delete_project/<int:project_id>")
def delete_project(project_id):
    database.delete_project(project_id)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)