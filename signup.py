import asyncio
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="Simple Auth System")

# 1. MongoDB Connection Setup
# Replace with your actual MongoDB URI string if using Atlas
MONGO_DETAILS = os.getenv("MONGODB_URL")
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.auth_database
users_collection = db.get_collection("users")


# 2. Pydantic Schemas for Request Validation
class UserSignupSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


# 3. Password Hashing Helpers
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# 4. Signup Endpoint
@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignupSchema):
    # Check if user already exists by email
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )
    
    # Hash the password and structure user document
    hashed_pass = hash_password(user.password)
    user_document = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pass  # Never store raw text passwords
    }
    
    # Insert into MongoDB
    await users_collection.insert_one(user_document)
    return {"message": "User registered successfully!", "username": user.username}


# 5. Login Endpoint
@app.post("/login")
async def login(credentials: UserLoginSchema):
    # Find user by email
    user = await users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    # Verify the incoming password against the hashed database value
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    return {"message": "Login successful!", "username": user["username"]}