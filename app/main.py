import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import sys

sys.path.append('/home/kannan.b2745/rfid')


def create_app():
    app = Flask(__name__, static_folder="styles")
    app.secret_key = "8fc00061972fa46e9cb2d53d2220d6f2"

    client = MongoClient("mongodb+srv://rfid:rfid@signup.ktcqg.mongodb.net/")
    db = client["Sign-in"]
    collection = db["Students"]

    Attendance = client["Students"]["Attendance"]
    StudentAttendance = client["Students"]

    meta_db = client["MetaData"]
    MetaDataStudents = meta_db["Students"]
    MetaDataEntries = meta_db["Entries"]

    admin_db = client["AdminDataBase"]
    AdminStudentList = admin_db["StudentsList"]

    @app.route("/")
    def sign_in():
        return render_template("index.html")

    @app.route("/auth", methods=["POST"])
    def auth():
        rollNumber = request.form.get('rollNo', '').strip()
        dob = request.form.get('DOB', '').strip()
        try:
            if rollNumber == "admin":
                validation = collection.find_one(
                    {"rollNo": rollNumber, "DOB": dob})
                return redirect(url_for("admin_dashboard")) if validation else redirect(url_for("sign_in"))
            else:
                validation = collection.find_one(
                    {"rollNo": rollNumber, "DOB": dob})
                if validation:
                    student_data = dict(MetaDataStudents.find_one(
                        {'rollNumber': str(rollNumber)}))
                    return redirect(url_for("student_dashboard", _rfidTag=student_data.get("rfidTag"), _name=student_data.get("name"), _rollNo=rollNumber, _department=student_data.get("department")))
                else:
                    return redirect(url_for("sign_in"))
        except ValueError:
            return redirect(url_for("sign_in"))

    @app.route("/admin-dashboard")
    def admin_dashboard():
        return render_template("admin_dashboard.html")

    @app.route("/api/generate-attendance", methods=["POST"])
    def generate_attendance():
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        day = str(data.get("day")).zfill(2)
        month = str(data.get("month")).zfill(2)
        year = data.get("year")

        if not day or not month or not year or int(day) > 31 or int(month) > 12 or int(year) < 2000:
            return jsonify([])

        AdminAttendance = admin_db[f"Attendance.{year}_{month}_{day}"]
        attendance_data = []
        for i in AdminAttendance.find({}):
            student_data = dict(MetaDataStudents.find_one(
                {'rfidTag': i["rfidTag"]}))
            attendance_data.append({
                "rollNo": student_data.get("rollNumber"),
                "name": student_data.get("name"),
                "date": f"{i['day']}-{i['month']}-{i['year']}",
                "entryTime": i['inTime'],
                "exitTime": i['outTime']
            })
        return jsonify(attendance_data)

    @app.route("/student-dashboard")
    def student_dashboard():
        return render_template("student_dashboard.html",
                               rfidTag=request.args.get('_rfidTag'),
                               name=request.args.get('_name'),
                               rollNo=request.args.get('_rollNo'),
                               department=request.args.get('_department'))

    @app.route("/api/student-generate-attendance", methods=["POST"])
    def student_generate_attendance():
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        month = data.get("month")
        year = data.get("year")
        rfidTag = data.get("rfidTag")

        if not month or not year or int(month) > 12 or int(year) < 2000:
            return jsonify([])

        student_data = client["Students"][f"Attendance.{str(rfidTag)}.MetaData"]
        if not student_data.find_one({'month': str(month), 'year': str(year)}):
            return jsonify({"error": "No Attendance are Available"}), 400

        students_collection = StudentAttendance[f"Attendance.{rfidTag}"]
        collected_data = list(students_collection.find(
            {'month': int(month), 'year': int(year)}))
        student_info = dict(MetaDataStudents.find_one({'rfidTag': rfidTag}))

        return jsonify([{
            "rollNo": student_info.get("rollNumber"),
            "name": student_info.get("name"),
            "date": f"{i['day']}-{i['month']}-{i['year']}",
            "entryTime": i['inTime'],
            "exitTime": str(i['outTime'])
        } for i in collected_data])

    @app.route('/register-user', methods=['GET', 'POST'])
    def register_user():
        if request.method == 'POST':
            try:
                data = request.get_json()
                student_details = {
                    "name": data.get("name"),
                    "DOB": data.get("dob"),
                    "gender": data.get("gender"),
                    "email": data.get("email"),
                    "rollNumber": str(data.get("rollNumber")),
                    "department": data.get("department"),
                    "batchYear": data.get("batchYear"),
                    "rfidTag": data.get("rfidTag"),
                }
                MetaDataStudents.insert_one(student_details)
                collection.insert_one(
                    {"rollNo": data.get("rollNumber"), "DOB": data.get("dob")})
                AdminStudentList.insert_one(student_details)
                MetaDataEntries.insert_one(
                    {"rfidTag": data.get("rfidTag"), "entryStatus": False})
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        return render_template('register_user.html', admin_dashboard='/admin-dashboard')

    @app.route('/receive-rfid', methods=['POST'])
    def receive_rfid():
        data = request.json
        rfid_id = data.get("rfid")
        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        time_str = ist_now.strftime("%H:%M:%S")

        check = MetaDataEntries.find_one({"rfidTag": rfid_id})
        date_str = datetime.now().strftime("%Y_%m_%d")
        AdminAttendance = admin_db["Attendance"]
        student_entry = AdminAttendance[date_str]

        if check and check.get("entryStatus"):
            student_entry.update_one({"rfidTag": rfid_id, "outTime": "Present"}, {
                                     "$set": {"outTime": time_str}})
            Attendance[rfid_id].update_one({"rfidTag": rfid_id, "outTime": "Present"}, {
                                           "$set": {"outTime": time_str}})
            MetaDataEntries.update_one({"rfidTag": rfid_id}, {
                                       "$set": {"entryStatus": False}})

        elif check:
            student_data = client["Students"][f"Attendance.{rfid_id}"]
            if not student_data["MetaData"].find_one({'month': str(datetime.now().month), 'year': str(datetime.now().year)}):
                student_data["MetaData"].insert_one(
                    {"month": str(datetime.now().month), "year": str(datetime.now().year)})

            details = {
                "rfidTag": rfid_id,
                "day": datetime.now().day,
                "month": datetime.now().month,
                "year": datetime.now().year,
                "inTime": time_str,
                "outTime": "Present",
                "entry": True
            }
            student_entry.insert_one(details)
            Attendance[rfid_id].insert_one(details)
            MetaDataEntries.update_one({"rfidTag": rfid_id}, {
                                       "$set": {"entryStatus": True}})

        else:
            admin_db["NullRFIDs"].insert_one(
                {"rfid": rfid_id, "ScannedTime": time_str})

        return jsonify({"message": "RFID received", "rfid": rfid_id})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5678, debug=True)
