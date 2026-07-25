import json
import os
import sys

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

def load_snapshot(directory):
    followers_path = os.path.join(directory, "followers_1.json")
    following_path = os.path.join(directory, "following.json")

    if not os.path.isdir(directory):
        print(f"ERROR: directory not found: {directory}")
        sys.exit(1)

    if not os.path.isfile(followers_path):
        print(f"ERROR: followers_1.json not found in: {directory}")
        sys.exit(1)

    if not os.path.isfile(following_path):
        print(f"ERROR: following.json not found in: {directory}")
        sys.exit(1)

    followers, followers_problems = extract_followers(followers_path)
    following, following_problems = extract_following(following_path)

    return (
        followers,
        following,
        followers_problems,
        following_problems,
    )

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
def write_username_file(path, title, usernames):
    with open(path, "w", encoding="utf-8") as out:
        out.write(f"{title}:\n")

        for username in usernames:
            out.write(username + "\n")


def write_problem_file(path, problems):
    if not problems:
        return

    with open(path, "w", encoding="utf-8") as out:
        json.dump(problems, out, ensure_ascii=False, indent=2)


def get_snapshot_directory(argument):
    script_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    # Absolute paths can be used directly.
    if os.path.isabs(argument):
        return argument

    # Relative folder names are searched beside ig_checker.py.
    return os.path.join(script_directory, argument)


def get_snapshot_name(directory):
    name = os.path.basename(os.path.normpath(directory))
    return name.replace(" ", "_")


def save_parse_problems(
    output_directory,
    snapshot_name,
    followers_problems,
    following_problems,
):
    if followers_problems:
        path = os.path.join(
            output_directory,
            f"{snapshot_name}_followers_parse_problems.json",
        )

        write_problem_file(path, followers_problems)
        print(f"Followers parse problems saved to: {path}")

    if following_problems:
        path = os.path.join(
            output_directory,
            f"{snapshot_name}_following_parse_problems.json",
        )

        write_problem_file(path, following_problems)
        print(f"Following parse problems saved to: {path}")


def run_single_snapshot(directory, output_directory):
    (
        followers,
        following,
        followers_problems,
        following_problems,
    ) = load_snapshot(directory)

    # Your original big unfollower list.
    not_following_back = sorted(
        following - followers
    )

    snapshot_name = get_snapshot_name(directory)

    output_path = os.path.join(
        output_directory,
        f"{snapshot_name}_unfollowers.txt",
    )

    write_username_file(
        output_path,
        "Not following you back",
        not_following_back,
    )

    save_parse_problems(
        output_directory,
        snapshot_name,
        followers_problems,
        following_problems,
    )

    print(f"Followers parsed: {len(followers)}")
    print(f"Following parsed: {len(following)}")
    print(
        f"Not following you back: "
        f"{len(not_following_back)}"
    )
    print(f"Saved to: {output_path}")


def run_comparison(
    old_directory,
    new_directory,
    output_directory,
):
    if os.path.abspath(old_directory) == os.path.abspath(
        new_directory
    ):
        print("ERROR: old and new directories are the same.")
        sys.exit(1)

    (
        old_followers,
        old_following,
        old_followers_problems,
        old_following_problems,
    ) = load_snapshot(old_directory)

    (
        new_followers,
        new_following,
        new_followers_problems,
        new_following_problems,
    ) = load_snapshot(new_directory)

    # Your original big unfollower list, using the newest data.
    not_following_back = sorted(
        new_following - new_followers
    )

    # Followed you before but are missing from the new export.
    unfollowed_by_others = sorted(
        old_followers - new_followers
    )

    # You followed them before but no longer follow them.
    unfollowed_by_me = sorted(
        old_following - new_following
    )

    old_name = get_snapshot_name(old_directory)
    new_name = get_snapshot_name(new_directory)

    unfollowers_path = os.path.join(
        output_directory,
        f"{new_name}_unfollowers.txt",
    )

    unfollowed_by_others_path = os.path.join(
        output_directory,
        (
            f"{old_name}_to_{new_name}_"
            "unfollowed_by_others.txt"
        ),
    )

    unfollowed_by_me_path = os.path.join(
        output_directory,
        (
            f"{old_name}_to_{new_name}_"
            "unfollowed_by_me.txt"
        ),
    )

    write_username_file(
        unfollowers_path,
        "Not following you back",
        not_following_back,
    )

    write_username_file(
        unfollowed_by_others_path,
        "Recently unfollowed by others",
        unfollowed_by_others,
    )

    write_username_file(
        unfollowed_by_me_path,
        "Recently unfollowed by you",
        unfollowed_by_me,
    )

    save_parse_problems(
        output_directory,
        old_name,
        old_followers_problems,
        old_following_problems,
    )

    save_parse_problems(
        output_directory,
        new_name,
        new_followers_problems,
        new_following_problems,
    )

    print(f"Old followers parsed: {len(old_followers)}")
    print(f"New followers parsed: {len(new_followers)}")
    print(f"Old following parsed: {len(old_following)}")
    print(f"New following parsed: {len(new_following)}")

    print()
    print(
        f"Not following you back: "
        f"{len(not_following_back)}"
    )
    print(
        f"Recently unfollowed by others: "
        f"{len(unfollowed_by_others)}"
    )
    print(
        f"Recently unfollowed by you: "
        f"{len(unfollowed_by_me)}"
    )

    print()
    print(f"Saved to: {unfollowers_path}")
    print(f"Saved to: {unfollowed_by_others_path}")
    print(f"Saved to: {unfollowed_by_me_path}")


def main():
    if len(sys.argv) not in (2, 3):
        script_name = os.path.basename(sys.argv[0])

        print("Usage:")
        print(
            f'  python3 {script_name} "<date directory>"'
        )
        print(
            f'  python3 {script_name} '
            '"<old directory>" "<new directory>"'
        )

        print()
        print("Examples:")
        print(
            f'  python3 {script_name} "25th July"'
        )
        print(
            f'  python3 {script_name} '
            '"1st July" "25th July"'
        )

        sys.exit(1)

    output_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    # One date directory was provided.
    if len(sys.argv) == 2:
        directory = get_snapshot_directory(sys.argv[1])

        run_single_snapshot(
            directory,
            output_directory,
        )

    # Two date directories were provided.
    else:
        old_directory = get_snapshot_directory(sys.argv[1])
        new_directory = get_snapshot_directory(sys.argv[2])

        run_comparison(
            old_directory,
            new_directory,
            output_directory,
        )


if __name__ == "__main__":
    main()