
from phi.agent import Agent 
# from phi.model.google import Gemini 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from phi.model.groq import Groq

import time
from datetime import datetime, time as dt_time
import os

from logbook_query import get_top_words # gettin the file with the data manipulation functions

from dotenv import load_dotenv

load_dotenv()

def run_daily_logbook(docs_id):
    user_api_key= os.getenv("GROQ_API_KEY")

    ai_model = Groq(id="llama-3.3-70b-versatile", api_key=user_api_key)

    SCOPES = ['https://www.googleapis.com/auth/documents'] # permission level to have access to read/write in the doc

    # loads and authenticates using your Service Account JSON file
    creds = service_account.Credentials.from_service_account_file(
        os.getenv("SERVICE_ACCOUNT_FILE"), scopes=SCOPES
    )
    # connect to the Google Docs API
    service = build('docs', 'v1', credentials=creds)
    # document_id = os.getenv("DOCUMENT_ID")
    document_id = docs_id

    logbook_agent = Agent(
        name="LogBook Filling Agent",
        # model=google_ai_model
        model=ai_model
    )
    # Function to get a short AI-generated summary
    def get_ai_summary(prompt):
        response = logbook_agent.run(prompt)
        return response.content if hasattr(response, "content") else str(response)

    # Date
    today_str = datetime.now().strftime("%m/%d/%y")

    # Time to run the code
    excecution_time = dt_time(hour=10, minute=0)  # 4:00 PM

    # Shared flag to stop loop
    stop_flag = False

    # function for getting data from the docs file
    def getting_doc_content(document_id):
        # Get the document content
        doc = service.documents().get(documentId=document_id).execute()

        # Access the text content
        doc_content = doc.get("body", {}).get("content", [])

        # Extracting all paragraphs and storing in lines
        lines = []
        for element in doc_content:
            paragraph = element.get("paragraph")
            if paragraph:
                line_text = ""
                for run in paragraph.get("elements", []):
                    text_run = run.get("textRun")
                    if text_run:
                        line_text += text_run.get("content", "")
                lines.append(line_text.strip())

        log_text = "\n".join(lines)
        return log_text

    # Raw Input variables
    task_assigned = ''
    accomplishment= ''
    learning= ''
    challenges= ''
    strategies= ''

    # checking if the time for the report to be updated has reached
    while True:
        time_now = datetime.now().time()  # current time
        if time_now >= excecution_time:
            logbook = getting_doc_content(document_id)
            # logbook = log_text
            results = get_top_words(logbook)
            if len(results) > 5 :
                print(results)
            else:
                task_assigned = ", ".join(results['Task Assigned'][:5])
                accomplishment = ", ".join(results['Accomplishments'][:5])
                learning = ", ".join(results['Learnings'][:5])
                challenges = ", ".join(results['Challenges Faced'][:5])
                strategies = ", ".join(results['Strategies to overcome Challenges'][:5])
            break
        else:
            print("waiting for schedul time")
            time.sleep(120)  # wait  seconds before checking again 1800

    # AI summaries
    task = get_ai_summary(f"Rewrite in less than 10 words, my task assigned based on the hint/keywords: {task_assigned}")
    accomplishments = get_ai_summary(f"Rewrite in less than 50 words, my task accomplishments based on the hint/keywords: {accomplishment}")
    learnings = get_ai_summary(f"Rewrite in less than 50 words my learning expirience based on the hint/keywords: {learning}")
    challenges = get_ai_summary(f"Rewrite in less than 50 words the challenges i faced based on the hint/keywords: {challenges}")
    strategies = get_ai_summary(f"Rewrite in less than 50 words the strategies i used to accomplish this challenges based on the hint/keywords: {strategies}")

    # Final report text
    report = (f"""Subject: Report for {today_str}
    Intern Daily Report
    Date: {today_str}
    Task Assigned: {task}
    Accomplishments: {accomplishments}
    Learnings: {learnings}
    Challenges Faced: {challenges}
    Strategies to overcome Challenges: {strategies}
    """)

    # # Get the document to find its current length
    # doc = service.documents().get(documentId=document_id).execute()
    # end_index = doc['body']['content'][-1]['endIndex'] - 1  # position before last newline

    # Insert into Google Doc at the end
    # requests = [
    #     {'insertText': {'location': {'index': end_index}, 'text': report}}
    # ]

    # Insert into Google Doc at the start
    requests = [
        {'insertText': {'location': {'index': 1}, 'text': report}}
    ]

    service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    return ("Daily report added to Google Doc!")
