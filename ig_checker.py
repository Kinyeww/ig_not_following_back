import json

def extract_followers(path):
    with open(path, "r") as f:
        data = json.load(f)
    # followers.json is just a list
    return {entry["string_list_data"][0]["value"] for entry in data}

def extract_following(path):
    with open(path, "r") as f:
        data = json.load(f)
    # following.json is a dict with "relationships_following"
    return {entry["string_list_data"][0]["value"] for entry in data["relationships_following"]}

followers = extract_followers("followers_1.json")
following = extract_following("following.json")

not_following_back = following - followers

print("Not following you back:")
for user in not_following_back:
    print(user)
