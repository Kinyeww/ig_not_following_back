import json
import os
import sys

# --- Helper: paths relative to script (parent directory) ---
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)

followers_path = os.path.join(parent_dir, "followers_1.json")
following_path = os.path.join(parent_dir, "following.json")

if not os.path.exists(followers_path):
    print(f"ERROR: followers file not found at {followers_path}")
    sys.exit(1)
if not os.path.exists(following_path):
    print(f"ERROR: following file not found at {following_path}")
    sys.exit(1)

# --- Utility to normalize a username ---
def norm(u):
    if not isinstance(u, str):
        return None
    return u.strip().lower()

# --- Flexible extractors that handle a few Instagram export shapes ---
def extract_followers(path):
    """Return set of usernames from followers file (robust to shapes)."""
    problems = []
    users = set()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # If file is a list of entries
    if isinstance(data, list):
        for i, entry in enumerate(data):
            # common shape: entry["string_list_data"][0]["value"]
            try:
                v = entry.get("string_list_data", [])
                if v and isinstance(v, list):
                    maybe = v[0].get("value") if isinstance(v[0], dict) else None
                    if maybe:
                        users.add(norm(maybe))
                        continue
            except Exception:
                pass

            # fallback: maybe entry has "title" or "value" at top level
            for key in ("value", "title", "username", "name"):
                maybe = entry.get(key)
                if maybe:
                    users.add(norm(maybe))
                    break
            else:
                problems.append(("followers_list_item", i, entry))

    # Some exports might be a dict with a key holding list
    elif isinstance(data, dict):
        # try common keys
        # If it's like {"relationships_followers": [...]}
        for candidate_key in ("relationships_followers", "followers", "connections", "list"):
            arr = data.get(candidate_key)
            if isinstance(arr, list):
                for i, entry in enumerate(arr):
                    # try same heuristics as above
                    got = None
                    if isinstance(entry, dict):
                        # try string_list_data -> value
                        v = entry.get("string_list_data")
                        if v and isinstance(v, list) and isinstance(v[0], dict):
                            got = v[0].get("value")
                        if not got:
                            for key in ("value", "title", "username", "name"):
                                maybe = entry.get(key)
                                if maybe:
                                    got = maybe
                                    break
                    if got:
                        users.add(norm(got))
                    else:
                        problems.append(("followers_dict_item", i, entry))
                break
        else:
            # try to parse any list-like values in the dict
            for k, v in data.items():
                if isinstance(v, list):
                    for i, entry in enumerate(v):
                        if isinstance(entry, dict):
                            for key in ("value", "title", "username", "name"):
                                if key in entry:
                                    users.add(norm(entry[key]))
                                    break
                        elif isinstance(entry, str):
                            users.add(norm(entry))
                # ignore non-list values
    else:
        raise ValueError("Unrecognized JSON root type in followers file")

    # remove None
    users.discard(None)
    return users, problems

def extract_following(path):
    """Return set of usernames from following.json (robust to shapes)."""
    problems = []
    users = set()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # If it's dict with "relationships_following" like your sample
    if isinstance(data, dict):
        arr = data.get("relationships_following")
        if isinstance(arr, list):
            for i, entry in enumerate(arr):
                if isinstance(entry, dict):
                    # try title first (your sample)
                    if "title" in entry and isinstance(entry["title"], str):
                        users.add(norm(entry["title"]))
                        continue
                    # fallback to string_list_data -> value
                    sld = entry.get("string_list_data")
                    if sld and isinstance(sld, list) and isinstance(sld[0], dict):
                        # sometimes exports put the username in href (extract from url)
                        val = sld[0].get("value") or sld[0].get("href")
                        if val:
                            # if href like https://www.instagram.com/_u/username
                            if val.startswith("http"):
                                uname = val.rstrip("/").split("/")[-1]
                                users.add(norm(uname))
                            else:
                                users.add(norm(val))
                            continue
                problems.append(("relationships_following_item", i, entry))
        else:
            # fallback: search for any list inside dict
            for k, v in data.items():
                if isinstance(v, list):
                    for i, entry in enumerate(v):
                        if isinstance(entry, dict):
                            for key in ("title", "value", "username", "name"):
                                if key in entry:
                                    users.add(norm(entry[key]))
                                    break
                        elif isinstance(entry, str):
                            users.add(norm(entry))
    elif isinstance(data, list):
        # handle list root fallback (treat similar to followers)
        for i, entry in enumerate(data):
            if isinstance(entry, dict):
                for key in ("title", "value", "username", "name"):
                    if key in entry:
                        users.add(norm(entry[key]))
                        break
            elif isinstance(entry, str):
                users.add(norm(entry))
            else:
                problems.append(("following_list_item", i, entry))
    else:
        raise ValueError("Unrecognized JSON root type in following file")

    users.discard(None)
    return users, problems

# --- Run extraction and report ---
followers, f_problems = extract_followers(followers_path)
following, fo_problems = extract_following(following_path)

print(f"Followers parsed: {len(followers)} (problems: {len(f_problems)})")
print(f"Following parsed: {len(following)} (problems: {len(fo_problems)})")

# If you want to inspect problems, write them to disk
if f_problems:
    with open(os.path.join(parent_dir, "followers_parse_problems.json"), "w", encoding="utf-8") as pf:
        json.dump(f_problems, pf, ensure_ascii=False, indent=2)
    print(f"Wrote followers parse problems to followers_parse_problems.json")

if fo_problems:
    with open(os.path.join(parent_dir, "following_parse_problems.json"), "w", encoding="utf-8") as pf:
        json.dump(fo_problems, pf, ensure_ascii=False, indent=2)
    print(f"Wrote following parse problems to following_parse_problems.json")

# --- Compute not-following-back set and write output (overwrite) ---
not_following_back = sorted(set(following) - set(followers))
out_file = os.path.join(parent_dir, "unfollowers.txt")
with open(out_file, "w", encoding="utf-8") as out:
    out.write("Not following you back:\n")
    for u in not_following_back:
        out.write(u + "\n")

print(f"Saved {len(not_following_back)} unfollowers to '{out_file}'")
