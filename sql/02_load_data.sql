-- =============================================================
-- Smart Hostel Analytics - Bulk load from CSV
-- =============================================================
-- The fact tables contain ~738K rows total, so BULK INSERT from the
-- generated CSVs is the correct loading strategy (literal INSERTs for
-- 700K+ rows are impractical). Small dimensions can alternatively be
-- seeded with 03_seed_dimensions.sql.
--
-- 1. Run 01_create_tables.sql first.
-- 2. Adjust the path below to wherever data/raw lives on your machine.
-- 3. Load DateDimension and Hostels BEFORE the tables that reference them.
-- =============================================================

DECLARE @path NVARCHAR(260) = N'D:\smart-hostel-analytics\data\raw\';

-- Dimensions first (referenced by facts)
BULK INSERT Hostels        FROM 'D:\smart-hostel-analytics\data\raw\Hostels.csv'          WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT DateDimension  FROM 'D:\smart-hostel-analytics\data\raw\DateDimension.csv'    WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT Rooms          FROM 'D:\smart-hostel-analytics\data\raw\Rooms.csv'            WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT Students       FROM 'D:\smart-hostel-analytics\data\raw\Students.csv'         WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);

-- Facts
BULK INSERT Attendance       FROM 'D:\smart-hostel-analytics\data\raw\Attendance.csv'       WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT Complaints       FROM 'D:\smart-hostel-analytics\data\raw\Complaints.csv'       WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT ElectricityUsage FROM 'D:\smart-hostel-analytics\data\raw\ElectricityUsage.csv' WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT WaterUsage       FROM 'D:\smart-hostel-analytics\data\raw\WaterUsage.csv'       WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT Visitors         FROM 'D:\smart-hostel-analytics\data\raw\Visitors.csv'         WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);
BULK INSERT MessAttendance   FROM 'D:\smart-hostel-analytics\data\raw\MessAttendance.csv'   WITH (FIRSTROW=2, FIELDTERMINATOR=',', ROWTERMINATOR='0x0a', TABLOCK);

-- Quick row-count verification
SELECT 'Hostels' t, COUNT(*) n FROM Hostels
UNION ALL SELECT 'Rooms', COUNT(*) FROM Rooms
UNION ALL SELECT 'Students', COUNT(*) FROM Students
UNION ALL SELECT 'Attendance', COUNT(*) FROM Attendance
UNION ALL SELECT 'Complaints', COUNT(*) FROM Complaints
UNION ALL SELECT 'ElectricityUsage', COUNT(*) FROM ElectricityUsage
UNION ALL SELECT 'WaterUsage', COUNT(*) FROM WaterUsage
UNION ALL SELECT 'Visitors', COUNT(*) FROM Visitors
UNION ALL SELECT 'MessAttendance', COUNT(*) FROM MessAttendance
UNION ALL SELECT 'DateDimension', COUNT(*) FROM DateDimension;
