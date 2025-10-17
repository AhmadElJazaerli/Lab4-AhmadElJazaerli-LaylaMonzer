import sys, csv, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTabWidget, QComboBox, QMessageBox, QLabel, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt5.QtCore import Qt, QRegularExpression, pyqtSignal

import db as DB

DB_PATH = DB.DEFAULT_DB
DB.init_db(DB_PATH)

EMAIL_RX = QRegularExpression(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
ID_RX    = QRegularExpression(r"^[A-Za-z0-9_\-]+$")

def info(parent, title, text): QMessageBox.information(parent, title, text)
def error(parent, title, text): QMessageBox.critical(parent, title, text)

def require_nonempty(parent, field, text):
    if not text.strip():
        error(parent, "Invalid Input", f"{field} cannot be empty.")
        return False
    return True

def require_regex(parent, field, text, rx, msg=None):
    if not rx.match(text).hasMatch():
        error(parent, "Invalid Input", msg or f"{field} is not valid.")
        return False
    return True

def require_int_in_range(parent, field, text, lo, hi):
    try:
        v = int(text)
    except Exception:
        error(parent, "Invalid Input", f"{field} must be an integer."); return None
    if v < lo or v > hi:
        error(parent, "Invalid Input", f"{field} must be between {lo} and {hi}."); return None
    return v

class StudentForm(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_e = QLineEdit()
        self.age_e = QLineEdit(); self.age_e.setValidator(QIntValidator(0, 150, self))
        self.email_e = QLineEdit(); self.email_e.setValidator(QRegularExpressionValidator(EMAIL_RX, self))
        self.sid_e = QLineEdit(); self.sid_e.setValidator(QRegularExpressionValidator(ID_RX, self))
        add_btn = QPushButton("Add Student"); add_btn.clicked.connect(self.on_add)

        form = QFormLayout()
        form.addRow("Name:", self.name_e)
        form.addRow("Age:", self.age_e)
        form.addRow("Email:", self.email_e)
        form.addRow("Student ID:", self.sid_e)

        v = QVBoxLayout(self)
        title = QLabel("Add Student"); title.setStyleSheet("font-size: 16px; font-weight: 600;")
        v.addWidget(title); v.addLayout(form); v.addWidget(add_btn, alignment=Qt.AlignLeft)

    def on_add(self):
        name = self.name_e.text().strip()
        age  = require_int_in_range(self, "Age", self.age_e.text().strip(), 0, 150)
        email = self.email_e.text().strip()
        sid   = self.sid_e.text().strip()
        if not (require_nonempty(self, "Name", name) and age is not None and
                require_regex(self, "Email", email, EMAIL_RX, "Please enter a valid email.") and
                require_nonempty(self, "Student ID", sid) and
                require_regex(self, "Student ID", sid, ID_RX, "Use letters, digits, _ or -.")):
            return
        try:
            DB.add_student(sid, name, age, email, DB_PATH)
            info(self, "Success", f"Student '{name}' added.")
            self.name_e.clear(); self.age_e.clear(); self.email_e.clear(); self.sid_e.clear()
            self.dataChanged.emit()
        except Exception as e:
            error(self, "Error", f"Failed to add student:\n{e}")

class InstructorForm(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.name_e = QLineEdit()
        self.age_e = QLineEdit(); self.age_e.setValidator(QIntValidator(0, 150, self))
        self.email_e = QLineEdit(); self.email_e.setValidator(QRegularExpressionValidator(EMAIL_RX, self))
        self.iid_e = QLineEdit(); self.iid_e.setValidator(QRegularExpressionValidator(ID_RX, self))
        add_btn = QPushButton("Add Instructor"); add_btn.clicked.connect(self.on_add)

        form = QFormLayout()
        form.addRow("Name:", self.name_e)
        form.addRow("Age:", self.age_e)
        form.addRow("Email:", self.email_e)
        form.addRow("Instructor ID:", self.iid_e)

        v = QVBoxLayout(self)
        title = QLabel("Add Instructor"); title.setStyleSheet("font-size: 16px; font-weight: 600;")
        v.addWidget(title); v.addLayout(form); v.addWidget(add_btn, alignment=Qt.AlignLeft)

    def on_add(self):
        name = self.name_e.text().strip()
        age  = require_int_in_range(self, "Age", self.age_e.text().strip(), 0, 150)
        email = self.email_e.text().strip()
        iid   = self.iid_e.text().strip()
        if not (require_nonempty(self, "Name", name) and age is not None and
                require_regex(self, "Email", email, EMAIL_RX, "Please enter a valid email.") and
                require_nonempty(self, "Instructor ID", iid) and
                require_regex(self, "Instructor ID", iid, ID_RX, "Use letters, digits, _ or -.")):
            return
        try:
            DB.add_instructor(iid, name, age, email, DB_PATH)
            info(self, "Success", f"Instructor '{name}' added.")
            self.name_e.clear(); self.age_e.clear(); self.email_e.clear(); self.iid_e.clear()
            self.dataChanged.emit()
        except Exception as e:
            error(self, "Error", f"Failed to add instructor:\n{e}")

class CourseForm(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cid_e = QLineEdit(); self.cid_e.setValidator(QRegularExpressionValidator(ID_RX, self))
        self.cname_e = QLineEdit()
        self.ins_combo = QComboBox(); self.ins_combo.setEditable(False)
        self.refresh_instructors()
        add_btn = QPushButton("Add Course"); add_btn.clicked.connect(self.on_add)

        form = QFormLayout()
        form.addRow("Course ID:", self.cid_e)
        form.addRow("Course Name:", self.cname_e)
        form.addRow("Instructor:", self.ins_combo)

        v = QVBoxLayout(self)
        title = QLabel("Add Course"); title.setStyleSheet("font-size: 16px; font-weight: 600;")
        v.addWidget(title); v.addLayout(form); v.addWidget(add_btn, alignment=Qt.AlignLeft)

    def refresh_instructors(self):
        self.ins_combo.clear()
        for ins in DB.list_instructors(DB_PATH):
            self.ins_combo.addItem(f"{ins['instructor_id']} - {ins['name']}")

    def selected_instructor_id(self) -> str:
        t = self.ins_combo.currentText()
        return t.split(" - ")[0].strip() if t else ""

    def on_add(self):
        cid = self.cid_e.text().strip()
        cname = self.cname_e.text().strip()
        iid = self.selected_instructor_id()
        if not (require_nonempty(self, "Course ID", cid) and
                require_regex(self, "Course ID", cid, ID_RX, "Use letters, digits, _ or -.") and
                require_nonempty(self, "Course Name", cname)):
            return
        if not iid:
            return error(self, "Invalid Input", "Please select an instructor.")
        try:
            DB.add_course(cid, cname, iid, DB_PATH)
            info(self, "Success", f"Course '{cname}' added.")
            self.cid_e.clear(); self.cname_e.clear()
            self.dataChanged.emit()
        except Exception as e:
            error(self, "Error", f"Failed to add course:\n{e}")

class RegistrationForm(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.student_combo = QComboBox(); self.student_combo.setEditable(False)
        self.course_combo  = QComboBox(); self.course_combo.setEditable(False)
        self.refresh_students(); self.refresh_courses()
        btn = QPushButton("Register"); btn.clicked.connect(self.on_register)

        form = QFormLayout()
        form.addRow("Student:", self.student_combo)
        form.addRow("Course:", self.course_combo)

        v = QVBoxLayout(self)
        title = QLabel("Register Student in Course"); title.setStyleSheet("font-size: 16px; font-weight: 600;")
        v.addWidget(title); v.addLayout(form); v.addWidget(btn, alignment=Qt.AlignLeft)

    def refresh_students(self):
        self.student_combo.clear()
        for s in DB.list_students(DB_PATH):
            self.student_combo.addItem(f"{s['student_id']} - {s['name']}")

    def refresh_courses(self):
        self.course_combo.clear()
        for c in DB.list_courses(DB_PATH):
            self.course_combo.addItem(f"{c['course_id']} - {c['course_name']}")

    def _ids(self):
        parse = lambda t: t.split(" - ")[0].strip() if t else ""
        return parse(self.student_combo.currentText()), parse(self.course_combo.currentText())

    def on_register(self):
        sid, cid = self._ids()
        if not sid or not cid:
            return error(self, "Invalid Input", "Select both a student and a course.")
        try:
            DB.register_student(sid, cid, DB_PATH)
            info(self, "Success", "Registration saved.")
            self.dataChanged.emit()
        except Exception as e:
            error(self, "Error", f"Registration failed:\n{e}")

class AssignmentForm(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ins_combo = QComboBox(); self.ins_combo.setEditable(False)
        self.course_combo = QComboBox(); self.course_combo.setEditable(False)
        self.refresh_instructors(); self.refresh_courses()
        btn = QPushButton("Assign"); btn.clicked.connect(self.on_assign)

        form = QFormLayout()
        form.addRow("Instructor:", self.ins_combo)
        form.addRow("Course:", self.course_combo)

        v = QVBoxLayout(self)
        title = QLabel("Assign Instructor to Course"); title.setStyleSheet("font-size: 16px; font-weight: 600;")
        v.addWidget(title); v.addLayout(form); v.addWidget(btn, alignment=Qt.AlignLeft)

    def refresh_instructors(self):
        self.ins_combo.clear()
        for ins in DB.list_instructors(DB_PATH):
            self.ins_combo.addItem(f"{ins['instructor_id']} - {ins['name']}")

    def refresh_courses(self):
        self.course_combo.clear()
        for c in DB.list_courses(DB_PATH):
            self.course_combo.addItem(f"{c['course_id']} - {c['course_name']}")

    def _ids(self):
        parse = lambda t: t.split(" - ")[0].strip() if t else ""
        return parse(self.ins_combo.currentText()), parse(self.course_combo.currentText())

    def on_assign(self):
        iid, cid = self._ids()
        if not iid or not cid:
            return error(self, "Invalid Input", "Select both an instructor and a course.")
        try:
            DB.update_course(cid, instructor_id=iid, db_path=DB_PATH)
            info(self, "Success", "Instructor assigned to course.")
            self.dataChanged.emit()
        except Exception as e:
            error(self, "Error", f"Assignment failed:\n{e}")
class StudentEditDialog(QDialog):
    def __init__(self, row: dict, parent=None):
        super().__init__(parent)
        self.orig_id = row["student_id"]
        self.setWindowTitle(f"Edit Student: {self.orig_id}")
        self.name_e = QLineEdit(row["name"])
        self.age_e  = QLineEdit(str(row["age"])); self.age_e.setValidator(QIntValidator(0,150,self))
        self.email_e= QLineEdit(row["email"]); self.email_e.setValidator(QRegularExpressionValidator(EMAIL_RX, self))
        self.sid_e  = QLineEdit(row["student_id"]); self.sid_e.setValidator(QRegularExpressionValidator(ID_RX, self))

        form = QFormLayout()
        form.addRow("Name:", self.name_e)
        form.addRow("Age:", self.age_e)
        form.addRow("Email:", self.email_e)
        form.addRow("Student ID:", self.sid_e)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

        v = QVBoxLayout(self); v.addLayout(form); v.addWidget(btns)

    def apply(self):
        name = self.name_e.text().strip()
        age = int(self.age_e.text().strip())
        email = self.email_e.text().strip()
        new_id = self.sid_e.text().strip()
        DB.update_student(self.orig_id, new_id=new_id, name=name, age=age, email=email, db_path=DB_PATH)

class InstructorEditDialog(QDialog):
    def __init__(self, row: dict, parent=None):
        super().__init__(parent)
        self.orig_id = row["instructor_id"]
        self.setWindowTitle(f"Edit Instructor: {self.orig_id}")
        self.name_e = QLineEdit(row["name"])
        self.age_e  = QLineEdit(str(row["age"])); self.age_e.setValidator(QIntValidator(0,150,self))
        self.email_e= QLineEdit(row["email"]); self.email_e.setValidator(QRegularExpressionValidator(EMAIL_RX, self))
        self.iid_e  = QLineEdit(row["instructor_id"]); self.iid_e.setValidator(QRegularExpressionValidator(ID_RX, self))

        form = QFormLayout()
        form.addRow("Name:", self.name_e)
        form.addRow("Age:", self.age_e)
        form.addRow("Email:", self.email_e)
        form.addRow("Instructor ID:", self.iid_e)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

        v = QVBoxLayout(self); v.addLayout(form); v.addWidget(btns)

    def apply(self):
        name = self.name_e.text().strip()
        age = int(self.age_e.text().strip())
        email = self.email_e.text().strip()
        new_id = self.iid_e.text().strip()
        DB.update_instructor(self.orig_id, new_id=new_id, name=name, age=age, email=email, db_path=DB_PATH)

class CourseEditDialog(QDialog):
    def __init__(self, row: dict, parent=None):
        super().__init__(parent)
        self.orig_id = row["course_id"]
        self.setWindowTitle(f"Edit Course: {self.orig_id}")
        self.cid_e = QLineEdit(row["course_id"]); self.cid_e.setValidator(QRegularExpressionValidator(ID_RX, self))
        self.cname_e = QLineEdit(row["course_name"])
        self.ins_combo = QComboBox()
        for ins in DB.list_instructors(DB_PATH):
            self.ins_combo.addItem(f"{ins['instructor_id']} - {ins['name']}")
        if row.get("instructor_id"):
            for i in range(self.ins_combo.count()):
                if self.ins_combo.itemText(i).startswith(row["instructor_id"] + " - "):
                    self.ins_combo.setCurrentIndex(i); break

        form = QFormLayout()
        form.addRow("Course ID:", self.cid_e)
        form.addRow("Course Name:", self.cname_e)
        form.addRow("Instructor:", self.ins_combo)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)

        v = QVBoxLayout(self); v.addLayout(form); v.addWidget(btns)

    def apply(self):
        new_id = self.cid_e.text().strip()
        name   = self.cname_e.text().strip()
        text   = self.ins_combo.currentText()
        iid    = text.split(" - ")[0].strip() if text else None
        DB.update_course(self.orig_id, new_id=new_id, course_name=name, instructor_id=iid, db_path=DB_PATH)
class RecordsTab(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scope_combo = QComboBox(); self.scope_combo.addItems(["All","Students","Instructors","Courses"])
        self.search_e = QLineEdit(); self.search_e.setPlaceholderText("Search by name, ID, or course…")
        s_btn = QPushButton("Search"); c_btn = QPushButton("Clear")
        s_btn.clicked.connect(self.apply_search); c_btn.clicked.connect(self.clear_search)
        self.search_e.returnPressed.connect(self.apply_search)
        top = QHBoxLayout()
        for w in (QLabel("Scope:"), self.scope_combo, self.search_e, s_btn, c_btn):
            top.addWidget(w)
        top.addStretch()
        self.stu = self._make_table(["Student ID","Name","Age","Email","Registered Courses"])
        self.ins = self._make_table(["Instructor ID","Name","Age","Email","Assigned Courses"])
        self.cou = self._make_table(["Course ID","Course Name","Instructor","Enrolled Students"])
        self.stu_edit, self.stu_del = QPushButton("Edit Selected"), QPushButton("Delete Selected")
        self.ins_edit, self.ins_del = QPushButton("Edit Selected"), QPushButton("Delete Selected")
        self.cou_edit, self.cou_del = QPushButton("Edit Selected"), QPushButton("Delete Selected")
        self.stu_edit.clicked.connect(self.edit_student); self.stu_del.clicked.connect(self.delete_student)
        self.ins_edit.clicked.connect(self.edit_instructor); self.ins_del.clicked.connect(self.delete_instructor)
        self.cou_edit.clicked.connect(self.edit_course); self.cou_del.clicked.connect(self.delete_course)
        layout = QVBoxLayout(self)
        title = QLabel("All Records"); title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title); layout.addLayout(top)

        layout.addWidget(QLabel("Students")); layout.addWidget(self.stu)
        b = QHBoxLayout(); b.addWidget(self.stu_edit); b.addWidget(self.stu_del); b.addStretch(); layout.addLayout(b)

        layout.addWidget(QLabel("Instructors")); layout.addWidget(self.ins)
        b = QHBoxLayout(); b.addWidget(self.ins_edit); b.addWidget(self.ins_del); b.addStretch(); layout.addLayout(b)

        layout.addWidget(QLabel("Courses")); layout.addWidget(self.cou)
        b = QHBoxLayout(); b.addWidget(self.cou_edit); b.addWidget(self.cou_del); b.addStretch(); layout.addLayout(b)

        self.refresh()

    def _make_table(self, headers):
        t = QTableWidget(0, len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setSelectionMode(QTableWidget.SingleSelection)
        t.verticalHeader().setVisible(False)
        return t

    def refresh(self):
        self._fill_students(); self._fill_instructors(); self._fill_courses()

    def _fill_students(self, q: str = ""):
        from db import list_registrations_for_student
        self.stu.setRowCount(0)
        data = DB.search_students(q, DB_PATH) if q else DB.list_students(DB_PATH)
        for row in data:
            regs = list_registrations_for_student(row["student_id"], DB_PATH)
            courses = ", ".join(r["course_name"] for r in regs) or "-"
            r = self.stu.rowCount(); self.stu.insertRow(r)
            self.stu.setItem(r,0,QTableWidgetItem(row["student_id"]))
            self.stu.setItem(r,1,QTableWidgetItem(row["name"]))
            self.stu.setItem(r,2,QTableWidgetItem(str(row["age"])))
            self.stu.setItem(r,3,QTableWidgetItem(row["email"]))
            self.stu.setItem(r,4,QTableWidgetItem(courses))

    def _fill_instructors(self, q: str = ""):
        self.ins.setRowCount(0)
        data = DB.search_instructors(q, DB_PATH) if q else DB.list_instructors(DB_PATH)
        all_courses = DB.list_courses(DB_PATH)
        for row in data:
            taught = [c for c in all_courses if c["instructor_id"] == row["instructor_id"]]
            courses = ", ".join(c["course_name"] for c in taught) or "-"
            r = self.ins.rowCount(); self.ins.insertRow(r)
            self.ins.setItem(r,0,QTableWidgetItem(row["instructor_id"]))
            self.ins.setItem(r,1,QTableWidgetItem(row["name"]))
            self.ins.setItem(r,2,QTableWidgetItem(str(row["age"])))
            self.ins.setItem(r,3,QTableWidgetItem(row["email"]))
            self.ins.setItem(r,4,QTableWidgetItem(courses))

    def _fill_courses(self, q: str = ""):
        self.cou.setRowCount(0)
        data = DB.search_courses(q, DB_PATH) if q else DB.list_courses(DB_PATH)
        for row in data:
            students = DB.list_registrations_for_course(row["course_id"], DB_PATH)
            s_names = ", ".join(s["name"] for s in students) or "-"
            r = self.cou.rowCount(); self.cou.insertRow(r)
            self.cou.setItem(r,0,QTableWidgetItem(row["course_id"]))
            self.cou.setItem(r,1,QTableWidgetItem(row["course_name"]))
            self.cou.setItem(r,2,QTableWidgetItem(row["instructor_name"]))
            self.cou.setItem(r,3,QTableWidgetItem(s_names))

    def apply_search(self):
        q = self.search_e.text().strip()
        scope = self.scope_combo.currentText()
        self._fill_students(q if scope in ("All","Students") else "")
        self._fill_instructors(q if scope in ("All","Instructors") else "")
        self._fill_courses(q if scope in ("All","Courses") else "")

    def clear_search(self):
        self.search_e.clear(); self.scope_combo.setCurrentIndex(0); self.refresh()

    def _selected_id(self, table, col=0):
        items = table.selectedItems()
        if not items: return ""
        return items[0].tableWidget().item(items[0].row(), col).text().strip()

    def edit_student(self):
        sid = self._selected_id(self.stu, 0)
        if not sid: return error(self, "Error", "Select a student to edit.")
        row = DB.get_student(sid, DB_PATH)
        if not row: return error(self, "Error", "Student not found.")
        dlg = StudentEditDialog(row, self)
        if dlg.exec_() == QDialog.Accepted:
            try: dlg.apply(); self.apply_search(); self.dataChanged.emit(); info(self,"Saved","Student updated.")
            except Exception as e: error(self,"Error",f"Failed to save: {e}")

    def delete_student(self):
        sid = self._selected_id(self.stu, 0)
        if not sid: return error(self, "Error", "Select a student to delete.")
        DB.delete_student(sid, DB_PATH)
        self.apply_search(); self.dataChanged.emit()
        info(self, "Deleted", f"Student '{sid}' deleted.")

    def edit_instructor(self):
        iid = self._selected_id(self.ins, 0)
        if not iid: return error(self, "Error", "Select an instructor to edit.")
        row = DB.get_instructor(iid, DB_PATH)
        if not row: return error(self, "Error", "Instructor not found.")
        dlg = InstructorEditDialog(row, self)
        if dlg.exec_() == QDialog.Accepted:
            try: dlg.apply(); self.apply_search(); self.dataChanged.emit(); info(self,"Saved","Instructor updated.")
            except Exception as e: error(self,"Error",f"Failed to save: {e}")

    def delete_instructor(self):
        iid = self._selected_id(self.ins, 0)
        if not iid: return error(self, "Error", "Select an instructor to delete.")
        DB.delete_instructor(iid, DB_PATH)
        self.apply_search(); self.dataChanged.emit()
        info(self, "Deleted", f"Instructor '{iid}' deleted.")

    def edit_course(self):
        cid = self._selected_id(self.cou, 0)
        if not cid: return error(self, "Error", "Select a course to edit.")
        row = DB.get_course(cid, DB_PATH)
        if not row: return error(self, "Error", "Course not found.")
        if row.get("instructor_id"):
            ins = DB.get_instructor(row["instructor_id"], DB_PATH)
            row["instructor_name"] = ins["name"] if ins else "-"
        dlg = CourseEditDialog(row, self)
        if dlg.exec_() == QDialog.Accepted:
            try: dlg.apply(); self.apply_search(); self.dataChanged.emit(); info(self,"Saved","Course updated.")
            except Exception as e: error(self,"Error",f"Failed to save: {e}")

    def delete_course(self):
        cid = self._selected_id(self.cou, 0)
        if not cid: return error(self, "Error", "Select a course to delete.")
        DB.delete_course(cid, DB_PATH)
        self.apply_search(); self.dataChanged.emit()
        info(self, "Deleted", f"Course '{cid}' deleted.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Management System")
        self.resize(1100, 740)

        tabs = QTabWidget()
        self.student_tab = StudentForm(self)
        self.instructor_tab = InstructorForm(self)
        self.course_tab = CourseForm(self)
        self.registration_tab = RegistrationForm(self)
        self.assignment_tab = AssignmentForm(self)
        self.records_tab = RecordsTab(self)

        for name, tab in [("Students", self.student_tab), ("Instructors", self.instructor_tab),
                          ("Courses", self.course_tab), ("Registration", self.registration_tab),
                          ("Assignment", self.assignment_tab), ("Records", self.records_tab)]:
            tabs.addTab(tab, name)

        for tab in (self.student_tab, self.instructor_tab, self.course_tab,
                    self.registration_tab, self.assignment_tab, self.records_tab):
            tab.dataChanged.connect(self.notify_data_changed)

        central = QWidget(); v = QVBoxLayout(central); v.addWidget(tabs); self.setCentralWidget(central)
        self._build_menus()
        self.statusBar().showMessage("Ready")

    def notify_data_changed(self):
        self.course_tab.refresh_instructors()
        self.registration_tab.refresh_students(); self.registration_tab.refresh_courses()
        self.assignment_tab.refresh_instructors(); self.assignment_tab.refresh_courses()
        self.records_tab.apply_search()
        self.statusBar().showMessage("Data updated", 3000)

    def _build_menus(self):
        mb = self.menuBar()
        file_m = mb.addMenu("&File")

        backup_act = file_m.addAction("Backup DB…")
        backup_act.triggered.connect(self._backup_db)

        export_m = file_m.addMenu("Export to CSV")
        export_m.addAction("Students…").triggered.connect(lambda: self._export_csv("students"))
        export_m.addAction("Instructors…").triggered.connect(lambda: self._export_csv("instructors"))
        export_m.addAction("Courses…").triggered.connect(lambda: self._export_csv("courses"))
        export_m.addAction("All (3 files)…").triggered.connect(lambda: self._export_csv("all"))

        file_m.addSeparator()
        file_m.addAction("Exit").triggered.connect(self.close)

        tools_m = mb.addMenu("&Tools")
        tools_m.addAction("Refresh Records").triggered.connect(self.records_tab.apply_search)

    def _backup_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite DB (*.db);;All Files (*)")
        if not path: return
        try:
            dest = DB.backup_database(DB_PATH, path)
            info(self, "Backup Complete", f"Database backed up to:\n{dest}")
        except Exception as e:
            error(self, "Backup Failed", str(e))

    def _export_csv(self, which="students"):
        if which == "all":
            folder = QFileDialog.getExistingDirectory(self, "Export folder")
            if not folder: return
            try:
                self._write_students_csv(os.path.join(folder, "students.csv"))
                self._write_instructors_csv(os.path.join(folder, "instructors.csv"))
                self._write_courses_csv(os.path.join(folder, "courses.csv"))
                info(self, "Exported", f"Exported 3 CSV files to:\n{folder}")
            except Exception as e:
                error(self, "Export Failed", str(e))
            return

        title = {"students":"Export Students","instructors":"Export Instructors","courses":"Export Courses"}[which]
        path, _ = QFileDialog.getSaveFileName(self, title, "", "CSV Files (*.csv);;All Files (*)")
        if not path: return
        try:
            if which == "students": self._write_students_csv(path)
            elif which == "instructors": self._write_instructors_csv(path)
            else: self._write_courses_csv(path)
            info(self, "Exported", f"Saved to:\n{path}")
        except Exception as e:
            error(self, "Export Failed", str(e))

    def _write_students_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            import db as DBm
            w = csv.writer(f)
            w.writerow(["student_id","name","age","email","registered_courses"])
            for s in DB.list_students(DB_PATH):
                regs = DBm.list_registrations_for_student(s["student_id"], DB_PATH)
                courses = ", ".join(r["course_name"] for r in regs)
                w.writerow([s["student_id"], s["name"], s["age"], s["email"], courses])

    def _write_instructors_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["instructor_id","name","age","email","assigned_courses"])
            all_courses = DB.list_courses(DB_PATH)
            for i in DB.list_instructors(DB_PATH):
                taught = [c["course_name"] for c in all_courses if c["instructor_id"] == i["instructor_id"]]
                w.writerow([i["instructor_id"], i["name"], i["age"], i["email"], ", ".join(taught)])

    def _write_courses_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["course_id","course_name","instructor","enrolled_students"])
            for c in DB.list_courses(DB_PATH):
                students = DB.list_registrations_for_course(c["course_id"], DB_PATH)
                w.writerow([c["course_id"], c["course_name"], c["instructor_name"],
                            ", ".join(s["name"] for s in students)])

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()