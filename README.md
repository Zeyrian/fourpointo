# 4point0 Updates Board

---

## 🛠️ Dev Log — 17 May 2026

- Added backend + frontend validation to reject due dates before today
- Handled invalid documents: AI returns `[]` if the file isn't an assignment spec, project is deleted and user gets an error
- Added delete project button — three dots appear on hover, opens confirmation modal with blur background
- Dots menu auto-closes when mouse leaves the project item
- Added due date and weightage to the project view header
- Due date formatted from `YYYY-MM-DD` to readable English (e.g. 19 May 2026)
- Tasks Completed displayed as `X / Y` instead of two separate lines
- Moved Groq API key to `.env` file for security

---

## 🛠️ Dev Log — 16 May 2026

- Built task completion with checkbox, undo button with red hover overlay, and live progress %
- Added task detail popup — click any task to see full instructions in a modal
- Added docx support alongside PDF using python-docx
- UX polish: loading state on form submit, form validation, blur modal background, sidebar card redesign, delete project with confirmation modal

---

## 🛠️ Dev Log — 15 May 2026

- Identified a gap: no project management app built specifically for poly students
- Designed the first wireframe for the layout
- Named the app **4point0** — the highest GPA you can get, and something we actually say
- Built the base HTML/CSS layout
- Discovered Groq API (free, no age restriction) and integrated Llama for AI task generation
- Got the first working task generation from a PDF in the terminal
- Migrated to Flask so the app runs in a browser with file upload
- Set up SQLite database with `projects` and `tasks` tables, and all CRUD functions
- Design cleanups and layout polish
