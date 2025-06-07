from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://iiot_data_base_spyu_user:mUYqkhHR7rEqa3j3bp98yeC8HmoKvWpi@dpg-d11oup3uibrs73ef4v0g-a/iiot_data_base_spyu"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()