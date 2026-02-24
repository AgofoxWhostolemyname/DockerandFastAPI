import uuid
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database import DBUser, DBBoard, DBList, DBCard

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    assignee: Optional[str] = None
    status: Optional[str] = "To Do"

def get_user_id(db: Session, x_api_key: str):
    user = db.query(DBUser).filter(DBUser.api_key == x_api_key).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return user.id

def create_board(db: Session, x_api_key: str, board_name: str):
    user_id = get_user_id(db, x_api_key)
    board_id = str(uuid.uuid4())
    
    new_board = DBBoard(id=board_id, name=board_name, user_id=user_id)
    db.add(new_board)
    db.commit()
    return {"board_id": board_id, "message": "Board created successfully"}

def get_boards(db: Session, x_api_key: str):
    user_id = get_user_id(db, x_api_key)
    boards = db.query(DBBoard).filter(DBBoard.user_id == user_id).all()
    return {"boards": [{"id": b.id, "name": b.name} for b in boards]}

def create_list(db: Session, board_id: str, list_name: str, x_api_key: str):
    user_id = get_user_id(db, x_api_key)

    board = db.query(DBBoard).filter(DBBoard.id == board_id,
                                      DBBoard.user_id == user_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    list_id = str(uuid.uuid4())
    new_list = DBList(id=list_id, name=list_name, board_id=board_id)
    db.add(new_list)
    db.commit()
    return {"list_id": list_id, "message": "List created successfully"}

def create_card(db: Session, board_id: str, list_id:
                 str, card_data: CardCreate, x_api_key: str):
    user_id = get_user_id(db, x_api_key)
    
    target_list = db.query(DBList).join(DBBoard).filter(
        DBList.id == list_id, DBBoard.id == board_id, DBBoard.user_id == user_id
    ).first()
    
    if not target_list:
        raise HTTPException(status_code=404, detail="List or Board not found")
        
    card_id = str(uuid.uuid4())
    new_card = DBCard(
        id=card_id, 
        title=card_data.title, 
        description=card_data.description,
        assignee=card_data.assignee,
        status=card_data.status,
        list_id=list_id
    )
    db.add(new_card)
    db.commit()
    return {"card_id": card_id, "message": "Card created successfully"}

def get_cards(db: Session, board_id: str, list_id: str,
               status: str, assignee: str, x_api_key: str):
    user_id = get_user_id(db, x_api_key)
    target_list = db.query(DBList).join(DBBoard).filter(
        DBList.id == list_id, DBBoard.id == board_id, DBBoard.user_id == user_id
    ).first()
    
    if not target_list:
        raise HTTPException(status_code=404, detail="List or Board not found")
        
    query = db.query(DBCard).filter(DBCard.list_id == list_id)
    
    if status:
        query = query.filter(DBCard.status == status)
    if assignee:
        query = query.filter(DBCard.assignee == assignee)
        
    cards = query.all()
    return {"cards": [{"id": c.id, "title": c.title, "description": c.description,
                        "assignee": c.assignee, "status": c.status} for c in cards]}

def move_card(db: Session, board_id: str, card_id: str, new_list_id: str, x_api_key: str):
    user_id = get_user_id(db, x_api_key)
    
    card = db.query(DBCard).join(DBList).join(DBBoard).filter(
        DBCard.id == card_id, DBBoard.id == board_id, DBBoard.user_id == user_id
    ).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    new_list = db.query(DBList).join(DBBoard).filter(
        DBList.id == new_list_id, DBBoard.id == board_id, DBBoard.user_id == user_id
    ).first()
    
    if not new_list:
        raise HTTPException(status_code=404, detail="Target list not found")
        
    card.list_id = new_list_id
    db.commit()
    return {"message": "Card moved successfully"}