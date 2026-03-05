-- Script to create the "sensores" database and required tables
CREATE DATABASE IF NOT EXISTS sensores;
USE sensores;

-- Table for sensor data (voltages and currents)
CREATE TABLE IF NOT EXISTS datos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    voltaje1 FLOAT,
    voltaje2 FLOAT,
    corriente1 FLOAT,
    corriente2 FLOAT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for control state (ON/OFF)
CREATE TABLE IF NOT EXISTS control (
    id INT PRIMARY KEY,
    estado VARCHAR(5),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert initial record for control
INSERT INTO control (id, estado) VALUES (1, 'OFF')
ON DUPLICATE KEY UPDATE estado = 'OFF';
