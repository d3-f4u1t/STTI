from app.extentions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False) 

    def __repr__(self):
        return f"<User {self.email}>"

class Timetable(db.Model):
    __tablename__ = "timetables"
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON serialized data

    def __repr__(self):
        return f"<Timetable {self.department} - {self.semester}>"
