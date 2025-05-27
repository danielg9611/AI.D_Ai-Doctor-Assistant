from fastapi import FastAPI, Body, Request
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv


# dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")

def create_tables():
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Drop tables if they exist
        cursor.execute("DROP TABLE IF EXISTS Ticket CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Paciente CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Doctor CASCADE;")

        cursor.execute("DROP TABLE IF EXISTS Tickets CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Pacientes CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS Doctores CASCADE;")

        # Create Paciente table
        cursor.execute("""
            CREATE TABLE Pacientes (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                mail VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)

        # Create Doctor table
        cursor.execute("""
            CREATE TABLE Doctores (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                especialidad VARCHAR(100) NOT NULL,
                mail VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)

        # Create Ticket table
        cursor.execute("""
            CREATE TABLE Tickets (
                id SERIAL PRIMARY KEY,
                fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                paciente INTEGER REFERENCES Pacientes(id) ON DELETE CASCADE,
                doctor INTEGER REFERENCES Doctores(id) ON DELETE CASCADE,
                sintomas TEXT,
                padecimiento VARCHAR(50),
                prescripcion TEXT,
                especialidad VARCHAR(100) NOT NULL,
                estado VARCHAR(10) NOT NULL DEFAULT 'abierto' CHECK (estado IN ('abierto', 'cerrado')),
                urgencia VARCHAR(50) NOT NULL CHECK (urgencia IN ('poco urgente', 'urgente', 'muy urgente'))
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()




def insert_dummy_data():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Insert dummy Paciente entries
    pacientes = [
        ("Juan", "Pérez", "juan.perez@example.com", "password123"),
        ("Ana", "García", "ana.garcia@example.com", "password456"),
        ("Luis", "Martínez", "luis.martinez@example.com", "password789"),
    ]
    for nombre, apellido, mail, password in pacientes:
        cursor.execute(
            "INSERT INTO Pacientes (nombre, apellido, mail, password) VALUES (%s, %s, %s, %s);",
            (nombre, apellido, mail, password)
        )

    # Insert dummy Doctor entries
    doctores = [
        ("Carlos", "Sánchez", "General", "carlos.sanchez@example.com", "docpass123"),
        ("María", "López", "General", "maria.lopez@example.com", "docpass456"),
        ("Pedro", "Ramírez", "General", "pedro.ramirez@example.com", "docpass789"),
    ]
    for nombre, apellido, especialidad, mail, password in doctores:
        cursor.execute(
            "INSERT INTO Doctores (nombre, apellido, especialidad, mail, password) VALUES (%s, %s, %s, %s, %s);",
            (nombre, apellido, especialidad, mail, password)
        )

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
    insert_dummy_data()



def create_ticket(paciente_id, doctor_id, sintomas, padecimiento, prescripcion, especialidad, urgencia):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Tickets (paciente, doctor, sintomas, padecimiento, prescripcion, especialidad, urgencia) VALUES (%s, %s, %s, %s, %s, %s, %s);",
        (paciente_id, doctor_id, sintomas, padecimiento, prescripcion, especialidad, urgencia)
    )

    conn.commit()
    cursor.close()
    conn.close()


create_ticket(
    paciente_id= 2,
    doctor_id= 1,
    sintomas= 'Vomitos, Diarrea',
    padecimiento= 'Virus',
    prescripcion= 'Pastillas cada 8h',
    especialidad= 'General',
    urgencia= 'poco urgente'
)

create_ticket(
    paciente_id= 1,
    doctor_id= 3,
    sintomas= 'Dolores de Cabeza',
    padecimiento= 'Migraña',
    prescripcion= 'Pastillas cada 8h',
    especialidad= 'General',
    urgencia= 'urgente'
)