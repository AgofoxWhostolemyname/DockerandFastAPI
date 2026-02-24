import uuid
import secrets
from sqlalchemy.orm import Session
from database import DBUser

def create_user(db: Session):

    user_id = str(uuid.uuid4())
    api_key = secrets.token_hex(16) 
    

    new_user = DBUser(id=user_id, api_key=api_key)
    db.add(new_user)
    db.commit()
    
    return {"user_id": user_id, "api_key": api_key, "message": "User created successfully!"}