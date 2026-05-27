from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Sensor(Base):
    __tablename__ = "sensores"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- CORREÇÃO PRINCIPAL AQUI ---
    # Adicionado o limite de 50 caracteres para a tag
    tag = Column(String(50), unique=True, index=True) 
    
    # Boa prática: limitar também os outros textos (ex: 50 e 20 caracteres)
    tipo = Column(String(50)) 
    range_lrv = Column(Float)
    range_urv = Column(Float)
    unidade = Column(String(20)) 

    leituras = relationship("Leitura", back_populates="sensor", cascade="all, delete")

class Leitura(Base):
    __tablename__ = "leituras"

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())  # Agora automático
    sensor_id = Column(Integer, ForeignKey("sensores.id"))

    sensor = relationship("Sensor", back_populates="leituras")