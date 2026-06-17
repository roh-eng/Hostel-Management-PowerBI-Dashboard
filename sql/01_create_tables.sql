-- =============================================================
-- Smart Hostel Analytics - DDL (matches data/raw CSV layout)
-- Target: Microsoft SQL Server (T-SQL)
-- Create order respects foreign-key dependencies.
-- =============================================================

CREATE TABLE Hostels (
    HostelID    INT          NOT NULL PRIMARY KEY,
    HostelName  VARCHAR(100) NOT NULL,
    Capacity    INT          NOT NULL,
    HostelType  VARCHAR(10)  NOT NULL CHECK (HostelType IN ('Boys','Girls','Co-ed')),
    WardenName  VARCHAR(100) NULL
);

CREATE TABLE Rooms (
    RoomID     INT         NOT NULL PRIMARY KEY,
    HostelID   INT         NOT NULL,
    RoomNumber VARCHAR(10) NOT NULL,
    Floor      INT         NOT NULL,
    Capacity   INT         NOT NULL CHECK (Capacity > 0),
    CONSTRAINT FK_Rooms_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID)
);

CREATE TABLE DateDimension (
    [Date]      DATE        NOT NULL PRIMARY KEY,
    [Day]       INT         NOT NULL,
    [Month]     VARCHAR(10) NOT NULL,
    MonthNumber INT         NOT NULL,
    [Quarter]   VARCHAR(2)  NOT NULL,
    [Year]      INT         NOT NULL,
    Weekday     VARCHAR(10) NOT NULL,
    WeekNumber  INT         NOT NULL,
    IsWeekend   VARCHAR(3)  NOT NULL
);

CREATE TABLE Students (
    StudentID     INT          NOT NULL PRIMARY KEY,
    RollNumber    VARCHAR(20)  NOT NULL,
    FirstName     VARCHAR(50)  NOT NULL,
    LastName      VARCHAR(50)  NOT NULL,
    Gender        VARCHAR(10)  NOT NULL CHECK (Gender IN ('Male','Female')),
    DOB           DATE         NOT NULL,
    Department    VARCHAR(20)  NOT NULL,
    [Year]        INT          NOT NULL CHECK ([Year] BETWEEN 1 AND 4),
    Phone         VARCHAR(15)  NULL,
    Email         VARCHAR(100) NULL,
    HostelID      INT          NOT NULL,
    RoomID        INT          NOT NULL,
    AdmissionDate DATE         NOT NULL,
    CONSTRAINT FK_Students_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Students_Rooms   FOREIGN KEY (RoomID)   REFERENCES Rooms(RoomID)
);

CREATE TABLE Attendance (
    AttendanceID INT         NOT NULL PRIMARY KEY,
    StudentID    INT         NOT NULL,
    [Date]       DATE        NOT NULL,
    [Status]     VARCHAR(10) NOT NULL CHECK ([Status] IN ('Present','Absent','Leave')),
    CONSTRAINT FK_Att_Students FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    CONSTRAINT FK_Att_Date     FOREIGN KEY ([Date])    REFERENCES DateDimension([Date])
);

CREATE TABLE Complaints (
    ComplaintID    INT         NOT NULL PRIMARY KEY,
    StudentID      INT         NOT NULL,
    ComplaintDate  DATE        NOT NULL,
    Category       VARCHAR(20) NOT NULL,
    Priority       VARCHAR(10) NOT NULL CHECK (Priority IN ('High','Medium','Low')),
    [Status]       VARCHAR(15) NOT NULL CHECK ([Status] IN ('Open','In Progress','Closed')),
    ResolutionDays INT         NULL,
    CONSTRAINT FK_Comp_Students FOREIGN KEY (StudentID)     REFERENCES Students(StudentID),
    CONSTRAINT FK_Comp_Date     FOREIGN KEY (ComplaintDate) REFERENCES DateDimension([Date])
);

CREATE TABLE ElectricityUsage (
    UsageID       INT           NOT NULL PRIMARY KEY,
    HostelID      INT           NOT NULL,
    [Date]        DATE          NOT NULL,
    UnitsConsumed DECIMAL(10,2) NOT NULL CHECK (UnitsConsumed >= 0),
    CONSTRAINT FK_Elec_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Elec_Date    FOREIGN KEY ([Date])   REFERENCES DateDimension([Date])
);

CREATE TABLE WaterUsage (
    UsageID        INT           NOT NULL PRIMARY KEY,
    HostelID       INT           NOT NULL,
    [Date]         DATE          NOT NULL,
    LitersConsumed DECIMAL(12,1) NOT NULL CHECK (LitersConsumed >= 0),
    CONSTRAINT FK_Water_Hostels FOREIGN KEY (HostelID) REFERENCES Hostels(HostelID),
    CONSTRAINT FK_Water_Date    FOREIGN KEY ([Date])   REFERENCES DateDimension([Date])
);

CREATE TABLE Visitors (
    VisitorID   INT          NOT NULL PRIMARY KEY,
    StudentID   INT          NOT NULL,
    VisitorName VARCHAR(100) NOT NULL,
    Relation    VARCHAR(20)  NOT NULL,
    VisitDate   DATE         NOT NULL,
    CheckIn     VARCHAR(5)   NOT NULL,
    CheckOut    VARCHAR(5)   NOT NULL,
    CONSTRAINT FK_Vis_Students FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    CONSTRAINT FK_Vis_Date     FOREIGN KEY (VisitDate)  REFERENCES DateDimension([Date])
);

CREATE TABLE MessAttendance (
    MessID    INT         NOT NULL PRIMARY KEY,
    StudentID INT         NOT NULL,
    [Date]    DATE        NOT NULL,
    Meal      VARCHAR(10) NOT NULL CHECK (Meal IN ('Breakfast','Lunch','Dinner')),
    [Status]  VARCHAR(10) NOT NULL CHECK ([Status] IN ('Taken','Skipped')),
    CONSTRAINT FK_Mess_Students FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    CONSTRAINT FK_Mess_Date     FOREIGN KEY ([Date])    REFERENCES DateDimension([Date])
);
