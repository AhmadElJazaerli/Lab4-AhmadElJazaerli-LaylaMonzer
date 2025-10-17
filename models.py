import json
from typing import Dict
import re

class Person:
    def __init__(self, name: str, age: int, email: str):
        if not isinstance(name, str) or not name:
            raise ValueError("Name must be  non-empty string")
        if not isinstance(age, int) or age < 0:
            raise ValueError("Age must be  non-negative integer")
        
        self.name = name
        self.age = age
        self._email = email   

    def validate_email(email: str):
        EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
        if not isinstance(email, str) or not  EMAIL_RE.match(email):
            raise ValueError("Invalid email address")

    def introduce(self):
        print(f"Hi, my name is {self.name}, I am {self.age} years old.")

    def  to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "email": self._email
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            age=data["age"],
            email=data["email"]
        )

class Student(Person):
    def __init__(self, name: str, age: int, email: str, student_id: str):
        super().__init__(name, age, email)  
        self.student_id = student_id
        self.registered_courses = []

    def register_course(self, course):
        self.registered_courses.append(course)
        print("Course registered successfully.")

class Instructor(Person):
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        if not isinstance(instructor_id, str) or not instructor_id:
            raise ValueError("Instructor ID must be a non-empty string")
        super().__init__(name, age, email)

        self.instructor_id = instructor_id
        self.assigned_courses = []  

    def assign_course(self, course):
       if course not in self.assigned_courses: 
        self.assigned_courses.append(course)
        print("Course assigned successfully.")

    def to_dict(self):
       return {
          'name': self.name,
          'age': self.age, 
          'email': self._email,
          'instructor_id': self.instructor_id,
          'assigned_courses': self.assigned_courses
       }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            name=data["name"],
            age=data["age"],
            email=data["_email"],
            instructor_id=data["instructor_id"]
        )
        obj.assigned_courses = list(data.get("assigned_courses", []))
        return obj

class Course:
    def __init__(self, course_id: str, course_name: str, instructor=None):
        if not isinstance(instructor, Instructor):
            raise ValueError("Instructor has to be a valid Instructor object.")
        if not isinstance(course_name, str) or not course_name:
            raise ValueError("Course name has to be a non-empty string.")
        if not isinstance(instructor, Instructor):
            raise ValueError("Instructor has to be a valid Instructor object.")
        
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor  
        self.enrolled_students = []  

    def add_student(self, student):
        if not isinstance(student, Student):
            raise ValueError("Student has to be a valid Student object.")
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)
        print("Student has been enrolled successfully.")

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'instructor': self.instructor.to_dict() if self.instructor else None,
            'enrolled_students': [student.to_dict() for student in self.enrolled_students]
        }

    @classmethod
    def from_dict(cls, data):
        students=[Student.from_dict(student_data) for student_data in data.get("enrolled_students", [])]
        instructor=Instructor.from_dict(data["instructor"]) if data.get("instructor") else None
        course=cls(
            course_id=data["course_id"],
            course_name=data["course_name"],
            instructor=instructor
        )
        course.enrolled_students=students
        return course 

class DataStore:
    """
    Keeps collections and handles JSON serialization.
    Relationships are stored by IDs; caller can resolve links after loading if needed.
    """
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}

    def add_student(self, student: Student):
        if student.student_id in self.students:
            raise ValueError(f"Student ID already exists: {student.student_id}")
        self.students[student.student_id] = student

    def add_instructor(self, instructor: Instructor):
        if instructor.instructor_id in self.instructors:
            raise ValueError(f"Instructor ID already exists: {instructor.instructor_id}")
        self.instructors[instructor.instructor_id] = instructor

    def add_course(self, course: Course):
        if course.course_id in self.courses:
            raise ValueError(f"Course ID already exists: {course.course_id}")
        self.courses[course.course_id] = course

    def to_json(self) -> str:
        payload = {
            "students": {sid: s.to_dict() for sid, s in self.students.items()},
            "instructors": {iid: i.to_dict() for iid, i in self.instructors.items()},
            "courses": {cid: c.to_dict() for cid, c in self.courses.items()},
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def from_json(cls, text: str):
        raw = json.loads(text)
        ds = cls()
       
        for sid, sdata in raw.get("students", {}).items():
            ds.students[sid] = Student.from_dict(sdata)
        for iid, idata in raw.get("instructors", {}).items():
            ds.instructors[iid] = Instructor.from_dict(idata)
        for cid, cdata in raw.get("courses", {}).items():
            ds.courses[cid] = Course.from_dict(cdata)
        return ds

    def save_file(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load_file(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())
