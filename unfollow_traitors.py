import os
import json
import urllib.request
import urllib.error
from datetime import datetime

TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set. Please set the USER_PAT secret.")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def api_request(method, url):
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in (204, 205):
                return None
            body = response.read()
            if body:
                return json.loads(body)
            return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for {url}")
        return None
    except Exception as e:
        print(f"Error: {e} for {url}")
        return None

def get_all_followers():
    followers = set()
    page = 1
    while True:
        url = f"https://api.github.com/user/followers?per_page=100&page={page}"
        print(f"Fetching followers page {page}...")
        try:
            req = urllib.request.Request(url, headers=HEADERS, method="GET")
            with urllib.request.urlopen(req) as response:
                body = response.read()
                data = json.loads(body)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason} for {url}")
            if e.code == 401:
                print("Unauthorized: Please check if your USER_PAT is valid and has the correct permissions.")
                exit(1)
            break
        except Exception as e:
            print(f"Error: {e} for {url}")
            break
            
        if not data:
            break
            
        for user in data:
            followers.add(user["login"])
            
        if len(data) < 100:
            break
        page += 1
        
    return followers

def get_all_following():
    following = set()
    page = 1
    while True:
        url = f"https://api.github.com/user/following?per_page=100&page={page}"
        print(f"Fetching following page {page}...")
        try:
            req = urllib.request.Request(url, headers=HEADERS, method="GET")
            with urllib.request.urlopen(req) as response:
                body = response.read()
                data = json.loads(body)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason} for {url}")
            if e.code == 401:
                print("Unauthorized: Please check if your USER_PAT is valid and has the correct permissions.")
                exit(1)
            break
        except Exception as e:
            print(f"Error: {e} for {url}")
            break
            
        if not data:
            break
            
        for user in data:
            following.add(user["login"])
            
        if len(data) < 100:
            break
        page += 1
        
    return following

def unfollow_user(username):
    url = f"https://api.github.com/user/following/{username}"
    print(f"Unfollowing {username}...")
    api_request("DELETE", url)

def follow_user(username):
    url = f"https://api.github.com/user/following/{username}"
    print(f"Following {username}...")
    api_request("PUT", url)

def main():
    followers_file = "followers.json"
    
    current_followers = get_all_followers()
    current_following = get_all_following()
    
    print(f"Total current followers: {len(current_followers)}")
    print(f"Total current following: {len(current_following)}")
    
    if not os.path.exists(followers_file):
        print(f"{followers_file} not found. This seems to be the first run.")
        print("Saving current followers and exiting.")
        with open(followers_file, "w") as f:
            json.dump(sorted(list(current_followers)), f, indent=2)
            
        non_followers = current_following - current_followers
        print(f"Found {len(non_followers)} users who don't follow back.")
        with open("non_followers.txt", "w") as f:
            for user in sorted(list(non_followers)):
                f.write(f"{user}\n")
        return
        
    with open(followers_file, "r") as f:
        try:
            previous_followers = set(json.load(f))
        except json.JSONDecodeError:
            print("Error reading followers.json. Starting fresh.")
            previous_followers = set()
        
    print(f"Total previous followers: {len(previous_followers)}")
    
    unfollowed_us = previous_followers - current_followers
    new_followers = current_followers - previous_followers
    
    known_traitors = set()
    if os.path.exists("traitors.txt"):
        with open("traitors.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("] ", 1)
                    if len(parts) == 2:
                        known_traitors.add(parts[1])
                        
    all_traitors = known_traitors.union(unfollowed_us)
    non_followers = (current_following - current_followers) - all_traitors
    
    print(f"Found {len(non_followers)} users who don't follow back.")
    with open("non_followers.txt", "w") as f:
        for user in sorted(list(non_followers)):
            f.write(f"{user}\n")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if unfollowed_us:
        print(f"Found {len(unfollowed_us)} users who unfollowed us: {', '.join(unfollowed_us)}")
        with open("traitors.txt", "a") as tf:
            for traitor in unfollowed_us:
                unfollow_user(traitor)
                tf.write(f"[{now}] {traitor}\n")
    else:
        print("No one unfollowed us. Everyone is loyal!")
        
    if new_followers:
        print(f"Found {len(new_followers)} new followers: {', '.join(new_followers)}")
        for friend in new_followers:
            follow_user(friend)
    else:
        print("No new followers.")
        
    # Always save the updated followers list
    with open(followers_file, "w") as f:
        json.dump(sorted(list(current_followers)), f, indent=2)
    print("Updated followers.json")

if __name__ == "__main__":
    main()
