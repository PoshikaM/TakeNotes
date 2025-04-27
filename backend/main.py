from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Notes, User
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from utils import hash_password, verify_password
from auth import create_access_token, decode_token

from fastapi import Depends
from fastapi import Request


# Initialize app
app = FastAPI()

# CORS setup for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(
    MONGO_URL,
    tls=True,
    tlsAllowInvalidCertificates=True
)
db = client.notes_db
notes_collection = db.notes
users_collection = db.users

try:
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

# Note Routes
@app.get("/notes")
def get_notes():
    notes = list(notes_collection.find())
    for note in notes:
        note["_id"] = str(note["_id"])  # convert ObjectId to string
    return notes

@app.post("/notes")
def add_note(note: Notes):
    result = notes_collection.insert_one(note.dict())
    return {"id": str(result.inserted_id)}

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    result = notes_collection.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}

@app.put("/notes/{note_id}")
def update_note(note_id: str, updated_note: Notes):
    result = notes_collection.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {"title": updated_note.title, "content": updated_note.content}}
    )
    if result.modified_count == 1:
        return {"message": "Note updated successfully"}
    else:
        return {"message": "Note not found or no changes made"}

# def get_current_user(request: Request):
#     token = request.headers.get("Authorization")
#     if not token or not token.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Unauthorized")
#     try:
#         payload = decode_token(token[7:])  # remove "Bearer "
#         return payload["sub"]  # email
#     except:
#         raise HTTPException(status_code=401, detail="Invalid token")

# @app.get("/notes")
# def get_notes(current_user: str = Depends(get_current_user)):
#     notes = list(notes_collection.find())
#     for note in notes:
#         note["_id"] = str(note["_id"])  # convert ObjectId to string
#     return notes

# @app.post("/notes")
# def add_note(note: Notes, current_user: str = Depends(get_current_user)):
#     result = notes_collection.insert_one(note.dict())
#     return {"id": str(result.inserted_id)}

# @app.put("/notes/{note_id}")
# def update_note(note_id: str, updated_note: Notes, current_user: str = Depends(get_current_user)):
#     result = notes_collection.update_one(
#         {"_id": ObjectId(note_id)},
#         {"$set": {"title": updated_note.title, "content": updated_note.content}}
#     )
#     if result.modified_count == 1:
#         return {"message": "Note updated successfully"}
#     else:
#         return {"message": "Note not found or no changes made"}

# @app.delete("/notes/{note_id}")
# def delete_note(note_id: str, current_user: str = Depends(get_current_user)):
#     result = notes_collection.delete_one({"_id": ObjectId(note_id)})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Note not found")
#     return {"message": "Note deleted"}


# User Routes
@app.post("/signup")
def signup(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pwd = hash_password(user.password)
    users_collection.insert_one({"email": user.email, "password": hashed_pwd})
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: User):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token}