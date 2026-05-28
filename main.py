from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

FUSO_BR = ZoneInfo("America/Sao_Paulo")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sensores/", response_model=schemas.SensorOut)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    db_sensor = db.query(models.Sensor).filter(models.Sensor.tag == sensor.tag).first()
    if db_sensor:
        raise HTTPException(status_code=400, detail="Sensor com essa tag já existe.")

    new_sensor = models.Sensor(
        tag=sensor.tag,
        tipo=sensor.tipo,
        range_lrv=sensor.range_lrv,
        range_urv=sensor.range_urv,
        unidade=sensor.unidade
    )
    db.add(new_sensor)
    db.commit()
    db.refresh(new_sensor)

    for leitura in sensor.leituras or []:
        new_leitura = models.Leitura(
            valor=leitura.valor,
            timestamp=leitura.timestamp or datetime.utcnow(),
            sensor_id=new_sensor.id
        )
        db.add(new_leitura)

    db.commit()
    db.refresh(new_sensor)

    return new_sensor

@app.get("/sensores/", response_model=List[schemas.SensorOut])
def list_sensores(db: Session = Depends(get_db)):
    sensores = db.query(models.Sensor).all()
    return sensores

@app.get("/leituras/{sensor_id}", response_model=List[schemas.LeituraOut])
def get_leituras(
    sensor_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Leitura).filter(models.Leitura.sensor_id == sensor_id)
    
    if start:
        query = query.filter(models.Leitura.timestamp >= start)
    if end:
        query = query.filter(models.Leitura.timestamp <= end)
    
    return query.all()

@app.post("/sensores/{sensor_id}/leituras", response_model=List[schemas.LeituraOut])
def add_leituras(sensor_id: int, dados: schemas.LeiturasInput, db: Session = Depends(get_db)):
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor não encontrado.")

    if len(dados.leituras) > 100:
        raise HTTPException(status_code=413, detail="Máximo de 100 leituras por requisição.")

    novas_leituras = []
    for leitura in dados.leituras:
        nova = models.Leitura(
            valor=leitura.valor,
            timestamp=leitura.timestamp or datetime.utcnow(),
            sensor_id=sensor.id
        )
        db.add(nova)
        novas_leituras.append(nova)

    db.commit()
    return novas_leituras


@app.get("/leituras/{sensor_id}/ultima", response_model=schemas.LeituraOut)
def get_ultima_leitura(sensor_id: int, db: Session = Depends(get_db)):
    # Faz a query filtrando pelo sensor e ordenando do mais recente para o mais antigo (desc)
    leitura = db.query(models.Leitura)\
                .filter(models.Leitura.sensor_id == sensor_id)\
                .order_by(desc(models.Leitura.timestamp))\
                .first()
    
    # Se não houver nenhuma leitura no banco para este sensor
    if not leitura:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para este sensor.")
        
    # Converte de UTC para o horário de Brasília
    if leitura.timestamp:
        if leitura.timestamp.tzinfo is None:
            leitura.timestamp = leitura.timestamp.replace(tzinfo=timezone.utc)
        leitura.timestamp = leitura.timestamp.astimezone(FUSO_BR)
        
    return leitura