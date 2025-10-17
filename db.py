import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional
import shutil
import os

DEFAULT_DB = "school.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    student_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    age          INTEGER NOT NULL CHECK(age >= 0),
    email        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instructors (
    instructor_id TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    age           INTEGER NOT NULL CHECK(age >= 0),
    email         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_id     TEXT PRIMARY KEY,
    course_name   TEXT NOT NULL,
    instructor_id TEXT,
    FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- Many-to-many: students <-> courses
CREATE TABLE IF NOT EXISTS registrations (
    student_id TEXT NOT NULL,
    course_id  TEXT NOT NULL,
    PRIMARY KEY(student_id, course_id),
    FOREIGN KEY(student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(course_id)  REFERENCES courses(course_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
"""

@contextmanager
def connect(db_path: str = DEFAULT_DB):
    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA foreign_keys = ON;")
        yield con
        con.commit()
    finally:
        con.close()

def init_db(db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.executescript(SCHEMA_SQL)
def add_student(student_id: str, name: str, age: int, email: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("INSERT INTO students(student_id, name, age, email) VALUES (?, ?, ?, ?)",
                    (student_id, name, age, email))

def list_students(db_path: str = DEFAULT_DB) -> List[Dict]:
    with connect(db_path) as con:
        rows = con.execute("SELECT student_id, name, age, email FROM students ORDER BY student_id").fetchall()
    return [dict(student_id=r[0], name=r[1], age=r[2], email=r[3]) for r in rows]

def get_student(student_id: str, db_path: str = DEFAULT_DB) -> Optional[Dict]:
    with connect(db_path) as con:
        r = con.execute("SELECT student_id, name, age, email FROM students WHERE student_id=?",
                        (student_id,)).fetchone()
    return None if not r else dict(student_id=r[0], name=r[1], age=r[2], email=r[3])

def update_student(student_id: str, *, new_id: Optional[str]=None, name: Optional[str]=None,
                   age: Optional[int]=None, email: Optional[str]=None, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        
        if new_id and new_id != student_id:
            con.execute("UPDATE students SET student_id=? WHERE student_id=?", (new_id, student_id))
            student_id = new_id
        if any(v is not None for v in (name, age, email)):
            sets, vals = [], []
            if name is not None: sets.append("name=?"); vals.append(name)
            if age is not None: sets.append("age=?"); vals.append(age)
            if email is not None: sets.append("email=?"); vals.append(email)
            vals.append(student_id)
            con.execute(f"UPDATE students SET {', '.join(sets)} WHERE student_id=?", vals)

def delete_student(student_id: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("DELETE FROM students WHERE student_id=?", (student_id,))


def add_instructor(instructor_id: str, name: str, age: int, email: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("INSERT INTO instructors(instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
                    (instructor_id, name, age, email))

def list_instructors(db_path: str = DEFAULT_DB) -> List[Dict]:
    with connect(db_path) as con:
        rows = con.execute("SELECT instructor_id, name, age, email FROM instructors ORDER BY instructor_id").fetchall()
    return [dict(instructor_id=r[0], name=r[1], age=r[2], email=r[3]) for r in rows]

def get_instructor(instructor_id: str, db_path: str = DEFAULT_DB) -> Optional[Dict]:
    with connect(db_path) as con:
        r = con.execute("SELECT instructor_id, name, age, email FROM instructors WHERE instructor_id=?",
                        (instructor_id,)).fetchone()
    return None if not r else dict(instructor_id=r[0], name=r[1], age=r[2], email=r[3])

def update_instructor(instructor_id: str, *, new_id: Optional[str]=None, name: Optional[str]=None,
                      age: Optional[int]=None, email: Optional[str]=None, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        if new_id and new_id != instructor_id:
            con.execute("UPDATE instructors SET instructor_id=? WHERE instructor_id=?", (new_id, instructor_id))
            instructor_id = new_id
        if any(v is not None for v in (name, age, email)):
            sets, vals = [], []
            if name is not None: sets.append("name=?"); vals.append(name)
            if age is not None: sets.append("age=?"); vals.append(age)
            if email is not None: sets.append("email=?"); vals.append(email)
            vals.append(instructor_id)
            con.execute(f"UPDATE instructors SET {', '.join(sets)} WHERE instructor_id=?", vals)

def delete_instructor(instructor_id: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        
        con.execute("DELETE FROM instructors WHERE instructor_id=?", (instructor_id,))


def add_course(course_id: str, course_name: str, instructor_id: Optional[str], db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("INSERT INTO courses(course_id, course_name, instructor_id) VALUES (?, ?, ?)",
                    (course_id, course_name, instructor_id))

def list_courses(db_path: str = DEFAULT_DB) -> List[Dict]:
    with connect(db_path) as con:
        rows = con.execute("""
            SELECT c.course_id, c.course_name, c.instructor_id, i.name
            FROM courses c
            LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
            ORDER BY c.course_id
        """).fetchall()
    return [dict(course_id=r[0], course_name=r[1], instructor_id=r[2], instructor_name=(r[3] or "-")) for r in rows]

def get_course(course_id: str, db_path: str = DEFAULT_DB) -> Optional[Dict]:
    with connect(db_path) as con:
        r = con.execute("SELECT course_id, course_name, instructor_id FROM courses WHERE course_id=?",
                        (course_id,)).fetchone()
    return None if not r else dict(course_id=r[0], course_name=r[1], instructor_id=r[2])

def update_course(course_id: str, *, new_id: Optional[str]=None, course_name: Optional[str]=None,
                  instructor_id: Optional[str]=None, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        if new_id and new_id != course_id:
            con.execute("UPDATE courses SET course_id=? WHERE course_id=?", (new_id, course_id))
            course_id = new_id
        if any(v is not None for v in (course_name, instructor_id)):
            sets, vals = [], []
            if course_name is not None: sets.append("course_name=?"); vals.append(course_name)
            sets.append("instructor_id=?"); vals.append(instructor_id)  # can be None
            vals.append(course_id)
            con.execute(f"UPDATE courses SET {', '.join(sets)} WHERE course_id=?", vals)

def delete_course(course_id: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("DELETE FROM courses WHERE course_id=?", (course_id,))


def register_student(student_id: str, course_id: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES (?, ?)",
                    (student_id, course_id))

def list_registrations_for_student(student_id: str, db_path: str = DEFAULT_DB) -> List[Dict]:
    with connect(db_path) as con:
        rows = con.execute("""
            SELECT r.course_id, c.course_name
            FROM registrations r JOIN courses c ON c.course_id = r.course_id
            WHERE r.student_id=?
            ORDER BY r.course_id
        """, (student_id,)).fetchall()
    return [dict(course_id=r[0], course_name=r[1]) for r in rows]

def list_registrations_for_course(course_id: str, db_path: str = DEFAULT_DB) -> List[Dict]:
    with connect(db_path) as con:
        rows = con.execute("""
            SELECT r.student_id, s.name
            FROM registrations r JOIN students s ON s.student_id = r.student_id
            WHERE r.course_id=?
            ORDER BY r.student_id
        """, (course_id,)).fetchall()
    return [dict(student_id=r[0], name=r[1]) for r in rows]

def unregister_student(student_id: str, course_id: str, db_path: str = DEFAULT_DB):
    with connect(db_path) as con:
        con.execute("DELETE FROM registrations WHERE student_id=? AND course_id=?",
                    (student_id, course_id))


def search_students(q: str, db_path: str = DEFAULT_DB) -> List[Dict]:
    pat = f"%{q}%"
    with connect(db_path) as con:
        rows = con.execute("""
            SELECT student_id, name, age, email
            FROM students
            WHERE student_id LIKE ? OR name LIKE ? OR email LIKE ?
            ORDER BY student_id
        """, (pat, pat, pat)).fetchall()
    return [dict(student_id=r[0], name=r[1], age=r[2], email=r[3]) for r in rows]

def search_instructors(q: str, db_path: str = DEFAULT_DB) -> List[Dict]:
    pat = f"%{q}%"
    with connect(db_path) as con:
        rows = con.execute("""
            SELECT instructor_id, name, age, email
            FROM instructors
            WHERE instructor_id LIKE ? OR name LIKE ? OR email LIKE ?
            ORDER BY instructor_id
        """, (pat, pat, pat)).fetchall()
    return [dict(instructor_id=r[0], name=r[1], age=r[2], email=r[3]) for r in rows]

def search_courses(q: str, db_path: str = DEFAULT_DB) -> List[Dict]:
    pat = f"%{q}%"
    with connect(db_path) as con:
        rows = con.execute("""
            SELECT c.course_id, c.course_name, c.instructor_id, COALESCE(i.name, '-')
            FROM courses c LEFT JOIN instructors i ON i.instructor_id=c.instructor_id
            WHERE c.course_id LIKE ? OR c.course_name LIKE ? OR COALESCE(i.name,'') LIKE ?
            ORDER BY c.course_id
        """, (pat, pat, pat)).fetchall()
    return [dict(course_id=r[0], course_name=r[1], instructor_id=r[2], instructor_name=r[3]) for r in rows]


def backup_database(src_path: str = DEFAULT_DB, dest_path: str = "school_backup.db"):
    if not os.path.exists(src_path):
        init_db(src_path)
    shutil.copyfile(src_path, dest_path)
    return dest_path
