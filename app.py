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
import uuid
from docx2pdf import convert
import pdfplumber

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

def generate_rubric(table_text, weightage):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""You are helping a student identify the marking rubric from an assignment specification.

The following is plain text extracted from the grading criteria section of an assignment specification. The text spans multiple pages of a table. Here is how to interpret it:

- The table has these columns: Criteria | In Context | A (>=80%) | B (>=70%) | C (>=60%) | D (>=50%) | F (<50%)
- A top-level criteria has its own marks allocation e.g. "Flowchart Design (16%)"
- Sub-criteria appear under a top-level criteria e.g. "Logic (10%)", "Flow Chart Conventions (3%)", "Constraints (3%)" are all under "Flowchart Design (16%)"
- The performance level descriptions (A/B/C/D/F) that follow a criteria name belong to that criteria
- The total marks of ALL top-level criteria must sum to exactly {weightage}%

Extract ONLY the top-level criteria. For each top-level criteria, collect ALL the sub-criteria and their performance levels. 
Important: The "criteria" field must NOT include the marks percentage in brackets. The marks belong only in the "marks" field.
Return a JSON array where each item has:
- "criteria": the full criteria name exactly as written, do not shorten or abbreviate it. Do not include the marks percentage in brackets.
- - "marks": the marks allocated exactly as written (e.g. "40%" or "4%")

Note: Some rubrics list criteria as a percentage of the assignment itself (e.g. 40% + 40% + 20% = 100%). Others list criteria as a percentage of the overall grade (e.g. 4% + 16% + 10% = 30%). Accept both formats — do not force criteria to sum to {weightage}%. Instead, just extract whatever criteria and marks are explicitly stated in the document.
- "in_context": all sub-criteria and context exactly as written
- "performance_levels": array of objects with "grade" and "description" exactly as written. If a top-level criteria has multiple sub-criteria, combine all their performance level descriptions together under the same grade.

Return only a JSON array, no intro text, no markdown backticks.

Grading criteria text:
{table_text}

Generate the rubric:"""
            }
        ]
    )
    
    return response.choices[0].message.content

def extract_tables(filepath):
    result = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    cleaned = [cell if cell else "" for cell in row]
                    result += " | ".join(cleaned) + "\n"
                result += "\n"
    return result

def extract_rubric_text(filepath):
    doc = fitz.open(filepath)
    rubric_text = ""
    start_page = None
    for page in doc:
        text = page.get_text()
        if any(keyword in text for keyword in ["Grading Criteria", "Marking Criteria", "Assessment Criteria", "Rubric", "Criteria", "grading criteria", "marking criteria", "criteria"]):
            start_page = page.number
            break
    
    if start_page is not None:
        for i in range(start_page, len(doc)):
            rubric_text += doc[i].get_text()
    
    return rubric_text

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
            "progress": round(counts[0] * 100) if counts != 0 else 0,
            "spec_file": project[4],
            "rubric": json.loads(project[5]) if project[5] else []
        })
    return render_template("index.html", projects=project_data)

@app.route("/add_project", methods=["POST"])
def add_project():
    assignment_name = request.form["assignment_name"]
    weightage = request.form["weightage"]
    due_date = request.form["due_date"]
    pdf = request.files["pdf"]

    due_date_obj = date.fromisoformat(due_date)
    if due_date_obj < date.today():
        return {"error": "Due date cannot be in the past."}, 400

    filename = f"{uuid.uuid4()}_{pdf.filename}"
    upload_folder = os.path.join('static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    pdf.save(filepath)

    pdf.stream.seek(0)
    text = extract_text(pdf)

    if text is None:
        return {"error": "Unsupported file type. Please upload a PDF or DOCX."}, 400

    if filename.endswith('.docx'):
        pdf_filepath = filepath.replace('.docx', '.pdf')
        convert(filepath, pdf_filepath)
        filepath = pdf_filepath
        os.remove(filepath.replace('.pdf', '.docx'))

    tasks_text = generate_tasks(text)
    tasks_json = json.loads(tasks_text)

    if len(tasks_json) == 0:
        return {"error": "Document does not appear to be an assignment specification."}, 400

    table_text = extract_rubric_text(filepath)
    rubric_raw = generate_rubric(table_text, weightage)
    print(rubric_raw)
    rubric_json = json.dumps(json.loads(rubric_raw))

    project_id = database.add_project(assignment_name, weightage, due_date, filepath, rubric_json)

    for task in tasks_json:
        database.add_task(project_id, task["title"], task["instructions"], 0)

    return {"redirect": f"/project/{project_id}"}, 200

@app.route("/update_task/<int:task_id>", methods=["POST"])
def update_task_instructions(task_id):

    entry = request.json["instructions"]
    database.update_task_instructions(entry, task_id)

    return {"success": True}, 200

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
            "progress": round(counts[0] * 100) if counts != 0 else 0,
            "spec_file": p[4],
            "rubric": json.loads(p[5]) if p[5] else []
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