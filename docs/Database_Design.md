# Smart Hostel Analytics – Database Design (Phase 2)

> **Project:** Smart Hostel Analytics – Business Intelligence Dashboard
> **Phase:** 2 – Database Design & Data Modeling
> **Author:** Data Architecture & BI Team
> **Status:** Approved for implementation
> **Target Platform:** Microsoft SQL Server (source) → Power BI (semantic model)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Approach & Architecture](#2-design-approach--architecture)
3. [List of Tables](#3-list-of-tables)
4. [Naming Conventions](#4-naming-conventions)
5. [Detailed Table & Column Definitions](#5-detailed-table--column-definitions)
6. [Primary Keys & Foreign Keys](#6-primary-keys--foreign-keys)
7. [Relationship Cardinalities](#7-relationship-cardinalities)
8. [Business Rules](#8-business-rules)
9. [Data Dictionary](#9-data-dictionary)
10. [Normalized (3NF) Database Design](#10-normalized-3nf-database-design)
11. [Star Schema Design for Power BI](#11-star-schema-design-for-power-bi)
12. [Entity Relationship Diagram (Text)](#12-entity-relationship-diagram-text)
13. [Assumptions & Constraints](#13-assumptions--constraints)
14. [SQL CREATE TABLE Statements](#14-sql-create-table-statements)
15. [Project Folder Structure](#15-project-folder-structure)
16. [Implementation Notes for Power BI](#16-implementation-notes-for-power-bi)

---

## 1. Overview

A university operates **multiple hostels** and requires a centralized Business Intelligence platform to monitor operations across seven domains:

| Domain | Business Question Answered |
|---|---|
| Hostel Occupancy | How full is each hostel/room? What is the vacancy trend? |
| Student Demographics | What is the gender / course / state-wise distribution of residents? |
| Electricity Consumption | Which hostels consume the most power? What is the cost trend? |
| Water Consumption | Where is water usage abnormal? Are there leaks? |
| Complaint Management | What is complaint volume, resolution time, and category mix? |
| Mess Attendance | What is daily meal participation and food-waste risk? |
| Visitor Analytics | Who visits, when, and for how long? Any security flags? |

This document defines the **source database (OLTP-style, normalized to 3NF)** and the **analytical model (star schema)** that Power BI will consume.

---

## 2. Design Approach & Architecture

We use a **two-layer architecture**, which is the industry standard for Power BI portfolio and production projects:

```
 ┌─────────────────────┐      ┌──────────────────────┐      ┌─────────────────────┐
 │   SOURCE / OLTP      │      │   ETL / TRANSFORM    │      │   SEMANTIC MODEL    │
 │  (3NF Normalized)    │ ───► │ (Power Query / SQL   │ ───► │  (Star Schema in    │
 │  SQL Server tables   │      │  views / staging)    │      │   Power BI)         │
 └─────────────────────┘      └──────────────────────┘      └─────────────────────┘
        Write-optimized              Cleansing/Conform            Read-optimized
```

- **Source layer (3NF):** Normalized relational tables that prevent redundancy and enforce integrity. This is where data is captured/maintained.
- **Semantic layer (Star Schema):** Denormalized **fact** and **dimension** tables optimized for slicing, DAX, and fast aggregation in Power BI's VertiPaq engine.

A dedicated **`DateDimension`** (role-playing date table) is shared across all facts — a non-negotiable best practice for time intelligence.

---

## 3. List of Tables

### 3.1 Source / Dimension Entities
| # | Table | Type | Grain |
|---|---|---|---|
| 1 | `Hostels` | Dimension | One row per hostel |
| 2 | `Rooms` | Dimension | One row per room |
| 3 | `Students` | Dimension | One row per enrolled student |
| 4 | `DateDimension` | Dimension | One row per calendar date |

### 3.2 Fact / Transaction Entities
| # | Table | Type | Grain |
|---|---|---|---|
| 5 | `Attendance` | Fact | One row per student per day (hostel presence) |
| 6 | `Complaints` | Fact | One row per complaint raised |
| 7 | `ElectricityUsage` | Fact | One row per hostel per meter-reading date |
| 8 | `WaterUsage` | Fact | One row per hostel per meter-reading date |
| 9 | `Visitors` | Fact | One row per visitor check-in event |
| 10 | `MessAttendance` | Fact | One row per student per meal per day |

> **Total: 10 tables** — 4 dimensions + 6 facts.

---

## 4. Naming Conventions

| Object | Convention | Example |
|---|---|---|
| Table names | `PascalCase`, plural for entities | `Students`, `ElectricityUsage` |
| Primary key | `<Entity>ID` (singular) | `StudentID`, `HostelID` |
| Foreign key | Same name as referenced PK | `HostelID` in `Rooms` |
| Surrogate/Date key | `DateKey` (integer `yyyymmdd`) | `20260617` |
| Boolean flags | `Is<State>` / `Has<State>` | `IsActive`, `IsBlacklisted` |
| Date columns | `<Event>Date` | `AdmissionDate`, `CheckInDate` |
| Datetime columns | `<Event>DateTime` | `CheckInDateTime` |
| Amount/money | `<Thing>Amount` / `<Thing>Cost` | `BillAmount`, `EnergyCost` |
| Measures (Power BI) | Spaced, business-friendly | `Total Energy Cost`, `Occupancy %` |
| Star schema tables | `Dim<Name>` / `Fact<Name>` | `DimStudent`, `FactElectricity` |

**General rules**
- No spaces or reserved words in physical SQL object names.
- Singular `ID` suffix for keys; consistent across all tables for natural relationship mapping.
- All dates stored as `DATE`/`DATETIME2`; never as text.
- Use `DECIMAL` for money/units (never `FLOAT`) to avoid rounding errors.

---

## 5. Detailed Table & Column Definitions

### 5.1 `Hostels` (Dimension)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `HostelID` | `INT` | No | PK | Unique hostel identifier |
| `HostelName` | `VARCHAR(100)` | No | | Hostel name (e.g., "Aravali Block A") |
| `HostelType` | `VARCHAR(20)` | No | | `Boys` / `Girls` / `Co-ed` |
| `TotalRooms` | `INT` | No | | Total rooms in the hostel |
| `TotalCapacity` | `INT` | No | | Max student capacity |
| `WardenName` | `VARCHAR(100)` | Yes | | Warden in charge |
| `ContactNumber` | `VARCHAR(15)` | Yes | | Hostel office contact |
| `Location` | `VARCHAR(150)` | Yes | | Campus block / address |
| `CommissionedDate` | `DATE` | Yes | | Date hostel became operational |
| `IsActive` | `BIT` | No | | 1 = operational, 0 = closed |

### 5.2 `Rooms` (Dimension)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `RoomID` | `INT` | No | PK | Unique room identifier |
| `HostelID` | `INT` | No | FK → Hostels | Hostel the room belongs to |
| `RoomNumber` | `VARCHAR(10)` | No | | Display room number (e.g., "A-204") |
| `RoomType` | `VARCHAR(20)` | No | | `Single` / `Double` / `Triple` / `Dorm` |
| `Capacity` | `INT` | No | | Max occupants for the room |
| `CurrentOccupancy` | `INT` | No | | Current number of residents |
| `Floor` | `INT` | Yes | | Floor number |
| `IsAvailable` | `BIT` | No | | 1 = has vacancy, 0 = full |

### 5.3 `Students` (Dimension)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `StudentID` | `INT` | No | PK | Unique student identifier |
| `FirstName` | `VARCHAR(50)` | No | | Student first name |
| `LastName` | `VARCHAR(50)` | Yes | | Student last name |
| `Gender` | `VARCHAR(10)` | No | | `Male` / `Female` / `Other` |
| `DateOfBirth` | `DATE` | No | | DOB (for age demographics) |
| `Course` | `VARCHAR(50)` | No | | Program enrolled (e.g., "B.Tech CSE") |
| `Department` | `VARCHAR(50)` | Yes | | Academic department |
| `YearOfStudy` | `TINYINT` | Yes | | 1–5 |
| `State` | `VARCHAR(50)` | Yes | | Home state (geo demographics) |
| `City` | `VARCHAR(50)` | Yes | | Home city |
| `Email` | `VARCHAR(100)` | Yes | | University email |
| `PhoneNumber` | `VARCHAR(15)` | Yes | | Contact number |
| `RoomID` | `INT` | Yes | FK → Rooms | Room currently allotted |
| `AdmissionDate` | `DATE` | No | | Hostel admission date |
| `IsActive` | `BIT` | No | | 1 = resident, 0 = checked out |

### 5.4 `DateDimension` (Dimension)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `DateKey` | `INT` | No | PK | Integer date `yyyymmdd` |
| `FullDate` | `DATE` | No | | Calendar date |
| `Day` | `TINYINT` | No | | Day of month (1–31) |
| `DayName` | `VARCHAR(10)` | No | | Monday … Sunday |
| `DayOfWeek` | `TINYINT` | No | | 1–7 |
| `WeekOfYear` | `TINYINT` | No | | ISO week number |
| `Month` | `TINYINT` | No | | 1–12 |
| `MonthName` | `VARCHAR(10)` | No | | January … December |
| `Quarter` | `TINYINT` | No | | 1–4 |
| `Year` | `SMALLINT` | No | | Calendar year |
| `IsWeekend` | `BIT` | No | | 1 = Sat/Sun |
| `AcademicYear` | `VARCHAR(9)` | Yes | | e.g., "2025-2026" |

### 5.5 `Attendance` (Fact)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `AttendanceID` | `BIGINT` | No | PK | Unique attendance record |
| `StudentID` | `INT` | No | FK → Students | Student |
| `HostelID` | `INT` | No | FK → Hostels | Hostel |
| `DateKey` | `INT` | No | FK → DateDimension | Date of record |
| `Status` | `VARCHAR(10)` | No | | `Present` / `Absent` / `OnLeave` |
| `CheckInTime` | `TIME` | Yes | | Night roll-call check-in |
| `Remarks` | `VARCHAR(200)` | Yes | | Optional notes |

### 5.6 `Complaints` (Fact)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `ComplaintID` | `BIGINT` | No | PK | Unique complaint identifier |
| `StudentID` | `INT` | No | FK → Students | Student who raised it |
| `HostelID` | `INT` | No | FK → Hostels | Hostel |
| `RoomID` | `INT` | Yes | FK → Rooms | Related room (if applicable) |
| `RaisedDateKey` | `INT` | No | FK → DateDimension | Date raised |
| `ResolvedDateKey` | `INT` | Yes | FK → DateDimension | Date resolved |
| `Category` | `VARCHAR(30)` | No | | `Electrical`/`Plumbing`/`Cleaning`/`Internet`/`Mess`/`Security`/`Other` |
| `Priority` | `VARCHAR(10)` | No | | `Low` / `Medium` / `High` / `Critical` |
| `Status` | `VARCHAR(15)` | No | | `Open` / `InProgress` / `Resolved` / `Closed` |
| `Description` | `VARCHAR(500)` | Yes | | Complaint text |
| `ResolutionDays` | `INT` | Yes | | Computed days to resolve |

### 5.7 `ElectricityUsage` (Fact)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `ElectricityID` | `BIGINT` | No | PK | Unique reading record |
| `HostelID` | `INT` | No | FK → Hostels | Hostel metered |
| `DateKey` | `INT` | No | FK → DateDimension | Reading date |
| `UnitsConsumed` | `DECIMAL(10,2)` | No | | kWh consumed in period |
| `RatePerUnit` | `DECIMAL(8,2)` | No | | Tariff per kWh |
| `EnergyCost` | `DECIMAL(12,2)` | No | | UnitsConsumed × RatePerUnit |
| `MeterReadingStart` | `DECIMAL(12,2)` | Yes | | Opening meter reading |
| `MeterReadingEnd` | `DECIMAL(12,2)` | Yes | | Closing meter reading |
| `BillingMonth` | `VARCHAR(7)` | Yes | | `YYYY-MM` |

### 5.8 `WaterUsage` (Fact)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `WaterID` | `BIGINT` | No | PK | Unique reading record |
| `HostelID` | `INT` | No | FK → Hostels | Hostel metered |
| `DateKey` | `INT` | No | FK → DateDimension | Reading date |
| `LitresConsumed` | `DECIMAL(12,2)` | No | | Litres consumed in period |
| `RatePerKilolitre` | `DECIMAL(8,2)` | No | | Tariff per 1000 L |
| `WaterCost` | `DECIMAL(12,2)` | No | | Cost for the period |
| `MeterReadingStart` | `DECIMAL(12,2)` | Yes | | Opening meter reading |
| `MeterReadingEnd` | `DECIMAL(12,2)` | Yes | | Closing meter reading |
| `BillingMonth` | `VARCHAR(7)` | Yes | | `YYYY-MM` |

### 5.9 `Visitors` (Fact)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `VisitorID` | `BIGINT` | No | PK | Unique visit event |
| `StudentID` | `INT` | No | FK → Students | Student being visited |
| `HostelID` | `INT` | No | FK → Hostels | Hostel visited |
| `DateKey` | `INT` | No | FK → DateDimension | Date of visit |
| `VisitorName` | `VARCHAR(100)` | No | | Name of visitor |
| `Relationship` | `VARCHAR(30)` | Yes | | `Parent`/`Sibling`/`Friend`/`Guardian`/`Other` |
| `CheckInDateTime` | `DATETIME2` | No | | Entry timestamp |
| `CheckOutDateTime` | `DATETIME2` | Yes | | Exit timestamp |
| `Purpose` | `VARCHAR(100)` | Yes | | Reason for visit |
| `IDProofType` | `VARCHAR(30)` | Yes | | `Aadhaar`/`License`/`PAN`/`Other` |
| `DurationMinutes` | `INT` | Yes | | Computed visit duration |

### 5.10 `MessAttendance` (Fact)
| Column | Data Type | Null | Key | Description |
|---|---|---|---|---|
| `MessAttendanceID` | `BIGINT` | No | PK | Unique meal-attendance record |
| `StudentID` | `INT` | No | FK → Students | Student |
| `HostelID` | `INT` | No | FK → Hostels | Hostel mess |
| `DateKey` | `INT` | No | FK → DateDimension | Meal date |
| `MealType` | `VARCHAR(15)` | No | | `Breakfast`/`Lunch`/`Snacks`/`Dinner` |
| `Attended` | `BIT` | No | | 1 = ate, 0 = skipped |
| `PlateCost` | `DECIMAL(8,2)` | Yes | | Per-plate subsidized cost |

---

## 6. Primary Keys & Foreign Keys

| Table | Primary Key | Foreign Keys |
|---|---|---|
| `Hostels` | `HostelID` | — |
| `Rooms` | `RoomID` | `HostelID` → `Hostels` |
| `Students` | `StudentID` | `RoomID` → `Rooms` |
| `DateDimension` | `DateKey` | — |
| `Attendance` | `AttendanceID` | `StudentID`, `HostelID`, `DateKey` |
| `Complaints` | `ComplaintID` | `StudentID`, `HostelID`, `RoomID`, `RaisedDateKey`, `ResolvedDateKey` |
| `ElectricityUsage` | `ElectricityID` | `HostelID`, `DateKey` |
| `WaterUsage` | `WaterID` | `HostelID`, `DateKey` |
| `Visitors` | `VisitorID` | `StudentID`, `HostelID`, `DateKey` |
| `MessAttendance` | `MessAttendanceID` | `StudentID`, `HostelID`, `DateKey` |

---

## 7. Relationship Cardinalities

| Parent (1) | Child (Many) | Cardinality | Power BI Filter Direction |
|---|---|---|---|
| `Hostels` | `Rooms` | One-to-Many | Single → |
| `Rooms` | `Students` | One-to-Many | Single → |
| `Hostels` | `Attendance` | One-to-Many | Single → |
| `Students` | `Attendance` | One-to-Many | Single → |
| `DateDimension` | `Attendance` | One-to-Many | Single → |
| `Students` | `Complaints` | One-to-Many | Single → |
| `Hostels` | `Complaints` | One-to-Many | Single → |
| `Rooms` | `Complaints` | One-to-Many | Single → |
| `DateDimension` | `Complaints` (RaisedDate) | One-to-Many (active) | Single → |
| `DateDimension` | `Complaints` (ResolvedDate) | One-to-Many (inactive) | via `USERELATIONSHIP` |
| `Hostels` | `ElectricityUsage` | One-to-Many | Single → |
| `DateDimension` | `ElectricityUsage` | One-to-Many | Single → |
| `Hostels` | `WaterUsage` | One-to-Many | Single → |
| `DateDimension` | `WaterUsage` | One-to-Many | Single → |
| `Students` | `Visitors` | One-to-Many | Single → |
| `Hostels` | `Visitors` | One-to-Many | Single → |
| `DateDimension` | `Visitors` | One-to-Many | Single → |
| `Students` | `MessAttendance` | One-to-Many | Single → |
| `Hostels` | `MessAttendance` | One-to-Many | Single → |
| `DateDimension` | `MessAttendance` | One-to-Many | Single → |

> **Rule:** All dimension-to-fact relationships use **single-direction** filtering for predictable DAX and performance. Bidirectional filters are avoided unless a specific many-to-many need is proven.

---

## 8. Business Rules

**Occupancy**
- `Rooms.CurrentOccupancy` must never exceed `Rooms.Capacity`.
- A room is `IsAvailable = 1` only when `CurrentOccupancy < Capacity`.
- `Hostels.TotalCapacity` must equal the sum of `Capacity` of its rooms.

**Students**
- A student belongs to **at most one** room at a time (`RoomID`).
- `Students.Gender` must match `Hostels.HostelType` (e.g., a `Female` student cannot reside in a `Boys` hostel).
- `IsActive = 0` students retain history but are excluded from current occupancy.

**Attendance**
- One attendance record per student per day (`StudentID` + `DateKey` unique).
- `Status` of `OnLeave` requires an approved leave (out of scope, but flagged).

**Complaints**
- `ResolvedDateKey` must be `>=` `RaisedDateKey`.
- `Status = Resolved/Closed` requires a non-null `ResolvedDateKey`.
- `ResolutionDays = ResolvedDate − RaisedDate`; null while open.
- `Critical` complaints target SLA of ≤ 1 day (used for KPI alerting).

**Electricity & Water**
- `MeterReadingEnd >= MeterReadingStart`.
- `UnitsConsumed`/`LitresConsumed` must be `>= 0`.
- Cost columns are derived: `EnergyCost = UnitsConsumed × RatePerUnit`.
- One reading per hostel per billing date.

**Visitors**
- `CheckOutDateTime` must be `>= CheckInDateTime`.
- `DurationMinutes` is derived from check-in/out.
- Visits to inactive students are not permitted.

**Mess Attendance**
- One record per student per meal per day (`StudentID` + `DateKey` + `MealType` unique).
- `Attended = 0` is recorded explicitly (needed for food-waste/no-show analytics).

**Date Dimension**
- Must be **contiguous** (no gaps) and span the full reporting range.
- Marked as the official Date table in Power BI.

---

## 9. Data Dictionary

| Table | Column | Type | Allowed Values / Format | Business Meaning |
|---|---|---|---|---|
| Hostels | HostelType | VARCHAR(20) | Boys, Girls, Co-ed | Gender designation of hostel |
| Hostels | IsActive | BIT | 0,1 | Operational status |
| Rooms | RoomType | VARCHAR(20) | Single, Double, Triple, Dorm | Room configuration |
| Rooms | CurrentOccupancy | INT | 0 ≤ x ≤ Capacity | Live resident count |
| Students | Gender | VARCHAR(10) | Male, Female, Other | Demographic dimension |
| Students | YearOfStudy | TINYINT | 1–5 | Academic year |
| Students | State | VARCHAR(50) | Indian states | Geo-demographic |
| DateDimension | DateKey | INT | yyyymmdd | Surrogate date key |
| DateDimension | IsWeekend | BIT | 0,1 | Weekend flag |
| Attendance | Status | VARCHAR(10) | Present, Absent, OnLeave | Nightly presence |
| Complaints | Category | VARCHAR(30) | Electrical, Plumbing, Cleaning, Internet, Mess, Security, Other | Complaint type |
| Complaints | Priority | VARCHAR(10) | Low, Medium, High, Critical | Urgency |
| Complaints | Status | VARCHAR(15) | Open, InProgress, Resolved, Closed | Lifecycle state |
| ElectricityUsage | UnitsConsumed | DECIMAL(10,2) | ≥ 0 | kWh used |
| ElectricityUsage | EnergyCost | DECIMAL(12,2) | ≥ 0 | Billed amount (INR) |
| WaterUsage | LitresConsumed | DECIMAL(12,2) | ≥ 0 | Litres used |
| WaterUsage | WaterCost | DECIMAL(12,2) | ≥ 0 | Billed amount (INR) |
| Visitors | Relationship | VARCHAR(30) | Parent, Sibling, Friend, Guardian, Other | Visitor link |
| Visitors | DurationMinutes | INT | ≥ 0 | Visit length |
| MessAttendance | MealType | VARCHAR(15) | Breakfast, Lunch, Snacks, Dinner | Meal slot |
| MessAttendance | Attended | BIT | 0,1 | Meal participation |

---

## 10. Normalized (3NF) Database Design

The source schema satisfies the first three normal forms:

- **1NF** — All columns are atomic; no repeating groups or multi-valued cells (e.g., visitor events are individual rows, not a comma list).
- **2NF** — All non-key attributes depend on the **whole** primary key. Fact tables use single-column surrogate PKs, so partial dependency is structurally impossible.
- **3NF** — No transitive dependencies. Descriptive attributes live in their owning entity:
  - `HostelName`, `WardenName` live in `Hostels`, **not** repeated in `Rooms`/facts.
  - `Course`, `State` live in `Students`, not duplicated in `Attendance`/`MessAttendance`.
  - `RatePerUnit` is stored per reading (it is a transactional attribute that varies over time), while stable descriptors are referenced via FK.

**Hierarchy:** `Hostels` → `Rooms` → `Students` forms a clean parent-child chain, eliminating redundancy and update anomalies.

---

## 11. Star Schema Design for Power BI

For analytics, the 3NF model is reshaped into **conformed dimensions** and **fact tables**. Power BI's VertiPaq engine performs best with a star (not snowflake) layout.

### 11.1 Dimensions
| Dimension | Source | Notes |
|---|---|---|
| `DimDate` | `DateDimension` | Marked as Date table; drives all time intelligence |
| `DimStudent` | `Students` | Includes derived `AgeBand`, `FullName` |
| `DimHostel` | `Hostels` | One conformed hostel dimension |
| `DimRoom` | `Rooms` | Optionally folded into `DimHostel` attributes if room grain not needed |

### 11.2 Facts
| Fact | Source | Measures |
|---|---|---|
| `FactAttendance` | `Attendance` | Attendance %, Present Count, Absent Count |
| `FactComplaints` | `Complaints` | Complaint Count, Avg Resolution Days, Open Complaints |
| `FactElectricity` | `ElectricityUsage` | Total Units, Total Energy Cost, Cost/Student |
| `FactWater` | `WaterUsage` | Total Litres, Total Water Cost |
| `FactVisitors` | `Visitors` | Visitor Count, Avg Visit Duration |
| `FactMess` | `MessAttendance` | Meals Served, Mess Attendance %, Plate Cost |

### 11.3 Star Schema Diagram (Text)

```
                          ┌──────────────┐
                          │   DimDate    │
                          └──────┬───────┘
                                 │ (shared across all facts)
       ┌──────────────┐         │          ┌──────────────┐
       │  DimStudent  │◄────────┼─────────►│  DimHostel   │
       └──────┬───────┘         │          └──────┬───────┘
              │      ┌──────────┴──────────┐      │
              │      │                      │      │
        ┌─────▼──────▼──┐  ┌────────────┐  ┌▼──────▼──────┐
        │ FactAttendance│  │FactComplaints│ │FactElectricity│
        └───────────────┘  └────────────┘  └──────────────┘
        ┌───────────────┐  ┌────────────┐  ┌──────────────┐
        │  FactVisitors │  │  FactMess   │ │  FactWater   │
        └───────────────┘  └────────────┘  └──────────────┘

   All Fact* tables connect to DimDate, DimHostel, and (where applicable) DimStudent.
```

### 11.4 Sample DAX Measures
```DAX
Total Energy Cost = SUM ( FactElectricity[EnergyCost] )

Occupancy % =
DIVIDE (
    SUM ( DimRoom[CurrentOccupancy] ),
    SUM ( DimRoom[Capacity] )
)

Attendance % =
DIVIDE (
    CALCULATE ( COUNTROWS ( FactAttendance ), FactAttendance[Status] = "Present" ),
    COUNTROWS ( FactAttendance )
)

Avg Complaint Resolution (Days) =
AVERAGEX (
    FILTER ( FactComplaints, NOT ISBLANK ( FactComplaints[ResolutionDays] ) ),
    FactComplaints[ResolutionDays]
)

Cost per Student =
DIVIDE ( [Total Energy Cost], DISTINCTCOUNT ( FactAttendance[StudentID] ) )
```

---

## 12. Entity Relationship Diagram (Text)

```
HOSTELS (HostelID PK)
   │ 1
   │
   ├──< ROOMS (RoomID PK, HostelID FK)
   │        │ 1
   │        │
   │        └──< STUDENTS (StudentID PK, RoomID FK)
   │                  │ 1
   │                  │
   │   ┌──────────────┼───────────────┬────────────────┐
   │   │              │               │                │
   │   v              v               v                v
   │  ATTENDANCE   COMPLAINTS      VISITORS        MESSATTENDANCE
   │  (StudentID,  (StudentID,     (StudentID,     (StudentID,
   │   HostelID,    HostelID,       HostelID,       HostelID,
   │   DateKey)     RoomID,         DateKey)        DateKey)
   │               RaisedDateKey,
   │               ResolvedDateKey)
   │
   ├──< ELECTRICITYUSAGE (HostelID FK, DateKey FK)
   │
   └──< WATERUSAGE (HostelID FK, DateKey FK)


DATEDIMENSION (DateKey PK)
   │ 1
   └──< ATTENDANCE, COMPLAINTS, ELECTRICITYUSAGE,
        WATERUSAGE, VISITORS, MESSATTENDANCE

Legend:  PK = Primary Key   FK = Foreign Key
         1 ──< Many   (one-to-many relationship)
```

---

## 13. Assumptions & Constraints

**Assumptions**
1. A student resides in exactly one room at any time; historical room changes are out of Phase 2 scope (no SCD Type 2 yet).
2. Electricity and water are metered **per hostel**, not per room.
3. Meter readings are captured on a regular (e.g., monthly) cadence.
4. Mess subscription is universal; non-attendance is still recorded.
5. Visitor identity verification happens at the gate; one record per visit.
6. Currency is INR; all costs are pre-tax operational figures.
7. The reporting window is the current and previous academic year.

**Constraints**
1. Referential integrity enforced via `FOREIGN KEY` constraints in SQL Server.
2. `CHECK` constraints enforce enumerated values and non-negative measures.
3. `DateDimension` must be pre-populated and gap-free before fact loads.
4. Power BI relationships are single-direction; the date table is explicitly marked.
5. No personally identifiable visitor ID numbers are stored (only ID **type**) for privacy compliance.
6. Decimal precision fixed to avoid floating-point cost errors.

---

## 14. SQL CREATE TABLE Statements

```sql
-- =============================================================
-- Smart Hostel Analytics – Source Schema (SQL Server / T-SQL)
-- Create order respects FK dependencies.
-- =============================================================

-- 1. HOSTELS -------------------------------------------------
CREATE TABLE Hostels (
    HostelID         INT            NOT NULL PRIMARY KEY,
    HostelName       VARCHAR(100)   NOT NULL,
    HostelType       VARCHAR(20)    NOT NULL
        CONSTRAINT CK_Hostels_Type CHECK (HostelType IN ('Boys','Girls','Co-ed')),
    TotalRooms       INT            NOT NULL CHECK (TotalRooms >= 0),
    TotalCapacity    INT            NOT NULL CHECK (TotalCapacity >= 0),
    WardenName       VARCHAR(100)   NULL,
    ContactNumber    VARCHAR(15)    NULL,
    Location         VARCHAR(150)   NULL,
    CommissionedDate DATE           NULL,
    IsActive         BIT            NOT NULL DEFAULT 1
);

-- 2. DATE DIMENSION ------------------------------------------
CREATE TABLE DateDimension (
    DateKey       INT          NOT NULL PRIMARY KEY,   -- yyyymmdd
    FullDate      DATE         NOT NULL,
    [Day]         TINYINT      NOT NULL,
    DayName       VARCHAR(10)  NOT NULL,
    DayOfWeek     TINYINT      NOT NULL,
    WeekOfYear    TINYINT      NOT NULL,
    [Month]       TINYINT      NOT NULL,
    MonthName     VARCHAR(10)  NOT NULL,
    [Quarter]     TINYINT      NOT NULL,
    [Year]        SMALLINT     NOT NULL,
    IsWeekend     BIT          NOT NULL,
    AcademicYear  VARCHAR(9)   NULL
);

-- 3. ROOMS ---------------------------------------------------
CREATE TABLE Rooms (
    RoomID           INT          NOT NULL PRIMARY KEY,
    HostelID         INT          NOT NULL,
    RoomNumber       VARCHAR(10)  NOT NULL,
    RoomType         VARCHAR(20)  NOT NULL
        CONSTRAINT CK_Rooms_Type CHECK (RoomType IN ('Single','Double','Triple','Dorm')),
    Capacity         INT          NOT NULL CHECK (Capacity > 0),
    CurrentOccupancy INT          NOT NULL DEFAULT 0 CHECK (CurrentOccupancy >= 0),
    Floor            INT          NULL,
    IsAvailable      BIT          NOT NULL DEFAULT 1,
    CONSTRAINT FK_Rooms_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID),
    CONSTRAINT CK_Rooms_Occupancy CHECK (CurrentOccupancy <= Capacity)
);

-- 4. STUDENTS ------------------------------------------------
CREATE TABLE Students (
    StudentID     INT          NOT NULL PRIMARY KEY,
    FirstName     VARCHAR(50)  NOT NULL,
    LastName      VARCHAR(50)  NULL,
    Gender        VARCHAR(10)  NOT NULL
        CONSTRAINT CK_Students_Gender CHECK (Gender IN ('Male','Female','Other')),
    DateOfBirth   DATE         NOT NULL,
    Course        VARCHAR(50)  NOT NULL,
    Department    VARCHAR(50)  NULL,
    YearOfStudy   TINYINT      NULL CHECK (YearOfStudy BETWEEN 1 AND 5),
    [State]       VARCHAR(50)  NULL,
    City          VARCHAR(50)  NULL,
    Email         VARCHAR(100) NULL,
    PhoneNumber   VARCHAR(15)  NULL,
    RoomID        INT          NULL,
    AdmissionDate DATE         NOT NULL,
    IsActive      BIT          NOT NULL DEFAULT 1,
    CONSTRAINT FK_Students_Rooms FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID)
);

-- 5. ATTENDANCE ----------------------------------------------
CREATE TABLE Attendance (
    AttendanceID  BIGINT       NOT NULL PRIMARY KEY,
    StudentID     INT          NOT NULL,
    HostelID      INT          NOT NULL,
    DateKey       INT          NOT NULL,
    Status        VARCHAR(10)  NOT NULL
        CONSTRAINT CK_Attendance_Status CHECK (Status IN ('Present','Absent','OnLeave')),
    CheckInTime   TIME         NULL,
    Remarks       VARCHAR(200) NULL,
    CONSTRAINT FK_Att_Students FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    CONSTRAINT FK_Att_Hostels  FOREIGN KEY (HostelID)  REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Att_Date     FOREIGN KEY (DateKey)   REFERENCES DateDimension(DateKey),
    CONSTRAINT UQ_Att_StudentDay UNIQUE (StudentID, DateKey)
);

-- 6. COMPLAINTS ----------------------------------------------
CREATE TABLE Complaints (
    ComplaintID     BIGINT       NOT NULL PRIMARY KEY,
    StudentID       INT          NOT NULL,
    HostelID        INT          NOT NULL,
    RoomID          INT          NULL,
    RaisedDateKey   INT          NOT NULL,
    ResolvedDateKey INT          NULL,
    Category        VARCHAR(30)  NOT NULL
        CONSTRAINT CK_Comp_Category CHECK (Category IN
            ('Electrical','Plumbing','Cleaning','Internet','Mess','Security','Other')),
    Priority        VARCHAR(10)  NOT NULL
        CONSTRAINT CK_Comp_Priority CHECK (Priority IN ('Low','Medium','High','Critical')),
    Status          VARCHAR(15)  NOT NULL
        CONSTRAINT CK_Comp_Status CHECK (Status IN ('Open','InProgress','Resolved','Closed')),
    [Description]   VARCHAR(500) NULL,
    ResolutionDays  INT          NULL,
    CONSTRAINT FK_Comp_Students FOREIGN KEY (StudentID)       REFERENCES Students(StudentID),
    CONSTRAINT FK_Comp_Hostels  FOREIGN KEY (HostelID)        REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Comp_Rooms    FOREIGN KEY (RoomID)          REFERENCES Rooms(RoomID),
    CONSTRAINT FK_Comp_Raised   FOREIGN KEY (RaisedDateKey)   REFERENCES DateDimension(DateKey),
    CONSTRAINT FK_Comp_Resolved FOREIGN KEY (ResolvedDateKey) REFERENCES DateDimension(DateKey),
    CONSTRAINT CK_Comp_ResolveOrder CHECK (ResolvedDateKey IS NULL OR ResolvedDateKey >= RaisedDateKey)
);

-- 7. ELECTRICITY USAGE ---------------------------------------
CREATE TABLE ElectricityUsage (
    ElectricityID     BIGINT        NOT NULL PRIMARY KEY,
    HostelID          INT           NOT NULL,
    DateKey           INT           NOT NULL,
    UnitsConsumed     DECIMAL(10,2) NOT NULL CHECK (UnitsConsumed >= 0),
    RatePerUnit       DECIMAL(8,2)  NOT NULL CHECK (RatePerUnit >= 0),
    EnergyCost        DECIMAL(12,2) NOT NULL CHECK (EnergyCost >= 0),
    MeterReadingStart DECIMAL(12,2) NULL,
    MeterReadingEnd   DECIMAL(12,2) NULL,
    BillingMonth      VARCHAR(7)    NULL,
    CONSTRAINT FK_Elec_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Elec_Date    FOREIGN KEY (DateKey)  REFERENCES DateDimension(DateKey),
    CONSTRAINT CK_Elec_Meter CHECK (MeterReadingEnd IS NULL OR MeterReadingEnd >= MeterReadingStart)
);

-- 8. WATER USAGE ---------------------------------------------
CREATE TABLE WaterUsage (
    WaterID           BIGINT        NOT NULL PRIMARY KEY,
    HostelID          INT           NOT NULL,
    DateKey           INT           NOT NULL,
    LitresConsumed    DECIMAL(12,2) NOT NULL CHECK (LitresConsumed >= 0),
    RatePerKilolitre  DECIMAL(8,2)  NOT NULL CHECK (RatePerKilolitre >= 0),
    WaterCost         DECIMAL(12,2) NOT NULL CHECK (WaterCost >= 0),
    MeterReadingStart DECIMAL(12,2) NULL,
    MeterReadingEnd   DECIMAL(12,2) NULL,
    BillingMonth      VARCHAR(7)    NULL,
    CONSTRAINT FK_Water_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Water_Date    FOREIGN KEY (DateKey)  REFERENCES DateDimension(DateKey),
    CONSTRAINT CK_Water_Meter CHECK (MeterReadingEnd IS NULL OR MeterReadingEnd >= MeterReadingStart)
);

-- 9. VISITORS ------------------------------------------------
CREATE TABLE Visitors (
    VisitorID         BIGINT       NOT NULL PRIMARY KEY,
    StudentID         INT          NOT NULL,
    HostelID          INT          NOT NULL,
    DateKey           INT          NOT NULL,
    VisitorName       VARCHAR(100) NOT NULL,
    Relationship      VARCHAR(30)  NULL
        CONSTRAINT CK_Vis_Relationship CHECK (Relationship IN
            ('Parent','Sibling','Friend','Guardian','Other')),
    CheckInDateTime   DATETIME2    NOT NULL,
    CheckOutDateTime  DATETIME2    NULL,
    Purpose           VARCHAR(100) NULL,
    IDProofType       VARCHAR(30)  NULL,
    DurationMinutes   INT          NULL,
    CONSTRAINT FK_Vis_Students FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    CONSTRAINT FK_Vis_Hostels  FOREIGN KEY (HostelID)  REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Vis_Date     FOREIGN KEY (DateKey)   REFERENCES DateDimension(DateKey),
    CONSTRAINT CK_Vis_Time CHECK (CheckOutDateTime IS NULL OR CheckOutDateTime >= CheckInDateTime)
);

-- 10. MESS ATTENDANCE ----------------------------------------
CREATE TABLE MessAttendance (
    MessAttendanceID BIGINT       NOT NULL PRIMARY KEY,
    StudentID        INT          NOT NULL,
    HostelID         INT          NOT NULL,
    DateKey          INT          NOT NULL,
    MealType         VARCHAR(15)  NOT NULL
        CONSTRAINT CK_Mess_Meal CHECK (MealType IN ('Breakfast','Lunch','Snacks','Dinner')),
    Attended         BIT          NOT NULL DEFAULT 0,
    PlateCost        DECIMAL(8,2) NULL CHECK (PlateCost >= 0),
    CONSTRAINT FK_Mess_Students FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    CONSTRAINT FK_Mess_Hostels  FOREIGN KEY (HostelID)  REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Mess_Date     FOREIGN KEY (DateKey)   REFERENCES DateDimension(DateKey),
    CONSTRAINT UQ_Mess_StudentMealDay UNIQUE (StudentID, DateKey, MealType)
);
```

> **Indexing recommendation:** create non-clustered indexes on all FK columns
> (`HostelID`, `StudentID`, `DateKey`, `RoomID`) in fact tables to accelerate joins and Power BI refresh.

---

## 15. Project Folder Structure

```
smart-hostel-analytics/
│
├── README.md                       # Project overview, screenshots, KPIs
├── LICENSE
│
├── docs/
│   ├── Database_Design.md          # ◄ THIS DOCUMENT
│   ├── Project_Charter.md          # Phase 1 – scope & objectives
│   ├── Requirements.md             # Functional/BI requirements
│   ├── Data_Dictionary.md          # Extended data dictionary
│   └── images/
│       ├── erd.png
│       ├── star-schema.png
│       └── dashboard-preview.png
│
├── sql/
│   ├── 01_create_tables.sql        # DDL (Section 14)
│   ├── 02_constraints_indexes.sql  # Indexes & extra constraints
│   ├── 03_seed_date_dimension.sql  # Date table population
│   ├── 04_sample_data.sql          # Demo/seed data
│   └── views/
│       └── vw_fact_*.sql           # Reporting views for Power BI
│
├── data/
│   ├── raw/                        # Source CSV/Excel extracts
│   ├── processed/                  # Cleaned data
│   └── sample/                     # Small sample for demo
│
├── powerbi/
│   ├── SmartHostelAnalytics.pbix   # Power BI report file
│   ├── measures/
│   │   └── dax_measures.md         # Documented DAX library
│   └── themes/
│       └── hostel-theme.json       # Custom Power BI theme
│
├── etl/
│   ├── power_query/                # M scripts / query notes
│   └── notebooks/                  # Optional Python/SQL prep
│
└── assets/
    └── logo.png
```

---

## 16. Implementation Notes for Power BI

1. **Load order:** Dimensions first (`DateDimension`, `Hostels`, `Rooms`, `Students`), then facts.
2. **Mark as Date Table:** Set `DateDimension[FullDate]` as the date table to enable time intelligence (`DATEADD`, `SAMEPERIODLASTYEAR`).
3. **Relationships:** Build them on `*ID` and `DateKey` columns; keep single-direction filtering.
4. **Role-playing dates:** For `Complaints`, create the active relationship on `RaisedDateKey` and an inactive one on `ResolvedDateKey`, activated in measures via `USERELATIONSHIP`.
5. **Measures over columns:** Implement KPIs (Occupancy %, Attendance %, Cost/Student) as **DAX measures**, not calculated columns, for performance.
6. **Hide keys:** Hide all `*ID`/`DateKey` columns from report view; expose only business-friendly fields.
7. **Star, not snowflake:** Optionally fold `Rooms` attributes into the hostel/student context if room-grain analysis is not required, to keep the model star-shaped.
8. **Incremental refresh:** For large facts (`Attendance`, `MessAttendance`), configure incremental refresh on `DateKey`.

---

*End of Phase 2 – Database Design Document.*
