# Smart Hostel Analytics – Dataset Data Dictionary

> Companion to the synthetic dataset in `data/raw/`.
> Generator: `scripts/generate_dataset.py` (seed = 42, reproducible).
> Coverage: full academic year **2025** (2025-01-01 → 2025-12-31).

All CSV files are UTF-8 encoded, comma-delimited, with a header row.
Dates use ISO format `YYYY-MM-DD`; times use `HH:MM` (24-hour).

---

## 1. Hostels.csv  — 5 rows
| Column | Type | Description | Example |
|---|---|---|---|
| HostelID | Integer (PK) | Unique hostel identifier | 1 |
| HostelName | Text | Hostel name | Aravali Boys Hostel |
| Capacity | Integer | Maximum student capacity | 150 |
| HostelType | Text | Boys / Girls / Co-ed | Boys |
| WardenName | Text | Warden in charge | Dr. Rajesh Kumar |

## 2. Rooms.csv  — 250 rows
| Column | Type | Description | Example |
|---|---|---|---|
| RoomID | Integer (PK) | Unique room identifier | 1 |
| HostelID | Integer (FK → Hostels) | Owning hostel | 1 |
| RoomNumber | Text | Floor-based room number | 101 |
| Floor | Integer | Floor number (1–5) | 1 |
| Capacity | Integer | Max occupants (2–3) | 2 |

## 3. Students.csv  — 500 rows
| Column | Type | Description | Example |
|---|---|---|---|
| StudentID | Integer (PK) | Unique student identifier | 1 |
| RollNumber | Text | University roll number | U23CSE0001 |
| FirstName | Text | First name | Aditya |
| LastName | Text | Last name | Yadav |
| Gender | Text | Male / Female (matches hostel type) | Male |
| DOB | Date | Date of birth | 2005-08-08 |
| Department | Text | CSE / ECE / EEE / Mechanical / Civil / AI & DS | CSE |
| Year | Integer | Year of study (1–4) | 3 |
| Phone | Text | Indian mobile number (+91…) | +916834738299 |
| Email | Text | University email (unique) | aditya.yadav23@university.edu |
| HostelID | Integer (FK → Hostels) | Allotted hostel | 1 |
| RoomID | Integer (FK → Rooms) | Allotted room | 1 |
| AdmissionDate | Date | Hostel admission date | 2023-08-26 |

## 4. Attendance.csv  — 182,500 rows
*Grain: one row per student per day. (~92% Present)*
| Column | Type | Description | Example |
|---|---|---|---|
| AttendanceID | Integer (PK) | Unique record | 1 |
| StudentID | Integer (FK → Students) | Student | 1 |
| Date | Date | Attendance date | 2025-01-01 |
| Status | Text | Present / Absent / Leave | Present |

## 5. Complaints.csv  — 800 rows
| Column | Type | Description | Example |
|---|---|---|---|
| ComplaintID | Integer (PK) | Unique complaint | 1 |
| StudentID | Integer (FK → Students) | Raising student | 89 |
| ComplaintDate | Date | Date raised (in 2025) | 2025-04-16 |
| Category | Text | WiFi / Plumbing / Electricity / Cleaning / Furniture / Security | WiFi |
| Priority | Text | High / Medium / Low | Low |
| Status | Text | Open / In Progress / Closed | Closed |
| ResolutionDays | Integer | Days to resolve; **blank** when not Closed | 4 |

## 6. ElectricityUsage.csv  — 1,825 rows
*Grain: one row per hostel per day. Higher in summer (Apr–Jun).*
| Column | Type | Description | Example |
|---|---|---|---|
| UsageID | Integer (PK) | Unique reading | 1 |
| HostelID | Integer (FK → Hostels) | Hostel | 1 |
| Date | Date | Reading date | 2025-01-01 |
| UnitsConsumed | Decimal | Electricity used (kWh) | 412.55 |

## 7. WaterUsage.csv  — 1,825 rows
*Grain: one row per hostel per day. Correlated with occupancy (~135 L/student/day).*
| Column | Type | Description | Example |
|---|---|---|---|
| UsageID | Integer (PK) | Unique reading | 1 |
| HostelID | Integer (FK → Hostels) | Hostel | 1 |
| Date | Date | Reading date | 2025-01-01 |
| LitersConsumed | Decimal | Water used (litres) | 13620.5 |

## 8. Visitors.csv  — 3,000 rows
*Mostly weekend visits (~66%).*
| Column | Type | Description | Example |
|---|---|---|---|
| VisitorID | Integer (PK) | Unique visit | 1 |
| StudentID | Integer (FK → Students) | Student visited | 195 |
| VisitorName | Text | Visitor full name | Arjun Bhat |
| Relation | Text | Father / Mother / Brother / Sister / Friend / Guardian | Father |
| VisitDate | Date | Date of visit | 2025-06-01 |
| CheckIn | Time | Entry time (HH:MM) | 11:30 |
| CheckOut | Time | Exit time (HH:MM ≥ CheckIn) | 14:00 |

## 9. MessAttendance.csv  — 547,500 rows
*Grain: one row per student per meal per day (3 meals). (~89% Taken)*
| Column | Type | Description | Example |
|---|---|---|---|
| MessID | Integer (PK) | Unique record | 1 |
| StudentID | Integer (FK → Students) | Student | 1 |
| Date | Date | Meal date | 2025-01-01 |
| Meal | Text | Breakfast / Lunch / Dinner | Breakfast |
| Status | Text | Taken / Skipped | Taken |

## 10. DateDimension.csv  — 365 rows
| Column | Type | Description | Example |
|---|---|---|---|
| Date | Date (PK) | Calendar date | 2025-01-01 |
| Day | Integer | Day of month | 1 |
| Month | Text | Month name | January |
| MonthNumber | Integer | Month number (1–12) | 1 |
| Quarter | Text | Q1–Q4 | Q1 |
| Year | Integer | Calendar year | 2025 |
| Weekday | Text | Day name | Wednesday |
| WeekNumber | Integer | Week of year | 0 |
| IsWeekend | Text | Yes / No | No |

---

## Relationships (for Power BI modeling)
```
Hostels (1) ──< Rooms (Many)         on HostelID
Hostels (1) ──< Students (Many)      on HostelID
Rooms   (1) ──< Students (Many)      on RoomID
Students(1) ──< Attendance (Many)    on StudentID
Students(1) ──< Complaints (Many)    on StudentID
Students(1) ──< Visitors (Many)      on StudentID
Students(1) ──< MessAttendance(Many) on StudentID
Hostels (1) ──< ElectricityUsage     on HostelID
Hostels (1) ──< WaterUsage           on HostelID
DateDimension (1) ──< Attendance / Complaints / ElectricityUsage /
                      WaterUsage / Visitors / MessAttendance   on Date
```
Set all relationships to **single-direction, one-to-many**, and mark
`DateDimension[Date]` as the official **Date table**.

---

## Validation performed (all passed)
- 0 orphan foreign-key records across every fact table.
- 0 room over-capacity violations.
- 0 gender / hostel-type mismatches.
- Attendance Present ≈ 92%; Mess Taken ≈ 89%; Visitors on weekends ≈ 66%.
- Electricity avg ≈ 619 kWh/day (summer) vs ≈ 400 kWh/day (winter).
