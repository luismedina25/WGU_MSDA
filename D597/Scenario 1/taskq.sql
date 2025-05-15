-- PATIENTS TABLE: Core patient information
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_id INT UNIQUE,
    name VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(5)
);

-- MEDICAL CONDITIONS TABLE
CREATE TABLE medical_conditions (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    medical_condition VARCHAR(100)
);

-- MEDICATIONS TABLE
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    medications VARCHAR(100)
);

-- ALLERGIES TABLE
CREATE TABLE allergies (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    allergies VARCHAR(50)
);

-- APPOINTMENTS TABLE
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    last_appointment_date DATE
);

-- FITNESS RECORDS TABLE: Device product data
CREATE TABLE fitness_records (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(25),
    device_type VARCHAR(50),
    model_name VARCHAR(100),
    color VARCHAR(50),
    selling_price NUMERIC(10,2),
    original_price NUMERIC(10,2),
    display VARCHAR(75),
    rating NUMERIC(3,1),
    strap_material VARCHAR(100),
    average_battery_life INT,
    reviews INT
);

CREATE TABLE trackers (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    fitness_record_id INT REFERENCES fitness_records(id)
);

CREATE TABLE medical_records (
	patient_id INT,
	name VARCHAR(75),
	date_of_birth TEXT,
	gender VARCHAR(10),
	medical_conditions VARCHAR(75),
	medications VARCHAR(100),
	allergies VARCHAR(50),
	last_appointment_date TEXT,
	tracker VARCHAR(75)
);

CREATE TABLE fitness_records_staging (
    "Brand Name" VARCHAR(25),
    "Device Type" VARCHAR(50),
    "Model Name" VARCHAR(100),
    "Color" VARCHAR(50),
    "Selling Price" NUMERIC(10,2),
    "Original Price" NUMERIC(10,2),
    "Display" VARCHAR(75),
    "Rating" NUMERIC(3,1),
    "Strap Material" VARCHAR(100),
    "Average Battery Life" INT,
    "Reviews" INT
);


INSERT INTO patients (patient_id, name, date_of_birth, gender)
SELECT DISTINCT
    patient_id,
    name,
    TO_DATE(date_of_birth, 'MM/DD/YYYY'),
    gender
FROM medical_records;

INSERT INTO medical_conditions (patient_id, medical_condition)
SELECT 
    patient_id,
    medical_conditions
FROM medical_records
WHERE medical_conditions IS NOT NULL AND medical_conditions <> '';

INSERT INTO medications (patient_id, medications)
SELECT 
    patient_id,
    medications
FROM medical_records
WHERE medications IS NOT NULL AND medications <> '';

INSERT INTO allergies (patient_id, allergies)
SELECT 
    patient_id,
    allergies
FROM medical_records
WHERE allergies IS NOT NULL AND allergies <> '';

INSERT INTO appointments (patient_id, last_appointment_date)
SELECT 
    patient_id,
    TO_DATE(last_appointment_date, 'MM/DD/YYYY')
FROM medical_records
WHERE last_appointment_date IS NOT NULL AND last_appointment_date <> '';

INSERT INTO fitness_records (
    brand_name, device_type, model_name, color,
    selling_price, original_price, display, rating,
    strap_material, average_battery_life, reviews
)
SELECT 
    "Brand Name",
    "Device Type",
    "Model Name",
    "Color",
    "Selling Price",
    "Original Price",
    "Display",
    "Rating",
    "Strap Material",
    "Average Battery Life",
    "Reviews"
FROM fitness_records_staging;

INSERT INTO trackers (patient_id, fitness_record_id)
SELECT 
    m.patient_id,
    f.id
FROM medical_records m
JOIN fitness_records f ON f.model_name = m.tracker;





-- Get patients health and device usuage
SELECT
	patients.name,
	patients.date_of_birth,
	mc.medical_condition,
	m.medications,
	a.allergies,
	appt.last_appointment_date,
	fit.brand_name || ' ' || fit.model_name AS device_model
FROM patients
LEFT JOIN medical_conditions AS mc ON patients.patient_id = mc.patient_id
LEFT JOIN medications AS m ON patients.patient_id = m.patient_id
LEFT JOIN allergies AS a ON patients.patient_id = a.patient_id
LEFT JOIN appointments AS appt ON patients.patient_id = appt.patient_id
LEFT JOIN trackers AS t ON patients.patient_id = t.patient_id
LEFT JOIN fitness_records AS fit ON t.fitness_record_id = fit.id
ORDER BY patients.name;


-- Count of patients using each tracker model
SELECT
	fit.model_name,
	COUNT(t.patient_id) AS user_count
FROM trackers AS t
JOIN fitness_records AS fit ON t.fitness_record_id = fit.id
GROUP BY fit.model_name
ORDER BY user_count DESC;



SELECT
	fit.brand_name,
	fit.model_name,
	COUNT(*) AS total_sales
FROM fitness_records AS fit
GROUP BY fit.brand_name, fit.model_name
ORDER BY total_sales DESC;



-- Find the device with low battery life
SELECT 
    brand_name,
    model_name,
    average_battery_life
FROM fitness_records
WHERE average_battery_life < 5
ORDER BY average_battery_life DESC;



-- Count of patients using each tracker model
SELECT
	fit.model_name,
	COUNT(t.patient_id) AS user_count
FROM trackers AS t
JOIN fitness_records AS fit ON t.fitness_record_id = fit.id
GROUP BY fit.model_name
ORDER BY user_count DESC;


CREATE INDEX idx_mc_patient_id ON medical_conditions(patient_id);
CREATE INDEX idx_meds_patient_id ON medications(patient_id);
CREATE INDEX idx_allergies_patient_id ON allergies(patient_id);
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_trackers_patient_id ON trackers(patient_id);
CREATE INDEX idx_trackers_fitness_id ON trackers(fitness_record_id);
CREATE INDEX idx_fitness_model_name ON fitness_records(model_name);
CREATE INDEX idx_fitness_battery ON fitness_records(average_battery_life);


SELECT
	fit.model_name,
	COUNT(t.patient_id) AS user_count
FROM trackers AS t
JOIN fitness_records AS fit ON t.fitness_record_id = fit.id
GROUP BY fit.model_name
ORDER BY user_count DESC;


