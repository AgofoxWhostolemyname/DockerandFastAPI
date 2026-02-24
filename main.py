from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

import user_operations as users_api
import board_operations as boards_api
from board_operations import CardCreate
from database import init_db, get_db

app = FastAPI(title="Mini Kanban API (PostgreSQL + Docker)")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "OK", "message": "Database connection works!"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.post("/create_user")
def api_register_user(db: Session = Depends(get_db)):
    return users_api.create_user(db)

@app.get("/boards")
def api_get_boards(x_api_key: str, db: Session = Depends(get_db)):
    return boards_api.get_boards(db, x_api_key)

@app.post("/boards")
def api_create_board(x_api_key: str, board_name: str, db: Session = Depends(get_db)):
    return boards_api.create_board(db, x_api_key, board_name)

@app.post("/boards/{board_id}/lists")
def api_create_list(board_id: str, list_name: str,
                     x_api_key: str, db: Session = Depends(get_db)):
    return boards_api.create_list(db, board_id, list_name, x_api_key)

@app.post("/boards/{board_id}/lists/{list_id}/cards")
def api_create_card(board_id: str, list_id: str, card_data: CardCreate,
                     x_api_key: str, db: Session = Depends(get_db)):
    return boards_api.create_card(db, board_id, list_id, card_data, x_api_key)

@app.get("/boards/{board_id}/lists/{list_id}/cards")
def api_get_cards(
    board_id: str, 
    list_id: str, 
    x_api_key: str, 
    status: Optional[str] = None, 
    assignee: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return boards_api.get_cards(db, board_id, list_id, status, assignee, x_api_key)

@app.put("/boards/{board_id}/cards/{card_id}/move")
def api_move_card(board_id: str, card_id: str, new_list_id: str,
                   x_api_key: str, db: Session = Depends(get_db)):
    return boards_api.move_card(db, board_id, card_id, new_list_id, x_api_key)