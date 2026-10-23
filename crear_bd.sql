-- Expedientes Digitales - Hospital de Diagnóstico (versión MariaDB/MySQL para phpMyAdmin)
CREATE DATABASE IF NOT EXISTS hospital_hdd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_hdd;
SET NAMES utf8mb4;

DROP TABLE IF EXISTS expediente;
DROP TABLE IF EXISTS documentos;
DROP TABLE IF EXISTS empleados;

CREATE TABLE empleados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    puesto VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    sucursal VARCHAR(50) NOT NULL,
    fecha_ingreso DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE expediente (
    empleado_id INT NOT NULL,
    documento_id INT NOT NULL,
    entregado TINYINT NOT NULL DEFAULT 0,
    PRIMARY KEY (empleado_id, documento_id),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (documento_id) REFERENCES documentos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO documentos (nombre) VALUES
  ('2 fotografías tamaño cédula'),
  ('Título de último grado académico y certificaciones'),
  ('Carnet de Junta de Vigilancia (según aplique)'),
  ('Curriculum vitae'),
  ('Solvencia de la Policía Nacional Civil'),
  ('Antecedentes penales'),
  ('2 recomendaciones personales'),
  ('2 recomendaciones laborales'),
  ('Fotocopia de DUI'),
  ('Fotocopia de NIT'),
  ('Fotocopia de ISSS'),
  ('Fotocopia de AFP');

INSERT INTO empleados (codigo, nombre, puesto, area, sucursal, fecha_ingreso) VALUES
  ('HDD-001', 'Camila Herrera', 'Médico general', 'Consulta externa', 'Escalón', '2024-02-12'),
  ('HDD-002', 'Andres Weil', 'Técnico de laboratorio', 'Laboratorio', 'Santa Elena', '2025-05-20'),
  ('HDD-003', 'Hector Calderon', 'Recepcionista', 'Admisión', 'Colonia Médica', '2026-01-08'),
  ('HDD-004', 'Herberth Barrera', 'Radiólogo', 'Imagenología', 'Escalón', '2023-09-01'),
  ('HDD-005', 'Daniel Gregg', 'Enfermero', 'Emergencias', 'Santa Elena', '2026-08-17'),
  ('HDD-006', 'Belen Diaz', 'Analista de talento humano', 'Talento Humano', 'Colonia Médica', '2025-11-03');

INSERT INTO expediente (empleado_id, documento_id, entregado) VALUES
  (1, 1, 1),
  (1, 2, 1),
  (1, 3, 1),
  (1, 4, 1),
  (1, 5, 1),
  (1, 6, 1),
  (1, 7, 1),
  (1, 8, 1),
  (1, 9, 1),
  (1, 10, 1),
  (1, 11, 1),
  (1, 12, 1),
  (2, 1, 1),
  (2, 2, 1),
  (2, 3, 1),
  (2, 4, 1),
  (2, 5, 1),
  (2, 6, 1),
  (2, 7, 1),
  (2, 8, 1),
  (2, 9, 1),
  (2, 10, 0),
  (2, 11, 0),
  (2, 12, 0),
  (3, 1, 1),
  (3, 2, 1),
  (3, 3, 1),
  (3, 4, 1),
  (3, 5, 0),
  (3, 6, 0),
  (3, 7, 0),
  (3, 8, 0),
  (3, 9, 0),
  (3, 10, 0),
  (3, 11, 0),
  (3, 12, 0),
  (4, 1, 1),
  (4, 2, 1),
  (4, 3, 1),
  (4, 4, 1),
  (4, 5, 1),
  (4, 6, 1),
  (4, 7, 1),
  (4, 8, 1),
  (4, 9, 1),
  (4, 10, 1),
  (4, 11, 1),
  (4, 12, 1),
  (5, 1, 0),
  (5, 2, 0),
  (5, 3, 0),
  (5, 4, 0),
  (5, 5, 0),
  (5, 6, 0),
  (5, 7, 0),
  (5, 8, 0),
  (5, 9, 0),
  (5, 10, 0),
  (5, 11, 0),
  (5, 12, 0),
  (6, 1, 1),
  (6, 2, 1),
  (6, 3, 1),
  (6, 4, 1),
  (6, 5, 1),
  (6, 6, 1),
  (6, 7, 1),
  (6, 8, 1),
  (6, 9, 1),
  (6, 10, 1),
  (6, 11, 1),
  (6, 12, 1);
