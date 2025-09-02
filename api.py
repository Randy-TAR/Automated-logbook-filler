from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from fill import run_daily_logbook
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")
if not DB_NAME:
    raise ValueError("MONGODB_DB not set in .env")

client = MongoClient(MONGODB_URL)
# database = client[DB_NAME] 
database = client.get_database(DB_NAME) # Put the database name in get_database(db_name)

users_collection = database['user']
# Pydantic model for user data scheme
class User(BaseModel):
    name: str
    doc_id: str
async def get_current_database():
    yield database # access the database object
    

def insert_user(user_data: User):
    user_dict = user_data.model_dump() # convert pydantic model to dictionary
    user_dict['_id'] = user_dict.pop("doc_id")  # Use doc_id as the _id
    try:
        result = users_collection.insert_one(user_dict)
        return str(result.inserted_id)
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=400, detail=f"User with doc_id '{user_data.doc_id}' already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Home page
@app.get("/")
def home():
    return {"text":"Logbook filling project"}

# endpoint to create user
@app.post("/users")
async def create_user(user_data: User):
    user_id = insert_user(user_data)
    return{"message":"User created successfully","user_id":str(user_id)}

# endpoint to get all users
@app.get("/users")
async def get_all_users(db: MongoClient = Depends(get_current_database)):
    users = users_collection.find()
    user_list = []
    for user in users:
        user['_id'] = str(user['_id']) # Convert objectID to string 
        user_list.append(user)
    return user_list

# Endpoint to delete a user by Id
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = users_collection.delete_one({"_id": user_id})
    if result.deleted_count == 1:
        return {"message":"User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
# End point to get all users and fill logbook with them
@app.get("/fill_logbook")
async def get_all_users_and_fill():
    users = users_collection.find()
    user_list = []
    responses = []
    for user in users:
        user['_id'] = str(user['_id']) # change the user_id(doc_id) into a string
        user_list.append(user)

        # Run the logbook filling function
        try:
            response = run_daily_logbook(user['_id'])
            responses.append({"doc_id": user['_id'], "response": response})
        except Exception as e:
            responses.append({"doc_id": user['_id'], "error": str(e)})
    return {"logbook_responses": responses}
    # return {"users": user_list, "logbook_responses": responses}

