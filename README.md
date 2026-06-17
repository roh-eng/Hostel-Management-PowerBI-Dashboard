# Smart Hostel Analytics – Business Intelligence Dashboard

An end-to-end Power BI solution that consolidates hostel operational data from multiple departments into a single, interactive Business Intelligence dashboard. It helps university administrators monitor hostel operations, optimize resource usage, improve student services, and make data-driven decisions.

![Tool](https://img.shields.io/badge/Tool-Power%20BI-yellow)
![Language](https://img.shields.io/badge/Language-DAX-blue)
![ETL](https://img.shields.io/badge/ETL-Power%20Query-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Business Objectives](#business-objectives)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Data Dictionary](#data-dictionary)
- [DAX Measures](#dax-measures)
- [Dashboards](#dashboards)
- [Advanced Features](#advanced-features)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [How to Use](#how-to-use)
- [Business Insights](#business-insights)
- [Future Scope](#future-scope)
- [Author](#author)

---

## Problem Statement

Greenfield University operates multiple hostels accommodating hundreds of students. Operational data is maintained separately by different departments — Hostel Administration, Maintenance, Mess Management, and Security — making it difficult to obtain a unified view of operations.

This project delivers a centralized BI dashboard that provides insight into occupancy, student attendance, utility consumption, complaint management, visitor activity, and mess operations, supporting both day-to-day monitoring and strategic decision-making.

---

## Business Objectives

- Monitor hostel occupancy across all hostels.
- Optimize electricity and water consumption.
- Improve complaint resolution efficiency.
- Analyze mess attendance and estimate food wastage.
- Monitor visitor activity for enhanced security.
- Provide actionable insights for university management.

---

## Architecture

```
   CSV Files
      │
      ▼
Power Query (ETL)
      │
      ▼
Star Schema Data Model
      │
      ▼
DAX Calculations
      │
      ▼
Interactive Dashboards
      │
      ▼
Business Insights & Decisions
```

> Full schema, data types, keys, business rules, and SQL DDL are documented in [docs/Database_Design.md](docs/Database_Design.md).

---

## Data Model

The solution uses a **Star Schema** with single-direction, one-to-many relationships.

**Dimension Tables**

| Table | Description |
| ----- | ----------- |
| DimDate | Calendar table for time intelligence |
| DimStudent | Student demographics and details |
| DimHostel | Hostel master information |
| DimRoom | Room-level details |

**Fact Tables**

| Table | Approx. Records | Description |
| ----- | --------------- | ----------- |
| FactAttendance | 90,000 | Daily student attendance |
| FactElectricity | 365 | Daily electricity consumption |
| FactWater | 365 | Daily water consumption |
| FactMess | 100,000 | Meal-wise mess attendance |
| FactComplaints | 3,000 | Complaint records and resolution |
| FactVisitors | 6,000 | Visitor entry logs |

> ER Diagram: `docs/ER_Diagram.png` · Data Model: `docs/Data_Model.png`

---

## Data Dictionary

A summary of key fields. Full column-level definitions, data types, and constraints are in [docs/Database_Design.md](docs/Database_Design.md).

| Table | Key Fields |
| ----- | ---------- |
| DimStudent | StudentID, Name, Gender, Department, AcademicYear, HostelID, RoomID |
| DimHostel | HostelID, HostelName, Capacity, TotalRooms |
| DimRoom | RoomID, HostelID, Floor, RoomType, IsOccupied |
| DimDate | Date, Day, Month, Quarter, Year |
| FactElectricity | Date, HostelID, UnitsConsumed, Cost |
| FactWater | Date, HostelID, LitresConsumed |
| FactComplaints | ComplaintID, StudentID, HostelID, Category, Priority, Status, RaisedDate, ResolvedDate |
| FactMess | Date, StudentID, HostelID, MealType, Attended |
| FactVisitors | VisitorID, StudentID, HostelID, EntryTime, ExitTime |
| FactAttendance | Date, StudentID, HostelID, Status |

---

## DAX Measures

Approximately 25 measures power the analytics, including:

- Total Students
- Occupied Rooms
- Vacant Rooms
- Occupancy Rate (`Occupied Rooms ÷ Total Rooms`)
- Total Electricity Cost
- Average Electricity Consumption
- Electricity Cost per Student
- Water Consumption
- Water Consumption per Student
- Complaint Count
- Resolved Complaints
- Complaint Resolution Rate
- Average Resolution Time
- Mess Attendance Rate
- Estimated Food Wastage
- Visitor Count
- Average Daily Visitors
- Monthly Trends & Running Totals
- Hostel Rankings & Highest Consuming Hostel
- Top N Analysis

> Full measure definitions: `dax/Measures.md`

---

## Dashboards

The report contains six interactive pages:

| # | Page | Focus |
| - | ---- | ----- |
| 1 | Executive Dashboard | High-level KPIs across all operations |
| 2 | Hostel Operations | Occupancy, room allocation, demographics |
| 3 | Utilities Dashboard | Electricity and water consumption |
| 4 | Complaint Analytics | Complaint volume, categories, resolution |
| 5 | Mess Analytics | Meal attendance and food wastage |
| 6 | Security Dashboard | Visitor trends and peak hours |

**Key KPIs:** Total Students · Occupancy Rate · Electricity Cost · Water Consumption · Complaint Resolution Rate · Average Resolution Time · Mess Attendance Rate · Visitor Count

> Screenshots: `docs/Dashboard1.png`, `docs/Dashboard2.png`, …

---

## Advanced Features

- Bookmarks and navigation buttons
- Drill-down (hostel → floor → room) and drill-through pages
- Tooltip pages
- Sync slicers across pages
- Field parameters and dynamic titles
- Conditional formatting
- Top N analysis
- What-if parameters
- Custom theme and consistent visual design

---

## Tech Stack

- **Power BI Desktop** — modeling and visualization
- **Power Query** — ETL (cleaning, transformation, merging)
- **DAX** — measures and calculations
- **CSV** — synthetic source datasets

---

## Repository Structure

```
smart-hostel-analytics/
├── data/
│   ├── raw/
│   └── processed/
├── pbix/
│   └── Smart_Hostel_Analytics.pbix
├── sql/
├── docs/
│   ├── Database_Design.md
│   ├── ER_Diagram.png
│   ├── Data_Model.png
│   ├── Dashboard1.png
│   └── Dashboard2.png
├── dax/
│   └── Measures.md
├── README.md
└── LICENSE
```

---

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/smart-hostel-analytics.git
   ```
2. Open `pbix/Smart_Hostel_Analytics.pbix` in **Power BI Desktop**.
3. If prompted, update the data source path to point to `data/raw/`.
4. Refresh the data model.
5. Explore the six dashboard pages using the slicers and navigation buttons.

---

## Business Insights

A few representative questions the dashboard answers:

- Which hostel has the highest occupancy rate, and are any operating beyond capacity?
- Which hostel consumes the most electricity and water, and what is the cost per student?
- Which complaint category is most frequent, and how many high-priority complaints remain open?
- Which meal is skipped most often, and what is the estimated food wastage?
- What are the peak visitor hours across hostels?

> Add your own findings and screenshots here once the report is finalized.

---

## Future Scope

- Real-time data integration via scheduled refresh or direct query.
- Predictive analytics for utility consumption and complaint volume.
- Mobile-optimized report layout.
- Integration with fee management and academic systems.
- Automated alerting for unresolved high-priority complaints.

---

## Author

**Rohit Devadula**
[GitHub]([https://github.com/<your-username>](https://github.com/roh-eng)) · [LinkedIn](https://linkedin.com/in/<your-profile>https://www.linkedin.com/in/rohit-devadula-1b9b9a290/)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
