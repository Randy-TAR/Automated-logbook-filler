# from logbook_query import get_top_words

# results = get_top_words("logbook.txt")

# if len(results) > 5 :
#     print(results)
# else:
#     # print(results)
#     # for i in range(5):
#     #     print(results['Task Assigned'][i])
#     # top_5 = list(map(lambda x: x, results['Task Assigned'][:5]))
#     task_assigned = ", ".join(results['Task Assigned'][:5])
#     accomplishment = ", ".join(results['Accomplishments'][:5])
#     learning = ", ".join(results['Learnings'][:5])
#     challenges = ", ".join(results['Challenges Faced'][:5])
#     strategies = ", ".join(results['Strategies to overcome Challenges'][:5])
#     print(challenges)

import time
from datetime import datetime, time as dt_time

# Define the target time (11:00 AM in this example)
target_time = dt_time(hour=11, minute=0)

while True:
    now = datetime.now().time()  # current time as `time` object

    if now >= target_time:
        print("✅ It's 11:00 AM or later! Running the code...")

        # Place your scheduled task here
        print("Running your scheduled task...")

        break  # stop the loop once the task is done
    else:
        print(f"⏳ It's not 11:00 AM yet. Current time: {now.strftime('%H:%M:%S')}. Checking again in 30 seconds...")
        time.sleep(30)  # wait 30 seconds before checking again

