import pandas as pd 
import numpy as np 
from datetime import datetime
import re # regex
from collections import Counter

def get_top_words(file_name):
    # with open(file_name, "r") as f:
        # logbook = f.read()
    logbook = file_name
    # print(logbook)

    # Splitting per each day from where we find "Subject:" (start of new report)
    days = re.split(r"Subject:", logbook)
    days = [s.strip() for s in days if s.strip()] # remove empties

    # Prepare a list to hold structured data
    records = []

    for day in days:
        # Extracting the fields using their keywords (go to empty string if not found)
        subject = re.search(r"(Report.*)", day)
        date = re.search(r"Date:\s*(.*)", day)
        name = re.search(r"Name:\s*(.*)", day)
        task = re.search(r"Task Assigned:\s*\*?(.*)", day)
        accomplishments = re.search(r"Accomplishments:\s*\*?(.*)", day)
        learnings = re.search(r"Learnings:\s*\*?(.*)", day)
        challenges_faced = re.search(r"Challenges Faced:\s*\*?(.*)", day)
        challenges_overcome = re.search(r"Strategies to overcome Challenges:\s*\*?(.*)", day)

        # saving to the records list
        records.append({
            "Subject": subject.group(1).strip() if subject else "",
            "Date": date.group(1).strip() if date else "",
            "Name": name.group(1).strip() if name else "",
            "Task Assigned": task.group(1).strip() if task else "",
            "Accomplishments": accomplishments.group(1).strip() if accomplishments else "",
            "Learnings": learnings.group(1).strip() if learnings else "",
            "Challenges Faced": challenges_faced.group(1).strip() if challenges_faced else "",
            "Strategies to overcome Challenges": challenges_overcome.group(1).strip() if challenges_overcome else "",
        })

    logs = pd.DataFrame(records)

    # Converting Date  to datetime
    logs["Date"] = pd.to_datetime(logs["Date"], errors="coerce")
    # print(logs.head())
    # print(logs["Date"])
    # saving into a  dataframe

    logs_5 = logs.head(6)
    # print(logs_5)

    # Get today's date without time
    today = pd.to_datetime(datetime.today().date())
    # print(today)

    # Simple stopwords list
    stopwords = {"the", "and", "to", "of", "a", "in", "on", "for", "is", "with", "that", "this", "it"}

    # Define the columns you care about
    freq_words = [
        "Task Assigned",
        "Accomplishments",
        "Learnings",
        "Challenges Faced",
        "Strategies to overcome Challenges"
    ]

    # dictionary to save the top 5 words 
    top_words = {}

    if today in logs_5["Date"].dt.normalize().values:
        # print("✅ Report for today filled 🥳🥳🥳")
        # return "✅ Report for today filled 🥳🥳🥳"
        top_words =  "✅ Report for today filled 🥳🥳🥳"
    else:
        print("❌ No report for today 😠😠😠")
        # print(logs_5['Task Assigned'])

        for col in freq_words:
            if col in logs_5.columns:
                # Joinning all the rows of the column into one
                text = " ".join(logs[col].dropna().astype(str))
                
                # making text lowercase and remove punctuation/numbers
                text = re.sub(r"[^a-zA-Z\s]", " ", text).lower()
                
                # Splitting into words
                words = text.split()
                
                # Remove stopwords
                words = [w for w in words if w not in stopwords]
                
                # Counting the words
                word_counts = Counter(words)
                # unique_words = sorted(set(words))
                # print(unique_words)            

                # Show top 5 words
                # print(f"\n🔹 Top words in {col}:")
                top_5_words = [word for word, _ in word_counts.most_common(5)]  # top 5
                # print(top_5_words)

                top_words[col] = top_5_words  # saving in the dictionary 
                
    return top_words

# results = get_top_words("logbook.txt")
# print(results)