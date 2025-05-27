from fastapi import FastAPI, Body, Request, HTTPException
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from pydantic import BaseModel


# dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")





app = FastAPI()



@app.post('/api/create')
async def create_db():
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

    return {'response' : 'database created'}



@app.get('/api/tickets')
async def get_all_tickets():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    tickets = [dict(zip(columns, row)) for row in rows]
    return {"tickets": tickets}




@app.get('/api/tickets/open')
async def get_open_tickets():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT * FROM tickets
                   WHERE tickets.estado = 'abierto'
                   """)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    tickets = [dict(zip(columns, row)) for row in rows]
    return {"tickets": tickets}






# @app.get('/recibe-dict')
# async def recibe_dict(request: Request):
#     params = dict(request.query_params)
#     return {"recibido": params}








@app.post('/api/tickets/post')
async def create_ticket(request: Request):
    # params = dict(request.query_params)
    try:
        params = await request.json()
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (paciente, doctor, sintomas, padecimiento, prescripcion, especialidad, urgencia) VALUES (%s, %s, %s, %s, %s, %s, %s);", 
            (params["paciente"],params["doctor"],params["sintomas"],params["padecimiento"],params["prescripcion"],params["especialidad"],params["urgencia"])
            )
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Ticket creado"}
    except Exception as e:
        return {"error": str(e)}
    


@app.put('/api/tickets/{ticket_id}')
async def update_ticket(ticket_id: int, request: Request):
    try:
        params = await request.json()
        allowed_fields = ["paciente", "doctor", "sintomas", "padecimiento", "prescripcion", "especialidad", "estado", "urgencia"]
        set_clauses = []
        values = []
        for field in allowed_fields:
            if field in params:
                set_clauses.append(f"{field} = %s")
                values.append(params[field])
        if not set_clauses:
            raise HTTPException(status_code=400, detail="No fields to update.")
        values.append(ticket_id)
        set_clause = ", ".join(set_clauses)
        query = f"UPDATE tickets SET {set_clause} WHERE id = %s"
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(query, values)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found.")
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Ticket actualizado"}
    except Exception as e:
        return {"error": str(e)}