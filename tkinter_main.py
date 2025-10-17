


""" Tkinter GUI – School Management System
A small School Management GUI used in **Software Tools Lab – Fall 2025–2026**.
This module is documented with Sphinx/Napoleon-style docstrings.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, os
import db as DB

DB_PATH = DB.DEFAULT_DB
DB.init_db(DB_PATH)

def info(msg): messagebox.showinfo("Info", msg)
def error(msg): messagebox.showerror("Error", msg)

def center(win, w=1100, h=700):
    """Center the main window on screen."""
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw-w)//2, (sh-h)//2; win.geometry(f"{w}x{h}+{x}+{y}")

class App(tk.Tk):

    """App (Tkinter)

    Provides the UI and actions for the *App* section.

    Notes
    -----
    Discovered by Sphinx via ``autodoc``.
    """
    def __init__(self):
        """Initialize the main window and construct the primary UI.

    This constructor sets the window title, centers the window, creates the
    root :class:`ttk.Notebook`, adds all top-level tabs, then delegates each
    tab’s widgets to the corresponding ``build_*`` helper. Finally, it builds
    the application menubar.

    Tabs
    ----
    - **Students** (``self.students_tab``)
    - **Instructors** (``self.instructors_tab``)
    - **Courses** (``self.courses_tab``)
    - **Registration** (``self.registration_tab``)
    - **Assignment** (``self.assignment_tab``)
    - **Records** (``self.records_tab``)

    Attributes
    ----------
    students_tab, instructors_tab, courses_tab, registration_tab,
    assignment_tab, records_tab : ttk.Frame
        The six notebook pages added to the main notebook.

    Notes
    -----
    - Calls :func:`center` to position the window on screen.
    - Packs the :class:`ttk.Notebook` with ``fill="both"`` and ``expand=True``
      (with 10px padding).
    - Delegates UI construction to :meth:`build_students`, :meth:`build_instructors`,
      :meth:`build_courses`, :meth:`build_registration`, :meth:`build_assignment`,
      and :meth:`build_records`.
    - Calls :meth:`build_menubar` to create File/Tools menus.
    """

        super().__init__()
        self.title("School Management System"); center(self)
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.students_tab = ttk.Frame(nb); nb.add(self.students_tab, text="Students")
        self.instructors_tab = ttk.Frame(nb); nb.add(self.instructors_tab, text="Instructors")
        self.courses_tab = ttk.Frame(nb); nb.add(self.courses_tab, text="Courses")
        self.registration_tab = ttk.Frame(nb); nb.add(self.registration_tab, text="Registration")
        self.assignment_tab = ttk.Frame(nb); nb.add(self.assignment_tab, text="Assignment")
        self.records_tab = ttk.Frame(nb); nb.add(self.records_tab, text="Records")

        self.build_students()
        self.build_instructors()
        self.build_courses()
        self.build_registration()
        self.build_assignment()
        self.build_records()

        self.build_menubar()

    def build_menubar(self):
        """Build and attach the application menubar.

    Creates **File** (Backup DB…, Exit) and **Tools** (Refresh Records) menus,
    wires their commands, and assigns the menu to the window.

    Returns
    -------
    None
    """
        m = tk.Menu(self)
        file_m = tk.Menu(m, tearoff=0)
        file_m.add_command(label="Backup DB…", command=self.backup_db)
        file_m.add_separator(); file_m.add_command(label="Exit", command=self.destroy)
        m.add_cascade(label="File", menu=file_m)
        tools_m = tk.Menu(m, tearoff=0)
        tools_m.add_command(label="Refresh Records", command=self.refresh_all)
        m.add_cascade(label="Tools", menu=tools_m)
        self.config(menu=m)

    def backup_db(self):
        """Back up the current SQLite DB to a user-selected file.

    Opens a Save As dialog; if confirmed, copies the DB from ``DB_PATH`` via
    ``DB.backup_database`` and shows a success message. On failure, displays
    an error dialog.

    Returns
    -------
    None
    """

        path = filedialog.asksaveasfilename(title="Backup DB", defaultextension=".db",
                                            filetypes=[("SQLite DB", "*.db"), ("All Files","*.*")])
        if not path: return
        try:
            DB.backup_database(DB_PATH, path)
            info(f"Database backed up to:\n{path}")
        except Exception as e:
            error(str(e))

    def build_students(self):
        """Construct the Students tab (form + table + action buttons)."""
        f = ttk.Frame(self.students_tab); f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Name").grid(row=0,column=0,sticky="e"); self.s_name=ttk.Entry(f,width=28); self.s_name.grid(row=0,column=1)
        ttk.Label(f, text="Age").grid(row=1,column=0,sticky="e"); self.s_age=ttk.Entry(f,width=28); self.s_age.grid(row=1,column=1)
        ttk.Label(f, text="Email").grid(row=2,column=0,sticky="e"); self.s_email=ttk.Entry(f,width=28); self.s_email.grid(row=2,column=1)
        ttk.Label(f, text="Student ID").grid(row=3,column=0,sticky="e"); self.s_id=ttk.Entry(f,width=28); self.s_id.grid(row=3,column=1)
        ttk.Button(f, text="Add Student", command=self.add_student).grid(row=4,column=0,columnspan=2,pady=6)

    def add_student(self):
        """Validate inputs and create a new student via the DB API.

    Raises
    ------
    Exception
        Propagated as a messagebox error if the DB insert fails.
    """
        try:
            DB.add_student(self.s_id.get().strip(), self.s_name.get().strip(),
                           int(self.s_age.get().strip()), self.s_email.get().strip(), DB_PATH)
            info("Student added."); self.s_name.delete(0,tk.END); self.s_age.delete(0,tk.END)
            self.s_email.delete(0,tk.END); self.s_id.delete(0,tk.END); self.refresh_all()
        except Exception as e: error(str(e))


    def build_instructors(self):
        """Construct the Instructors tab UI."""
        f = ttk.Frame(self.instructors_tab); f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Name").grid(row=0,column=0,sticky="e"); self.i_name=ttk.Entry(f,width=28); self.i_name.grid(row=0,column=1)
        ttk.Label(f, text="Age").grid(row=1,column=0,sticky="e"); self.i_age=ttk.Entry(f,width=28); self.i_age.grid(row=1,column=1)
        ttk.Label(f, text="Email").grid(row=2,column=0,sticky="e"); self.i_email=ttk.Entry(f,width=28); self.i_email.grid(row=2,column=1)
        ttk.Label(f, text="Instructor ID").grid(row=3,column=0,sticky="e"); self.i_id=ttk.Entry(f,width=28); self.i_id.grid(row=3,column=1)
        ttk.Button(f, text="Add Instructor", command=self.add_instructor).grid(row=4,column=0,columnspan=2,pady=6)

    def add_instructor(self):
        """Create a new instructor using form entries."""
        try:
            DB.add_instructor(self.i_id.get().strip(), self.i_name.get().strip(),
                              int(self.i_age.get().strip()), self.i_email.get().strip(), DB_PATH)
            info("Instructor added."); self.i_name.delete(0,tk.END); self.i_age.delete(0,tk.END)
            self.i_email.delete(0,tk.END); self.i_id.delete(0,tk.END); self.refresh_all()
        except Exception as e: error(str(e))


    def build_courses(self):
        """Construct the Courses tab UI (ID, name, instructor selector)."""
        f = ttk.Frame(self.courses_tab); f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Course ID").grid(row=0,column=0,sticky="e"); self.c_id=ttk.Entry(f,width=28); self.c_id.grid(row=0,column=1)
        ttk.Label(f, text="Course Name").grid(row=1,column=0,sticky="e"); self.c_name=ttk.Entry(f,width=28); self.c_name.grid(row=1,column=1)
        ttk.Label(f, text="Instructor").grid(row=2,column=0,sticky="e"); self.c_ins=ttk.Combobox(f,width=26,state="readonly"); self.c_ins.grid(row=2,column=1)
        ttk.Button(f, text="Add Course", command=self.add_course).grid(row=3,column=0,columnspan=2,pady=6)
        self.refresh_instructor_combo(self.c_ins)

    def refresh_instructor_combo(self, combo):
        """Reload the instructor Combobox with 'instructor_id - name' options.

    Parameters
    ----------
    combo : ttk.Combobox
        The Combobox to update.

    Returns
    -------
    None
    """

        combo["values"] = [f"{i['instructor_id']} - {i['name']}" for i in DB.list_instructors(DB_PATH)]

    def add_course(self):
        """Create a course and link it to the selected instructor."""
        try:
            iid = (self.c_ins.get().split(" - ")[0] if self.c_ins.get() else None)
            DB.add_course(self.c_id.get().strip(), self.c_name.get().strip(), iid, DB_PATH)
            info("Course added."); self.c_id.delete(0,tk.END); self.c_name.delete(0,tk.END); self.refresh_all()
        except Exception as e: error(str(e))


    def build_registration(self):
        """Construct the Registration tab (student ↦ course)."""
        f = ttk.Frame(self.registration_tab); f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Student").grid(row=0,column=0,sticky="e"); self.reg_s=ttk.Combobox(f,width=26,state="readonly"); self.reg_s.grid(row=0,column=1)
        ttk.Label(f, text="Course").grid(row=1,column=0,sticky="e"); self.reg_c=ttk.Combobox(f,width=26,state="readonly"); self.reg_c.grid(row=1,column=1)
        ttk.Button(f, text="Register", command=self.register_student).grid(row=2,column=0,columnspan=2,pady=6)
        self.refresh_student_combo(self.reg_s); self.refresh_course_combo(self.reg_c)

    def refresh_student_combo(self, combo):
        """Reload the student Combobox with 'student_id - name' options.

        Parameters
        ----------
        combo : ttk.Combobox
            The Combobox to update.

        Returns
        -------
        None
        """

        
        combo["values"] = [f"{s['student_id']} - {s['name']}" for s in DB.list_students(DB_PATH)]

    def refresh_course_combo(self, combo):
        """Reload the course Combobox with 'course_id - course_name' options.

        Parameters
        ----------
        combo : ttk.Combobox
            The Combobox to update.

        Returns
        -------
        None
        """
        combo["values"] = [f"{c['course_id']} - {c['course_name']}" for c in DB.list_courses(DB_PATH)]

    def register_student(self):
        """Persist a student-course registration via DB API."""
        try:
            sid = self.reg_s.get().split(" - ")[0]; cid = self.reg_c.get().split(" - ")[0]
            DB.register_student(sid, cid, DB_PATH); info("Registered."); self.refresh_all()
        except Exception as e: error(str(e))

    def build_assignment(self):
        """Construct the Assignment tab (instructor ↦ course)."""
        f = ttk.Frame(self.assignment_tab); f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Instructor").grid(row=0,column=0,sticky="e"); self.asg_i=ttk.Combobox(f,width=26,state="readonly"); self.asg_i.grid(row=0,column=1)
        ttk.Label(f, text="Course").grid(row=1,column=0,sticky="e"); self.asg_c=ttk.Combobox(f,width=26,state="readonly"); self.asg_c.grid(row=1,column=1)
        ttk.Button(f, text="Assign", command=self.assign_instructor).grid(row=2,column=0,columnspan=2,pady=6)
        self.refresh_instructor_combo(self.asg_i); self.refresh_course_combo(self.asg_c)

    def assign_instructor(self):
        """Assign an instructor to a course and save in DB."""
        try:
            iid = self.asg_i.get().split(" - ")[0]; cid = self.asg_c.get().split(" - ")[0]
            DB.update_course(cid, instructor_id=iid, db_path=DB_PATH); info("Assigned."); self.refresh_all()
        except Exception as e: error(str(e))


    def build_records(self):
        """Build the aggregated Records tab with search and tables."""
        top = ttk.Frame(self.records_tab); top.pack(fill="x", padx=6, pady=(8,2))
        ttk.Label(top, text="Scope:").pack(side="left")
        self.scope = ttk.Combobox(top, values=["All","Students","Instructors","Courses"], width=14, state="readonly")
        self.scope.current(0); self.scope.pack(side="left", padx=6)
        self.search = ttk.Entry(top, width=40); self.search.pack(side="left", padx=6)
        ttk.Button(top, text="Search", command=self.apply_search).pack(side="left")
        ttk.Button(top, text="Clear", command=self.clear_search).pack(side="left", padx=4)

        self.stu = self._table(self.records_tab, ["Student ID","Name","Age","Email","Registered Courses"])
        self.ins = self._table(self.records_tab, ["Instructor ID","Name","Age","Email","Assigned Courses"])
        self.cou = self._table(self.records_tab, ["Course ID","Course Name","Instructor","Enrolled Students"])


        act = ttk.Frame(self.records_tab); act.pack(fill="x", padx=6, pady=6)
        ttk.Button(act, text="Refresh", command=self.refresh_all).pack(side="left")

        self.refresh_all()

    def _table(self, parent, headers):
        """Create a scrollable Treeview with the given headers.

    Builds a frame, a Treeview configured with heading columns, and a vertical
    scrollbar; sets grid weights for resizing and returns the Treeview.

    Parameters
    ----------
    parent : tkinter widget
        Parent container for the table.
    headers : Sequence[str]
        Column headers.

    Returns
    -------
    ttk.Treeview
        The configured Treeview widget (its parent frame is already packed).
    """

        f = ttk.Frame(parent); f.pack(fill="both", expand=True, padx=6, pady=6)
        tree = ttk.Treeview(f, columns=list(range(len(headers))), show="headings", height=8)
        for i,h in enumerate(headers):
            tree.heading(i, text=h, anchor="w"); tree.column(i, width=140, anchor="w")
        vsb = ttk.Scrollbar(f, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0,column=0,sticky="nsew"); vsb.grid(row=0,column=1,sticky="ns")
        f.columnconfigure(0, weight=1); f.rowconfigure(0, weight=1)
        return tree

    def refresh_all(self):
        """Reload combos and tables across all tabs after data changes."""

        self.fill_students(""); self.fill_instructors(""); self.fill_courses("")
        self.refresh_instructor_combo(self.c_ins)
        self.refresh_student_combo(self.reg_s); self.refresh_course_combo(self.reg_c)
        self.refresh_instructor_combo(self.asg_i); self.refresh_course_combo(self.asg_c)

    def apply_search(self):
        """Apply the current query to tables based on selected scope.

    Reads the query from ``self.search`` and the scope from ``self.scope``,
    then repopulates Students, Instructors, and Courses—passing the query
    only to the chosen scope (or all when scope is "All").

    Returns
    -------
    None
    """

        q = self.search.get().strip(); scope = self.scope.get()
        self.fill_students(q if scope in ("All","Students") else "")
        self.fill_instructors(q if scope in ("All","Instructors") else "")
        self.fill_courses(q if scope in ("All","Courses") else "")

    def clear_search(self):
        """Clear the search UI and refresh all tables.

    Resets the query entry, sets scope to "All", and triggers a full refresh.

    Returns
    -------
    None
    """

        self.search.delete(0,tk.END); self.scope.current(0); self.refresh_all()

    def fill_students(self, q=""):
        """Populate the Students table.

        Clears rows, fetches students (all or search by ``q``), computes the
        registered courses string, and inserts rows into ``self.stu``.

        Parameters
        ----------
        q : str, optional
            Search filter; empty shows all.

        Returns
        -------
        None
        """
        for i in self.stu.get_children(): self.stu.delete(i)
        data = DB.search_students(q, DB_PATH) if q else DB.list_students(DB_PATH)
        for r in data:
            regs = DB.list_registrations_for_student(r["student_id"], DB_PATH)
            courses = ", ".join(x["course_name"] for x in regs) or "-"
            self.stu.insert("", "end", values=(r["student_id"], r["name"], r["age"], r["email"], courses))

    def fill_instructors(self, q=""):
        """Populate the Instructors table.

        Clears rows, fetches instructors (all or search by ``q``), derives the
        taught courses from ``DB.list_courses``, and inserts rows into ``self.ins``.

        Parameters
        ----------
        q : str, optional
            Search filter; empty shows all.

        Returns
        -------
        None
        """
        for i in self.ins.get_children(): self.ins.delete(i)
        data = DB.search_instructors(q, DB_PATH) if q else DB.list_instructors(DB_PATH)
        all_courses = DB.list_courses(DB_PATH)
        for r in data:
            taught = ", ".join(c["course_name"] for c in all_courses if c["instructor_id"] == r["instructor_id"]) or "-"
            self.ins.insert("", "end", values=(r["instructor_id"], r["name"], r["age"], r["email"], taught))

    def fill_courses(self, q=""):
        """Populate the Courses table.

        Clears rows, fetches courses (all or search by ``q``), derives enrolled
        student names, and inserts rows into ``self.cou``.

        Parameters
        ----------
        q : str, optional
            Search filter; empty shows all.

        Returns
        -------
        None
        """
        for i in self.cou.get_children(): self.cou.delete(i)
        data = DB.search_courses(q, DB_PATH) if q else DB.list_courses(DB_PATH)
        for r in data:
            studs = DB.list_registrations_for_course(r["course_id"], DB_PATH)
            s_names = ", ".join(s["name"] for s in studs) or "-"
            self.cou.insert("", "end", values=(r["course_id"], r["course_name"], r["instructor_name"], s_names))

if __name__ == "__main__":
    App().mainloop()
