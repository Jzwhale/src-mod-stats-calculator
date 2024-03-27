# VARIABLES #################################################################################

examiner_name = "Awesome_Username"

#############################################################################################

import requests
from time import sleep
from math import floor
import re

try:
    examiner_id = requests.get(f"https://www.speedrun.com/api/v1/users/{examiner_name}").json()["data"]["id"]
except:
    print("ERROR: There is no user with this name!")
    exit()

# Starting link, for all verified runs examined by specified user, offset by 0
link = f"https://www.speedrun.com/api/v1/runs?examiner={examiner_id}&status=verified&orderby=verify-date&offset=0"

total_time = 0
run_count = 0
longest_run = 0

while True:

    result = requests.get(link)
    
    # This just assumes you've been rate limited. Might be another problem though (hopefully not..)
    if result.status_code != 200:
        print(f"RATE LIMITED! WAITING 30 SECONDS.")
        sleep(30)
        continue
    
    # Looping over the runs on this page
    info = result.json()
    for entry in info["data"]:
    
        # This block pretty much just skips over "N/A" runs
        run_should_be_considered = True
        for player in entry["players"]:
            if player["rel"] == "guest" and player["name"].upper() == "N/A":
                run_should_be_considered = False
                break
        if not run_should_be_considered: continue

        # Adds to the total time
        time = entry["times"]["realtime_t"]
        total_time += time

        # Assigns new longest run time
        if time > longest_run: 
            longest_run = time
            print(f"New Longest Run Found: {entry["weblink"]}")
        
        run_count += 1

    print("Calculating total time... {0:.2f} (Run #{1})".format(total_time, run_count))

    # Changes link to get next page, or stops if complete
    if info["pagination"]["size"] < 20:
        break
    else:
        for x in info["pagination"]["links"]:
            if x["rel"] == "next":
                link = x["uri"]
                break

    sleep(0.3)

    # Yields for 15 seconds every 1000 runs checked to avoid rate limits
    if int(re.search(r"\d+$", link).group()) % 1000 == 0 and run_count != 0:
        print("Resuming in 15 seconds... (avoiding rate limits)")
        sleep(15)

# STATS!!!!
hours = total_time / 3600

average_length = total_time / run_count
average_minutes = floor(average_length / 60)
average_seconds = floor(average_length % 60)

longest_minutes = floor(longest_run / 60)
longest_seconds = floor(longest_run % 60)

print()
print()
print(f"User: {examiner_name}")
print()
print(f"Hours: {floor(hours)}")
print(f"Minutes: {floor(total_time/60) % 60}")
print(f"Seconds: {floor(total_time % 60)}")
print()
print(f"Final Run Count: {run_count}")
print(f"Average Run Length: {average_minutes}m{average_seconds}s")
print(f"Longest Run: {longest_minutes}m{longest_seconds}s")
print()
print("How much money should you have received by now? ($15 per hour of video)")
print("${0:,.2f}".format(hours * 15))
print()