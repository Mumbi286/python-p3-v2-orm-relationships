from __init__ import CURSOR, CONN
from department import Department

class Employee:

    all = {}  # Track all Employee instances by id

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id
        if id is not None:
            Employee.all[id] = self  # Track this instance

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept {self.department_id}>"

    @classmethod
    def create_table(cls):
        sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY(department_id) REFERENCES departments(id)
        )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = """
        INSERT INTO employees (name, job_title, department_id)
        VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Employee.all[self.id] = self  # Track instance

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        sql = """
        UPDATE employees
        SET name = ?, job_title = ?, department_id = ?
        WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        # Remove from Employee.all
        if self.id in Employee.all:
            employee_id = self.id
            del Employee.all[self.id]

        # Delete from database
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        # Reset this instance's id
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            return cls.all[row[0]]  # Return existing instance
        return cls(row[1], row[2], row[3], row[0])

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_name(cls, name):
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
