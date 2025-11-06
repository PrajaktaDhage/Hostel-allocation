from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import date

app = Flask(__name__)

# DB Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hostel"
)
cursor = db.cursor()

@app.route('/')
def home():
    cursor.execute("SELECT * FROM Students")
    students = cursor.fetchall()

    cursor.execute("""
        SELECT s.Name, h.HostelName, r.RoomNumber, a.AllocationDate
        FROM Allocation a
        JOIN Students s ON a.StudentID = s.StudentID
        JOIN Rooms r ON a.RoomID = r.RoomID
        JOIN Hostels h ON r.HostelID = h.HostelID
    """)
    allocations = cursor.fetchall()

    return render_template('index.html', students=students, allocations=allocations)

@app.route('/allocate', methods=['POST'])
def allocate():
    student_id = request.form['student_id']

    # Check if student already has a room
    cursor.execute("SELECT * FROM Allocation WHERE StudentID = %s", (student_id,))
    existing = cursor.fetchone()
    if existing:
        return "Student already has a room!"

    # Find first available room
    cursor.execute("SELECT RoomID FROM Rooms WHERE IsOccupied = FALSE LIMIT 1")
    room = cursor.fetchone()
    if room:
        room_id = room[0]
        cursor.execute("INSERT INTO Allocation (StudentID, RoomID, AllocationDate) VALUES (%s, %s, %s)",
                       (student_id, room_id, date.today()))
        cursor.execute("UPDATE Rooms SET IsOccupied = TRUE WHERE RoomID = %s", (room_id,))
        db.commit()
    else:
        return "No available rooms!"

    return redirect('/')

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    gender = request.form['gender']
    dept = request.form['department']
    year = request.form['year']
    cursor.execute("INSERT INTO Students (Name, Gender, Department, Year) VALUES (%s, %s, %s, %s)",
                   (name, gender, dept, year))
    db.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)