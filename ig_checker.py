import json
import os

def extract_followers(path):
    with open(path, "r") as f:
        data = json.load(f)
    # followers.json is just a list
    return {entry["string_list_data"][0]["value"] for entry in data}

def extract_following(path):
    with open(path, "r") as f:
        data = json.load(f)
    # following.json is a dict with "relationships_following"
    return {entry["title"] for entry in data["relationships_following"]}

followers = extract_followers("followers_1.json")
following = extract_following("following.json")

not_following_back = following - followers

# Check if unfollowers.txt exists
output_file = "unfollowers.txt"

if os.path.exists(output_file):
    print(f"File '{output_file}' already exists. No new file created.")
else:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Not following you back:\n")
        for user in sorted(not_following_back):
            f.write(f"{user}\n")
    print(f"Saved {len(not_following_back)} unfollowers to '{output_file}'.")
