# School Management System — Tkinter & PyQt GUIs

This repo contains two desktop interfaces for a small School Management System, built on the **same SQLite database** and **shared DB utilities**:

- **Tkinter app** (lightweight, stdlib only) — `tkinter_main.py`
- **PyQt app** (feature-rich, polished UI) — `pyqt_main.py`

Both apps operate on `school.db` using helper functions in `db.py` (schema, CRUD, search, backups).

---

## 1) Requirements

- **Python 3.8+**
- **SQLite** (bundled with Python via `sqlite3`)
- For PyQt interface: `PyQt5`

Install PyQt5 (if you plan to use the PyQt app):

```bash
pip install PyQt5
```

> The Tkinter app uses modules from the Python standard library and needs no extra packages.

---

## 2) Quick Start

Clone/download this project, then in a terminal from the project root:

### Run the Tkinter interface (no extra deps)
```bash
python tkinter_main.py
```

### Run the PyQt interface (after installing PyQt5)
```bash
python pyqt_main.py
```

On first run, both apps will **initialize** the SQLite DB (`school.db`) with the required tables if the file doesn't exist.

---

## 3) How the Data Layer Works (shared by both UIs)

- The DB layer lives in **`db.py`** — it defines the schema (students, instructors, courses, registrations) and exposes CRUD/search helpers that both UIs call.
- The SQLite file is **`school.db`** (in the project folder by default).
- There is also a **`models.py`** module with simple OOP models and JSON (de)serialization helpers; it's useful for non‑GUI scripting or future extensions but is **not** required for the GUIs.

> You can back up the database from either interface (see menus below).

---

## 4) Using the Tkinter App

**Launch:** `python tkinter_main.py`

**Tabs & Features**

1. **Students** — Add a student (ID, name, age, email).
2. **Instructors** — Add an instructor (ID, name, age, email).
3. **Courses** — Create a course (course ID, name) and link it to an instructor.
4. **Registration** — Register a student into a course.
5. **Assignment** — Assign an instructor to a course.
6. **Records** — Three tables (Students/Instructors/Courses) with **Scope**, **Search**, and **Refresh**.

**Menu** (top bar)
- **File → Backup DB…** — Save a copy of `school.db` anywhere you choose.
- **Tools → Refresh Records** — Refresh all tables/combos after changes.

**Notes**
- The Tkinter app focuses on **adding** and **listing** data quickly.
- Edits/deletes and CSV export are available in the PyQt app (see below).

---

## 5) Using the PyQt App

**Launch:** `python pyqt_main.py`

**Tabs & Features**

1. **Students** — Add a student with input validation.
2. **Instructors** — Add an instructor with validation.
3. **Courses** — Add a course and pick the instructor from a dropdown (kept in sync).
4. **Registration** — Register a student in a course.
5. **Assignment** — Assign an instructor to a course.
6. **Records** — Unified view with filters and **row selection** for:
   - **Edit Selected** — Edit the highlighted Student/Instructor/Course (dialog).
   - **Delete Selected** — Delete the highlighted record (with cascades where applicable).

**Menu** (top bar)
- **File → Backup DB…** — Back up `school.db` to a user-chosen path.
- **File → Export to CSV → Students / Instructors / Courses / All (3 files)** — Export the current DB entities to CSV files.
- **Tools → Refresh Records** — Refresh the aggregated tables.

**Quality-of-life**
- Inline **validators** for age, email, and ID formats.
- Status bar messages when data updates.
- Combos refresh automatically after inserts/edits.

---

## 6) Data Model (SQLite)

**Tables**
- `students(student_id TEXT PK, name TEXT, age INT>=0, email TEXT)`
- `instructors(instructor_id TEXT PK, name TEXT, age INT>=0, email TEXT)`
- `courses(course_id TEXT PK, course_name TEXT, instructor_id TEXT NULL, FK → instructors)`
- `registrations(student_id TEXT, course_id TEXT, PK(student_id, course_id), FKs → students, courses)`

**Foreign keys** are enforced and cascade on update (course/instructor IDs) and delete (registrations).

**Backups**
- Both apps expose **Backup DB…**. This copies `school.db` to your chosen location.

---

## 7) Common Workflows

- **Add people first** → Add **Instructors** and **Students**.
- **Create courses** and **link an instructor**.
- **Register students** into courses.
- Optionally **assign instructors** (or reassign) to courses later.
- Use **Records** to search/inspect the current state.
- In PyQt: **Edit/Delete** rows and **Export** CSV files for reports.

---

## 8) Troubleshooting

- **App won't start / ImportError: PyQt5** — Install `PyQt5` (`pip install PyQt5`) or run the Tkinter app which needs no extras.
- **Database errors / constraint failures** — Check unique IDs and email/age formats.
- **I don’t see new data in combos/tables** — Use **Refresh Records** (menu) or the provided buttons; PyQt auto-updates most views after actions.
- **Reset DB** — Delete `school.db` (or rename it) and relaunch; the schema will be recreated automatically. (You can always back up first.)

---

## 9) Dev Notes

- Both GUIs call the same DB API from `db.py`. Keeping all data rules in one place avoids duplication.
- `models.py` provides simple classes and JSON (de)serialization that can be used for tests, CLI tools, or future REST endpoints.
- Feel free to swap `DB.DEFAULT_DB` to point to a different SQLite file for testing.

---

## 10) License

Educational use for **Software Tools Lab – Fall 2025–2026**. Add your preferred license if needed.
