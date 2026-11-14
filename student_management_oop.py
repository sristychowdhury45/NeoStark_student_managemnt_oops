import json
import os



# Custom Exception


class StudentNotFoundError(Exception):
    pass


class DuplicateStudentError(Exception):
    pass



# Student Class


class Student:

    def __init__(self, student_id, name, department,
                 marks, attendance, status="Active"):

        self._student_id = student_id
        self._name = name
        self._department = department
        self._marks = marks
        self._attendance = attendance
        self._status = status

        self.validate()

    def validate(self):
        if not self._student_id.strip():
            raise ValueError("Student ID cannot be empty.")

        if not self._name.strip():
            raise ValueError("Student name cannot be empty.")

        if not self._department.strip():
            raise ValueError("Department cannot be empty.")

        if not self._marks:
            raise ValueError("At least one mark is required.")

        if any(not isinstance(m, (int, float)) or isinstance(m, bool)
               or not 0 <= m <= 100 for m in self._marks):
            raise ValueError("Marks must be between 0 and 100.")

        if not isinstance(self._attendance, (int, float)) or isinstance(
                self._attendance, bool
        ) or not 0 <= self._attendance <= 100:
            raise ValueError("Attendance must be between 0 and 100.")

    @property
    def student_id(self):
        return self._student_id

    @property
    def name(self):
        return self._name

    @property
    def department(self):
        return self._department

    @property
    def marks(self):
        return self._marks.copy()

    @property
    def attendance(self):
        return self._attendance

    @property
    def status(self):
        return self._status

    @property
    def average(self):
        return sum(self._marks) / len(self._marks)

    def update(self, name=None, department=None,
               marks=None, attendance=None, status=None):

        old_values = (
            self._name,
            self._department,
            self._marks,
            self._attendance,
            self._status
        )

        try:
            if name is not None:
                self._name = name

            if department is not None:
                self._department = department

            if marks is not None:
                self._marks = marks

            if attendance is not None:
                self._attendance = attendance

            if status is not None:
                self._status = status

            self.validate()

        except ValueError:
            (
                self._name,
                self._department,
                self._marks,
                self._attendance,
                self._status
            ) = old_values
            raise

    def to_dict(self):
        return {
            "id": self._student_id,
            "name": self._name,
            "department": self._department,
            "marks": self._marks,
            "attendance": self._attendance,
            "status": self._status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["name"],
            data["department"],
            data["marks"],
            data["attendance"],
            data.get("status", "Active")
        )



# File Manager Class


class FileManager:

    FILE_NAME = "students.json"

    @staticmethod
    def save_students(students):
        try:
            data = [student.to_dict() for student in students]

            with open(FileManager.FILE_NAME, "w") as file:
                json.dump(data, file, indent=4)

            return True

        except (OSError, TypeError) as error:
            print("File saving error:", error)
            return False

    @staticmethod
    def load_students():
        if not os.path.exists(FileManager.FILE_NAME):
            return []

        try:
            with open(FileManager.FILE_NAME, "r") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("Invalid JSON file format.")

            students = []
            ids = set()

            for record in data:
                student = Student.from_dict(record)

                if student.student_id in ids:
                    raise ValueError("Duplicate ID in saved records.")

                ids.add(student.student_id)
                students.append(student)

            return students

        except (OSError, json.JSONDecodeError, ValueError,
                KeyError, TypeError) as error:
            print("Error loading records:", error)
            return []



# Student Manager Class


class StudentManager:

    def __init__(self):
        self.students = {}

        for student in FileManager.load_students():
            self.students[student.student_id] = student

    def save(self):
        return FileManager.save_students(self.students.values())

    def add_student(self, student):

        if student.student_id in self.students:
            raise DuplicateStudentError("Student ID already exists.")

        self.students[student.student_id] = student

        if self.save():
            print("Student added successfully!")
        else:
            del self.students[student.student_id]
            print("Student was not added because saving failed.")

    def view_students(self):

        if not self.students:
            print("No student records found.")
            return

        print("\n========== STUDENT RECORDS ==========")

        for student in self.students.values():
            print(
                f"{student.student_id} | "
                f"{student.name} | {student.department}"
            )
            print(f"Average: {student.average:.1f}%")
            print(f"Attendance: {student.attendance}%")
            print(f"Status: {student.status}")
            print("-------------------------------------")

    def search_student(self, student_id):

        if student_id not in self.students:
            raise StudentNotFoundError("Student record not found.")

        return self.students[student_id]

    def update_student(self, student_id, **details):

        student = self.search_student(student_id)

        student.update(**details)

        if self.save():
            print("Student updated successfully!")
        else:
            print("Update could not be saved.")

    def delete_student(self, student_id):

        student = self.search_student(student_id)

        del self.students[student_id]

        if self.save():
            print("Student deleted successfully!")
        else:
            self.students[student_id] = student
            print("Deletion could not be saved.")

    def get_all_students(self):
        return list(self.students.values())



# Report Generator Class


class ReportGenerator:

    @staticmethod
    def get_performance(average):

        if average >= 90:
            return "Excellent"
        elif average >= 80:
            return "Very Good"
        elif average >= 70:
            return "Good"
        elif average >= 60:
            return "Average"
        elif average >= 40:
            return "Pass"
        else:
            return "Fail"

    @staticmethod
    def generate_report(student):

        print("\n========== STUDENT REPORT ==========")
        print("------------------------------------")
        print(
            f"{student.student_id} | "
            f"{student.name} | {student.department}"
        )
        print(f"Average: {student.average:.1f}%")
        print(f"Attendance: {student.attendance}%")
        print(
            "Performance:",
            ReportGenerator.get_performance(student.average)
        )
        print("Status:", student.status)
        print("------------------------------------")

    @staticmethod
    def generate_all_reports(students):

        if not students:
            print("No records available for reporting.")
            return

        print("\n========== PERFORMANCE REPORT ==========")

        for student in students:
            ReportGenerator.generate_report(student)



# Main Application Class


class StudentApplication:

    def __init__(self):
        self.manager = StudentManager()

    def add_student(self):

        student_id = input("Student ID: ").strip()
        name = input("Student Name: ").strip()
        department = input("Department: ").strip()

        marks = [
            float(x.strip())
            for x in input("Marks (comma separated): ").split(",")
        ]

        attendance = float(input("Attendance (%): "))

        student = Student(
            student_id, name, department, marks, attendance
        )

        self.manager.add_student(student)

    def search_student(self):

        student_id = input("Enter Student ID: ").strip()

        student = self.manager.search_student(student_id)

        ReportGenerator.generate_report(student)

    def update_student(self):

        student_id = input("Enter Student ID to update: ").strip()

        self.manager.search_student(student_id)

        print("Press Enter to keep the existing value.")

        name = input("New Name: ").strip()
        department = input("New Department: ").strip()
        marks_input = input("New Marks (comma separated): ").strip()
        attendance_input = input("New Attendance: ").strip()
        status = input("New Status (Active/Inactive): ").strip()

        details = {}

        if name:
            details["name"] = name

        if department:
            details["department"] = department

        if marks_input:
            details["marks"] = [
                float(x.strip()) for x in marks_input.split(",")
            ]

        if attendance_input:
            details["attendance"] = float(attendance_input)

        if status:
            details["status"] = status

        if details:
            self.manager.update_student(student_id, **details)
        else:
            print("No changes entered.")

    def delete_student(self):

        student_id = input("Enter Student ID to delete: ").strip()

        self.manager.delete_student(student_id)

    def run(self):

        print("\n========================================")
        print("     STUDENT MANAGEMENT SYSTEM - OOP")
        print("========================================")
        print("Records loaded:", len(self.manager.students))

        while True:

            print("\nChoose an option:")
            print("1. Add Student")
            print("2. View Students")
            print("3. Search Student")
            print("4. Update Student")
            print("5. Delete Student")
            print("6. Performance Report")
            print("7. Save Records")
            print("8. Exit")

            choice = input("\nEnter your choice: ").strip()

            try:

                if choice == "1":
                    self.add_student()

                elif choice == "2":
                    self.manager.view_students()

                elif choice == "3":
                    self.search_student()

                elif choice == "4":
                    self.update_student()

                elif choice == "5":
                    self.delete_student()

                elif choice == "6":
                    ReportGenerator.generate_all_reports(
                        self.manager.get_all_students()
                    )

                elif choice == "7":
                    if self.manager.save():
                        print("Records saved successfully!")

                elif choice == "8":
                    if self.manager.save():
                        print("Records saved successfully!")

                    print("Thank you for using the system!")
                    break

                else:
                    print("Invalid choice! Select 1 to 8.")

            except (ValueError, StudentNotFoundError,
                    DuplicateStudentError, KeyError) as error:
                print("Error:", error)

            except (KeyboardInterrupt, EOFError):
                print("\nInput interrupted. Exiting safely.")
                self.manager.save()
                break

            except Exception as error:
                print("Unexpected error:", error)



# Program Execution


if __name__ == "__main__":

    app = StudentApplication()
    app.run()
