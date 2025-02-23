from sqlalchemy import Column, Integer, String
from api.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)  # 🔹 Adicionado
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)