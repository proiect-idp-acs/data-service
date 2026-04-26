from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI(title="Tournament Data Service", description="Operațiuni CRUD cu PostgreSQL")

# Configurarea Bazei de Date
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tennis_admin:supersecretpassword@postgres_db:5432/tennis_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tabela Meciuri
class MatchDB(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    player1 = Column(String, index=True)
    player2 = Column(String, index=True)
    status = Column(String, default="Scheduled") # Scheduled, In_Progress, Completed
    score = Column(JSON, default={"sets": [0, 0], "games": [0, 0], "points": ["0", "0"]})
    winner = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

class MatchCreate(BaseModel):
    player1: str
    player2: str

class MatchUpdate(BaseModel):
    status: str
    score: dict
    winner: str = None

Instrumentator().instrument(app).expose(app)

# Crearea unui meci nou
@app.post("/api/data/matches")
def create_match(match: MatchCreate):
    db: Session = SessionLocal()
    new_match = MatchDB(player1=match.player1, player2=match.player2)
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    db.close()
    return new_match

# Extragerea tuturor meciurilor
@app.get("/api/data/matches")
def get_all_matches():
    db: Session = SessionLocal()
    matches = db.query(MatchDB).all()
    db.close()
    return matches

# Extragerea unui singur meci
@app.get("/api/data/matches/{match_id}")
def get_match(match_id: int):
    db: Session = SessionLocal()
    match = db.query(MatchDB).filter(MatchDB.id == match_id).first()
    db.close()
    if not match:
        raise HTTPException(status_code=404, detail="Meciul nu a fost găsit")
    return match

# Actualizarea unui meci (apelat de Match Service)
@app.put("/api/data/matches/{match_id}")
def update_match(match_id: int, match_update: MatchUpdate):
    db: Session = SessionLocal()
    db_match = db.query(MatchDB).filter(MatchDB.id == match_id).first()
    
    if not db_match:
        db.close()
        raise HTTPException(status_code=404, detail="Meciul nu a fost găsit")
        
    db_match.status = match_update.status
    db_match.score = match_update.score
    if match_update.winner:
        db_match.winner = match_update.winner
        
    db.commit()
    db.refresh(db_match)
    db.close()
    return db_match