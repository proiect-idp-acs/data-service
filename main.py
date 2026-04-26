from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI(title="Tournament Data Service", description="Operațiuni CRUD cu PostgreSQL")

# Vom prelua URL-ul bazei de date din variabilele de mediu setate în docker-compose
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tennis_admin:supersecretpassword@postgres_db:5432/tennis_db")

Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    return {"message": "Tournament Data Service este activ!", "db_target": DATABASE_URL}

@app.get("/api/data/matches")
def get_all_matches():
    # Aici va veni logica de SQLAlchemy pentru a scoate meciurile din DB
    return [{"id": 1, "player1": "Nadal", "player2": "Federer", "status": "Scheduled"}]

# TODO: rute POST pentru a salva scorurile primite de la Match Service