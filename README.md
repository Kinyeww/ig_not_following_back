# Instagram Not Following Back Checker

A simple Python script that compares your Instagram followers and following data using Instagram’s exported JSON files.

It can:

* Find accounts that currently do not follow you back
* Compare two dated exports
* Find accounts that recently disappeared from your followers
* Find accounts that recently disappeared from your following
* Save the results into readable text files
* Run entirely on your computer without requiring your Instagram login

## Features

### Single-date mode

Provide one dated Instagram export folder to generate your current list of accounts that do not follow you back.

```bash
python3 ig_checker.py "25th July"
```

### Two-date comparison mode

Provide an older export followed by a newer export to generate:

1. The current accounts that do not follow you back
2. Accounts that followed you in the old export but are missing from the new export
3. Accounts you followed in the old export but are missing from the new export

```bash
python3 ig_checker.py "1st July" "25th July"
```

The order matters:

```text
First directory  = older Instagram export
Second directory = newer Instagram export
```

## Requirements

* Python 3
* Instagram data exported in JSON format
* `followers_1.json`
* `following.json`

No third-party Python packages are required.

## Downloading Your Instagram Data

When requesting your information from Instagram:

1. Select **Followers and following**
2. Uncheck the other information categories if you do not need them
3. Select **JSON** as the file format
4. Choose **ALL TIME** for date range
5. Download and extract the archive

You should locate these two files:

```text
followers_1.json
following.json
```

Place both files inside a folder named after the export date.

For example:

```text
25th July/
├── followers_1.json
└── following.json
```

> HTML exports are not supported. Make sure you select JSON.

<img width="565" height="186" alt="Instagram export settings" src="https://github.com/user-attachments/assets/2e0be25f-c084-4066-bef7-fbecc26088ee" />

## Installation

Clone the repository:

```bash
git clone https://github.com/Kinyeww/ig_not_following_back.git
```

Enter the repository:

```bash
cd ig_not_following_back
```

Create your dated export folders beside `ig_checker.py`.

## Folder Structure

Your project should look like this:

```text
ig_not_following_back/
├── ig_checker.py
├── README.md
│
├── 1st July/
│   ├── followers_1.json
│   └── following.json
│
└── 25th July/
    ├── followers_1.json
    └── following.json
```

You can use any folder name. Using the export date makes it easier to identify and compare different snapshots.

If a directory name contains spaces, place quotation marks around it when running the program.

## Usage

### Check one Instagram export

Run the script with one directory:

```bash
python3 ig_checker.py "25th July"
```

On Windows, you can also use:

```powershell
py ig_checker.py "25th July"
```

This calculates:

```text
Current following − Current followers
```

The result contains accounts you currently follow that are not present in your current followers export.

Example output:

```text
Followers parsed: 520
Following parsed: 610
Not following you back: 90
Saved to: 25th_July_unfollowers.txt
```

The generated file will be:

```text
25th_July_unfollowers.txt
```

### Compare two Instagram exports

Run the script with the older directory first and the newer directory second:

```bash
python3 ig_checker.py "1st July" "25th July"
```

On Windows:

```powershell
py ig_checker.py "1st July" "25th July"
```

This generates three lists.

#### 1. Currently not following you back

```text
New following − New followers
```

These are accounts you currently follow that are not present in your latest followers export.

#### 2. Recently unfollowed by others

```text
Old followers − New followers
```

These are accounts that appeared in your older followers export but are missing from your newer followers export.

#### 3. Recently unfollowed by you

```text
Old following − New following
```

These are accounts that appeared in your older following export but are missing from your newer following export.

Example terminal output:

```text
Old followers parsed: 525
New followers parsed: 520
Old following parsed: 615
New following parsed: 610

Not following you back: 90
Recently unfollowed by others: 5
Recently unfollowed by you: 5
```

## Generated Files

For this command:

```bash
python3 ig_checker.py "1st July" "25th July"
```

the program generates:

```text
25th_July_unfollowers.txt
1st_July_to_25th_July_unfollowed_by_others.txt
1st_July_to_25th_July_unfollowed_by_me.txt
```

Spaces in directory names are replaced with underscores in the generated filenames.

### Example unfollower file

```text
Not following you back:
example_user1
example_user2
example_user3
```

### Example comparison file

```text
Recently unfollowed by others:
example_user4
example_user5
```

## Choosing an Export Time Range

The time range you select when downloading your Instagram data affects the results.

### Shorter time range

A shorter range, such as the last year or last three years, may produce cleaner results because it is less likely to contain old or inactive account records.

However, the exported follower and following totals may be lower than the numbers currently displayed on your Instagram profile.

### All-time export

An all-time export generally provides more complete historical data and may produce totals closer to those displayed on your Instagram account.

However, Instagram may include old records related to accounts that have:

* Changed their username
* Been deleted
* Been deactivated
* Been disabled or banned
* Become unavailable
* Blocked your account

These may appear as unfollowers or missing accounts even when they did not simply unfollow you.

If your exported follower or following totals are noticeably lower than your current Instagram totals, try exporting a longer date range or selecting all time.

## Important Accuracy Warning

The script compares usernames stored in two JSON exports. It does not have access to Instagram’s internal account IDs or account status information.

Because of this, it cannot reliably determine whether someone:

* Unfollowed you
* Removed you as a follower
* Blocked you
* Deactivated their account
* Deleted their account
* Was disabled by Instagram
* Changed their username

For example, if an account changes from:

```text
old_username
```

to:

```text
new_username
```

the script sees one username disappear and another username appear. It cannot automatically know that both usernames belong to the same person.

Therefore, **“recently unfollowed by others” means the username is missing from the newer export**, not that the script has proven the person intentionally unfollowed you.

The same limitation applies to “recently unfollowed by you.” An unavailable account may disappear from your following export even if you did not manually unfollow it.

Use the generated lists as comparison results that may require manual verification.

## Parse Problem Files

The script supports several Instagram JSON structures. If an entry cannot be understood, it may generate files such as:

```text
25th_July_followers_parse_problems.json
25th_July_following_parse_problems.json
```

These files contain the entries that the script could not parse.

A parse problem does not necessarily mean the entire result is incorrect, but you should inspect the file if the reported problem count is greater than zero.

## Common Errors

### Directory not found

```text
ERROR: directory not found: ...
```

Make sure:

* The directory exists
* You typed its name correctly
* You are running the command from the repository directory
* Folder names containing spaces are inside quotation marks

Correct:

```bash
python3 ig_checker.py "25th July"
```

Incorrect:

```bash
python3 ig_checker.py 25th July
```

Without quotation marks, `25th` and `July` are treated as separate arguments.

### `followers_1.json` not found

```text
ERROR: followers_1.json not found in: ...
```

Make sure the filename is exactly:

```text
followers_1.json
```

and that it is directly inside the dated directory.

### `following.json` not found

```text
ERROR: following.json not found in: ...
```

Make sure the filename is exactly:

```text
following.json
```

and that it is directly inside the dated directory.

### Incorrect number of arguments

The program accepts either:

```text
One directory  → current unfollower list
Two directories → current list and date comparison
```

Examples:

```bash
python3 ig_checker.py "25th July"
python3 ig_checker.py "1st July" "25th July"
```

### Invalid JSON

Make sure:

* You selected JSON instead of HTML
* The downloaded archive was completely extracted
* The files were not corrupted or manually modified
* You selected the Followers and following category

## Privacy

The script processes everything locally on your computer.

It does not:

* Ask for your Instagram username or password
* Log in to Instagram
* Upload your files
* Use an external API
* Send your follower data anywhere
* Automatically access Instagram profiles

Your Instagram export may contain personal information. Do not commit your dated export folders or generated result files to a public repository.

A recommended `.gitignore` is:

```gitignore
# Instagram exports
*/followers_1.json
*/following.json

# Generated results
*_unfollowers.txt
*_unfollowed_by_others.txt
*_unfollowed_by_me.txt
*_parse_problems.json
```

## How It Works

The script loads usernames into Python sets.

For a single export:

```python
not_following_back = following - followers
```

For two exports:

```python
not_following_back = new_following - new_followers

unfollowed_by_others = old_followers - new_followers

unfollowed_by_me = old_following - new_following
```

The results are sorted alphabetically and saved into text files.

## Disclaimer

This project is not affiliated with, endorsed by, or associated with Instagram or Meta.

Instagram may change its data export format at any time. If the format changes, the parser may require an update.

Only use this tool with data exported from your own Instagram account.
