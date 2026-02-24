import os
from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppass")
DB_HOST = os.getenv("DB_HOST", "localhost") 
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True)
    
    boards = relationship("DBBoard", back_populates="owner",
                           cascade="all, delete-orphan")

class DBBoard(Base):
    __tablename__ = "boards"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(String, ForeignKey("users.id"))
    
    owner = relationship("DBUser", back_populates="boards")
    lists = relationship("DBList", back_populates="board",
                          cascade="all, delete-orphan")

class DBList(Base):
    __tablename__ = "lists"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    board_id = Column(String, ForeignKey("boards.id"))
    
    board = relationship("DBBoard", back_populates="lists")
    cards = relationship("DBCard", back_populates="parent_list",
                          cascade="all, delete-orphan")

class DBCard(Base):
    __tablename__ = "cards"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    assignee = Column(String)
    status = Column(String)
    list_id = Column(String, ForeignKey("lists.id"))
    
    parent_list = relationship("DBList", back_populates="cards")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()