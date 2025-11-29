from fastapi import FastAPI, HTTPException, Path, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from fill import run_daily_logbook
import os
from dotenv import load_dotenv
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading
import time

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to fill logbook for all users
def fill_logbook_for_all_users():
    """Function to be called by scheduler to fill logbook for all users"""
    print(f"Scheduled task running at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
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
                print(f"Successfully filled logbook for user: {user['_id']}")
            except Exception as e:
                responses.append({"doc_id": user['_id'], "error": str(e)})
                print(f"Error filling logbook for user {user['_id']}: {str(e)}")
        
        print(f"Scheduled task completed. Responses: {responses}")
        return responses
    except Exception as e:
        print(f"Error in scheduled task: {str(e)}")
        return {"error": str(e)}

# Setup scheduler
scheduler = BackgroundScheduler()
# Schedule the job to run every day at 4:00 PM
scheduler.add_job(
    fill_logbook_for_all_users,
    trigger=CronTrigger(hour=16, minute=0),  # 4:00 PM
    id='daily_logbook_fill',
    name='Fill logbook for all users daily at 4 PM',
    replace_existing=True
)

# Start the scheduler when the application starts
@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("Scheduler started - Logbook will be filled daily at 4:00 PM")

# Stop the scheduler when the application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("Scheduler stopped")

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

# New endpoint to manually trigger the logbook filling
@app.post("/trigger_fill")
async def trigger_fill_now():
    """Manually trigger the logbook filling process"""
    responses = fill_logbook_for_all_users()
    return {"message": "Logbook filling triggered manually", "responses": responses}

# New endpoint to check scheduler status
@app.get("/scheduler/status")
async def get_scheduler_status():
    jobs = scheduler.get_jobs()
    job_info = []
    for job in jobs:
        job_info.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time)
        })
    return {
        "scheduler_running": scheduler.running,
        "scheduled_jobs": job_info
    }