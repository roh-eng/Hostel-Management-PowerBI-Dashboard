"""
Smart Hostel Analytics - Synthetic Dataset Generator
=====================================================

Generates a realistic, internally consistent dataset for the
"Smart Hostel Analytics - Business Intelligence Dashboard" Power BI project.

- Standard library only (no external dependencies).
- Deterministic: fixed RANDOM_SEED makes every run reproducible.
- Enforces all referential-integrity and business rules (no orphan records).

Run:
    python scripts/generate_dataset.py

Output:
    data/raw/*.csv  (one file per table)

Author: Data Engineering Team
"""

import csv
import os
import random
from datetime import date, timedelta

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
RANDOM_SEED = 42
YEAR = 2025
START_DATE = date(YEAR, 1, 1)
END_DATE = date(YEAR, 12, 31)

NUM_HOSTELS = 5
NUM_ROOMS = 250            # 50 per hostel
NUM_STUDENTS = 500         # 100 per hostel
NUM_COMPLAINTS = 800
NUM_VISITORS = 3000

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

random.seed(RANDOM_SEED)

# --------------------------------------------------------------------------- #
# Reference data (realistic Indian names)
# --------------------------------------------------------------------------- #
MALE_FIRST = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Krishna", "Ishaan",
    "Rohan", "Karthik", "Aniket", "Siddharth", "Rahul", "Aman", "Harsh", "Yash",
    "Nikhil", "Pranav", "Akash", "Manish", "Sai", "Tarun", "Varun", "Dhruv",
    "Kabir", "Ayaan", "Rudra", "Shaurya", "Veer", "Naveen",
]
FEMALE_FIRST = [
    "Aanya", "Diya", "Aadhya", "Saanvi", "Ananya", "Pari", "Anika", "Navya",
    "Ira", "Myra", "Priya", "Sneha", "Pooja", "Kavya", "Riya", "Isha",
    "Meera", "Nisha", "Divya", "Shreya", "Tanvi", "Sakshi", "Neha", "Swati",
    "Lakshmi", "Bhavya", "Charvi", "Aarohi", "Mahi", "Trisha",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Reddy", "Nair", "Iyer", "Menon",
    "Singh", "Kumar", "Rao", "Das", "Bose", "Chopra", "Malhotra", "Joshi",
    "Mehta", "Shah", "Pillai", "Naidu", "Mishra", "Pandey", "Agarwal", "Bhat",
    "Desai", "Kulkarni", "Saxena", "Chauhan", "Yadav", "Khanna",
]

HOSTELS = [
    # (HostelName, HostelType, WardenName, Capacity)
    ("Aravali Boys Hostel", "Boys", "Dr. Rajesh Kumar", 150),
    ("Nilgiri Boys Hostel", "Boys", "Mr. Suresh Menon", 150),
    ("Shivalik Girls Hostel", "Girls", "Dr. Anita Sharma", 150),
    ("Vindhya Girls Hostel", "Girls", "Mrs. Kavita Nair", 150),
    ("Satpura Co-ed Hostel", "Co-ed", "Dr. Vikram Singh", 150),
]

DEPARTMENTS = ["CSE", "ECE", "EEE", "Mechanical", "Civil", "AI & DS"]
YEARS = [1, 2, 3, 4]

COMPLAINT_CATEGORIES = ["WiFi", "Plumbing", "Electricity", "Cleaning", "Furniture", "Security"]
COMPLAINT_PRIORITY = ["High", "Medium", "Low"]
COMPLAINT_STATUS = ["Open", "In Progress", "Closed"]

VISITOR_RELATIONS = ["Father", "Mother", "Brother", "Sister", "Friend", "Guardian"]
MEALS = ["Breakfast", "Lunch", "Dinner"]

UNIVERSITY_DOMAIN = "university.edu"

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def daterange(start, end):
    """Yield each date from start to end inclusive."""
    days = (end - start).days
    for n in range(days + 1):
        yield start + timedelta(days=n)


def random_phone():
    return "+91" + str(random.randint(6, 9)) + "".join(str(random.randint(0, 9)) for _ in range(9))


def write_csv(filename, header, rows):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  {filename:<24} {len(rows):>8,} rows")
    return len(rows)


# --------------------------------------------------------------------------- #
# 1. Hostels
# --------------------------------------------------------------------------- #
def build_hostels():
    rows = []
    for i, (name, htype, warden, cap) in enumerate(HOSTELS, start=1):
        rows.append([i, name, cap, htype, warden])
    return rows  # [HostelID, HostelName, Capacity, HostelType, WardenName]


# --------------------------------------------------------------------------- #
# 2. Rooms  (50 rooms/hostel, 5 floors x 10 rooms, capacity 2-3)
# --------------------------------------------------------------------------- #
def build_rooms():
    rows = []
    room_id = 1
    rooms_by_hostel = {h: [] for h in range(1, NUM_HOSTELS + 1)}
    for hostel_id in range(1, NUM_HOSTELS + 1):
        for floor in range(1, 6):                  # 5 floors
            for r in range(1, 11):                  # 10 rooms per floor
                room_number = f"{floor}{r:02d}"     # e.g. 101, 102 ... 510
                capacity = random.choice([2, 2, 3]) # mostly doubles
                rows.append([room_id, hostel_id, room_number, floor, capacity])
                rooms_by_hostel[hostel_id].append({"RoomID": room_id, "Capacity": capacity, "filled": 0})
                room_id += 1
    return rows, rooms_by_hostel  # [RoomID, HostelID, RoomNumber, Floor, Capacity]


# --------------------------------------------------------------------------- #
# 3. Students  (100/hostel, gender matches hostel type, valid room allocation)
# --------------------------------------------------------------------------- #
def build_students(rooms_by_hostel):
    rows = []
    students = []           # internal records reused by fact tables
    used_emails = set()
    student_id = 1
    dept_counters = {d: 0 for d in DEPARTMENTS}

    students_per_hostel = NUM_STUDENTS // NUM_HOSTELS  # 100

    for hostel_id in range(1, NUM_HOSTELS + 1):
        htype = HOSTELS[hostel_id - 1][1]
        room_pool = rooms_by_hostel[hostel_id]
        room_cursor = 0

        for _ in range(students_per_hostel):
            # Gender per hostel type
            if htype == "Boys":
                gender = "Male"
            elif htype == "Girls":
                gender = "Female"
            else:
                gender = random.choice(["Male", "Female"])

            first = random.choice(MALE_FIRST if gender == "Male" else FEMALE_FIRST)
            last = random.choice(LAST_NAMES)

            department = random.choice(DEPARTMENTS)
            year = random.choice(YEARS)

            # Roll number e.g. U25CSE0001  (admission year encoded as 25 - (year-1))
            admission_year = YEAR - (year - 1)
            dept_counters[department] += 1
            dept_code = department.replace(" & ", "").replace(" ", "")[:3].upper()
            roll = f"U{str(admission_year)[-2:]}{dept_code}{dept_counters[department]:04d}"

            # Unique email
            base_email = f"{first.lower()}.{last.lower()}{str(admission_year)[-2:]}"
            email = f"{base_email}@{UNIVERSITY_DOMAIN}"
            suffix = 1
            while email in used_emails:
                suffix += 1
                email = f"{base_email}{suffix}@{UNIVERSITY_DOMAIN}"
            used_emails.add(email)

            phone = random_phone()
            dob = date(YEAR - (17 + year), random.randint(1, 12), random.randint(1, 28))
            admission_date = date(admission_year, random.choice([7, 8]), random.randint(1, 28))

            # Allocate a room with free capacity (never exceed room limit)
            while room_pool[room_cursor]["filled"] >= room_pool[room_cursor]["Capacity"]:
                room_cursor += 1
            room = room_pool[room_cursor]
            room["filled"] += 1
            room_id = room["RoomID"]

            rows.append([
                student_id, roll, first, last, gender, dob.isoformat(),
                department, year, phone, email, hostel_id, room_id,
                admission_date.isoformat(),
            ])
            students.append({
                "StudentID": student_id,
                "HostelID": hostel_id,
                "AdmissionDate": admission_date,
            })
            student_id += 1

    return rows, students


# --------------------------------------------------------------------------- #
# 4. Attendance  (every student, every day; ~92% Present)
# --------------------------------------------------------------------------- #
def build_attendance(students):
    rows = []
    attendance_id = 1
    all_dates = list(daterange(START_DATE, END_DATE))
    statuses = ["Present", "Absent", "Leave"]
    weights = [0.92, 0.05, 0.03]
    for s in students:
        for d in all_dates:
            # Only count days on/after admission; before that, treat as not-yet-resident
            status = random.choices(statuses, weights=weights, k=1)[0]
            rows.append([attendance_id, s["StudentID"], d.isoformat(), status])
            attendance_id += 1
    return rows  # [AttendanceID, StudentID, Date, Status]


# --------------------------------------------------------------------------- #
# 5. Complaints  (~800; valid students; resolution depends on status)
# --------------------------------------------------------------------------- #
def build_complaints(students):
    rows = []
    all_dates = list(daterange(START_DATE, END_DATE))
    for cid in range(1, NUM_COMPLAINTS + 1):
        student = random.choice(students)
        cdate = random.choice(all_dates)
        category = random.choice(COMPLAINT_CATEGORIES)
        priority = random.choices(COMPLAINT_PRIORITY, weights=[0.25, 0.45, 0.30], k=1)[0]
        status = random.choices(COMPLAINT_STATUS, weights=[0.15, 0.20, 0.65], k=1)[0]

        if status == "Closed":
            # High priority resolved faster
            if priority == "High":
                resolution = random.randint(1, 4)
            elif priority == "Medium":
                resolution = random.randint(2, 8)
            else:
                resolution = random.randint(3, 15)
        else:
            resolution = ""  # Open / In Progress -> not yet resolved

        rows.append([cid, student["StudentID"], cdate.isoformat(),
                     category, priority, status, resolution])
    return rows  # [ComplaintID, StudentID, ComplaintDate, Category, Priority, Status, ResolutionDays]


# --------------------------------------------------------------------------- #
# Occupancy per hostel (for utility correlation)
# --------------------------------------------------------------------------- #
def occupancy_by_hostel(students):
    occ = {h: 0 for h in range(1, NUM_HOSTELS + 1)}
    for s in students:
        occ[s["HostelID"]] += 1
    return occ


# --------------------------------------------------------------------------- #
# 6. ElectricityUsage  (daily/hostel; higher in summer Apr-Jun)
# --------------------------------------------------------------------------- #
def build_electricity(occupancy):
    rows = []
    usage_id = 1
    summer_months = {4, 5, 6}          # peak AC/cooler load
    shoulder_months = {3, 7, 8, 9}     # warm
    for hostel_id in range(1, NUM_HOSTELS + 1):
        occ = occupancy[hostel_id]
        base = occ * 4.0               # ~4 kWh per student baseline
        for d in daterange(START_DATE, END_DATE):
            if d.month in summer_months:
                seasonal = 1.55
            elif d.month in shoulder_months:
                seasonal = 1.20
            else:
                seasonal = 1.0
            noise = random.uniform(0.9, 1.1)
            units = round(base * seasonal * noise, 2)
            rows.append([usage_id, hostel_id, d.isoformat(), units])
            usage_id += 1
    return rows  # [UsageID, HostelID, Date, UnitsConsumed]


# --------------------------------------------------------------------------- #
# 7. WaterUsage  (daily/hostel; correlated with occupancy ~135 L/student/day)
# --------------------------------------------------------------------------- #
def build_water(occupancy):
    rows = []
    usage_id = 1
    summer_months = {4, 5, 6}
    for hostel_id in range(1, NUM_HOSTELS + 1):
        occ = occupancy[hostel_id]
        base = occ * 135.0             # litres per student per day
        for d in daterange(START_DATE, END_DATE):
            seasonal = 1.20 if d.month in summer_months else 1.0
            noise = random.uniform(0.9, 1.1)
            litres = round(base * seasonal * noise, 1)
            rows.append([usage_id, hostel_id, d.isoformat(), litres])
            usage_id += 1
    return rows  # [UsageID, HostelID, Date, LitersConsumed]


# --------------------------------------------------------------------------- #
# 8. Visitors  (~3000; mostly weekends)
# --------------------------------------------------------------------------- #
def build_visitors(students):
    rows = []
    all_dates = list(daterange(START_DATE, END_DATE))
    # Weight weekends heavily
    date_weights = [5 if d.weekday() >= 5 else 1 for d in all_dates]

    for vid in range(1, NUM_VISITORS + 1):
        student = random.choice(students)
        relation = random.choice(VISITOR_RELATIONS)

        # Visitor surname often matches the family relations
        if relation in ("Father", "Mother", "Brother", "Sister"):
            vlast = random.choice(LAST_NAMES)
            vfirst = random.choice(MALE_FIRST if relation in ("Father", "Brother") else FEMALE_FIRST)
        else:
            vfirst = random.choice(MALE_FIRST + FEMALE_FIRST)
            vlast = random.choice(LAST_NAMES)
        visitor_name = f"{vfirst} {vlast}"

        vdate = random.choices(all_dates, weights=date_weights, k=1)[0]
        check_in_hour = random.randint(9, 17)
        check_in_min = random.choice([0, 15, 30, 45])
        duration = random.randint(30, 180)  # minutes
        ci_total = check_in_hour * 60 + check_in_min
        co_total = min(ci_total + duration, 19 * 60)  # gates close ~19:00
        check_in = f"{ci_total // 60:02d}:{ci_total % 60:02d}"
        check_out = f"{co_total // 60:02d}:{co_total % 60:02d}"

        rows.append([vid, student["StudentID"], visitor_name, relation,
                     vdate.isoformat(), check_in, check_out])
    return rows  # [VisitorID, StudentID, VisitorName, Relation, VisitDate, CheckIn, CheckOut]


# --------------------------------------------------------------------------- #
# 9. MessAttendance  (every student, every day, 3 meals; ~90% Taken)
# --------------------------------------------------------------------------- #
def build_mess(students):
    rows = []
    mess_id = 1
    all_dates = list(daterange(START_DATE, END_DATE))
    # Breakfast skipped a bit more often than lunch/dinner
    meal_taken_prob = {"Breakfast": 0.85, "Lunch": 0.92, "Dinner": 0.90}
    for s in students:
        sid = s["StudentID"]
        for d in all_dates:
            diso = d.isoformat()
            for meal in MEALS:
                taken = random.random() < meal_taken_prob[meal]
                status = "Taken" if taken else "Skipped"
                rows.append([mess_id, sid, diso, meal, status])
                mess_id += 1
    return rows  # [MessID, StudentID, Date, Meal, Status]


# --------------------------------------------------------------------------- #
# 10. DateDimension  (every date in 2025)
# --------------------------------------------------------------------------- #
def build_date_dimension():
    rows = []
    for d in daterange(START_DATE, END_DATE):
        weekday = DAY_NAMES[d.weekday()]
        is_weekend = "Yes" if d.weekday() >= 5 else "No"
        quarter = f"Q{(d.month - 1) // 3 + 1}"
        week_number = int(d.strftime("%W"))
        rows.append([
            d.isoformat(), d.day, MONTH_NAMES[d.month - 1], d.month,
            quarter, d.year, weekday, week_number, is_weekend,
        ])
    return rows  # [Date, Day, Month, MonthNumber, Quarter, Year, Weekday, WeekNumber, IsWeekend]


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating Smart Hostel Analytics dataset (seed={RANDOM_SEED}) ...\n")

    summary = {}

    hostels = build_hostels()
    summary["Hostels"] = write_csv(
        "Hostels.csv",
        ["HostelID", "HostelName", "Capacity", "HostelType", "WardenName"],
        hostels)

    rooms, rooms_by_hostel = build_rooms()
    summary["Rooms"] = write_csv(
        "Rooms.csv",
        ["RoomID", "HostelID", "RoomNumber", "Floor", "Capacity"],
        rooms)

    students, student_records = build_students(rooms_by_hostel)
    summary["Students"] = write_csv(
        "Students.csv",
        ["StudentID", "RollNumber", "FirstName", "LastName", "Gender", "DOB",
         "Department", "Year", "Phone", "Email", "HostelID", "RoomID", "AdmissionDate"],
        students)

    occupancy = occupancy_by_hostel(student_records)

    attendance = build_attendance(student_records)
    summary["Attendance"] = write_csv(
        "Attendance.csv",
        ["AttendanceID", "StudentID", "Date", "Status"],
        attendance)

    complaints = build_complaints(student_records)
    summary["Complaints"] = write_csv(
        "Complaints.csv",
        ["ComplaintID", "StudentID", "ComplaintDate", "Category", "Priority", "Status", "ResolutionDays"],
        complaints)

    electricity = build_electricity(occupancy)
    summary["ElectricityUsage"] = write_csv(
        "ElectricityUsage.csv",
        ["UsageID", "HostelID", "Date", "UnitsConsumed"],
        electricity)

    water = build_water(occupancy)
    summary["WaterUsage"] = write_csv(
        "WaterUsage.csv",
        ["UsageID", "HostelID", "Date", "LitersConsumed"],
        water)

    visitors = build_visitors(student_records)
    summary["Visitors"] = write_csv(
        "Visitors.csv",
        ["VisitorID", "StudentID", "VisitorName", "Relation", "VisitDate", "CheckIn", "CheckOut"],
        visitors)

    mess = build_mess(student_records)
    summary["MessAttendance"] = write_csv(
        "MessAttendance.csv",
        ["MessID", "StudentID", "Date", "Meal", "Status"],
        mess)

    date_dim = build_date_dimension()
    summary["DateDimension"] = write_csv(
        "DateDimension.csv",
        ["Date", "Day", "Month", "MonthNumber", "Quarter", "Year", "Weekday", "WeekNumber", "IsWeekend"],
        date_dim)

    total = sum(summary.values())
    print("\n" + "-" * 40)
    print(f"  {'TOTAL':<24} {total:>8,} rows")
    print("-" * 40)
    print(f"\nDone. Files written to: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()
