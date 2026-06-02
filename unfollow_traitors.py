import os
import json
import urllib.request
import urllib.error

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

def unfollow_user(username):
    url = f"https://api.github.com/user/following/{username}"
    print(f"Unfollowing {username}...")
    api_request("DELETE", url)

def main():
    followers_file = "followers.json"
    
    current_followers = get_all_followers()
    
    print(f"Total current followers: {len(current_followers)}")
    
    if not os.path.exists(followers_file):
        print(f"{followers_file} not found. This seems to be the first run.")
        print("Saving current followers and exiting.")
        with open(followers_file, "w") as f:
            json.dump(sorted(list(current_followers)), f, indent=2)
        return
        
    with open(followers_file, "r") as f:
        try:
            previous_followers = set(json.load(f))
        except json.JSONDecodeError:
            print("Error reading followers.json. Starting fresh.")
            previous_followers = set()
        
    print(f"Total previous followers: {len(previous_followers)}")
    
    unfollowed_us = previous_followers - current_followers
    
    if unfollowed_us:
        print(f"Found {len(unfollowed_us)} users who unfollowed us: {', '.join(unfollowed_us)}")
        for traitor in unfollowed_us:
            unfollow_user(traitor)
    else:
        print("No one unfollowed us. Everyone is loyal!")
        
    # Always save the updated followers list
    with open(followers_file, "w") as f:
        json.dump(sorted(list(current_followers)), f, indent=2)
    print("Updated followers.json")

if __name__ == "__main__":
    main()
