-- Database initialization: create users and databases
-- Runs before schema.sql

-- IndiaLens app DB
CREATE USER indialens WITH PASSWORD 'indialens_dev';
CREATE DATABASE indialens OWNER indialens;
GRANT ALL PRIVILEGES ON DATABASE indialens TO indialens;

-- Airflow DB
CREATE USER airflow WITH PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

\c indialens
GRANT ALL ON SCHEMA public TO indialens;
