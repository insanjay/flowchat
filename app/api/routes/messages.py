from fastapi import UploadFile, File, Form
from fastapi import APIRouter, Depends
from app.models.message import MessageCreate
from app.database.connection import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.post("/send", response_model=dict)
# async def send_message(message: MessageCreate, db: Session = Depends(get_db)):
#     # db_message = MessageDB(**message.dict())
#     # db.add(db_message)
#     db.commit()
    # return {"status": "sent", "message_id": db_message.id}

# @router.get("/chat/{chat_id}")
# async def get_messages(chat_id: int, db: Session = Depends(get_db)):
    # messages = db.query(MessageDB).filter(MessageDB.chat_id == chat_id).all()
    # return {"messages": messages}

# @router.post("/send-file")
# async def send_file(
#     chat_id: int = Form(...),
#     sender_id: int = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)  # FIX: Proper dependency injection
# ):
#     # Save the file locally (for MVP)
#     file_location = f"files/{file.filename}"
#     with open(file_location, "wb") as buffer:
#         buffer.write(await file.read())

    # # Save message in DB
    # # db_message = MessageDB(
    #     content=file.filename,
    #     message_type="file",
    #     file_url=file_location,
    #     file_type=file.filename.split('.')[-1],
    #     chat_id=chat_id,
    #     sender_id=sender_id
    # )
    # # db.add(db_message)
    # db.commit()
    # return {"status": "success", "filename": file.filename}
