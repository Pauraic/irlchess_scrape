#https://www.irlchess.com/cgi-bin/searchforgames.pl?query=O%27Reilly+Conor

import os
import requests
from bs4 import BeautifulSoup,Comment
from urllib.parse import quote
import glob
import shutil
import re


site = "https://www.irlchess.com/cgi-bin/searchforgames.pl?query="

name = input("Enter player name ( e.g. John Smith): ")
color = input("Are they playing white or black? ( type w or b): ").strip().lower()
if color not in ["w","b"]:
    print("invalid choice!")
    exit()

def match_comment_color(comment,color,firstname,lastname):
    white_match = re.search(r'\[White "([^"]+)"\]',comment)
    black_match = re.search(r'\[Black "([^"]+)"\]',comment)

    white_player = white_match.group(1) if white_match else ""
    black_player = black_match.group(1) if black_match else ""

    player_field = white_player if color == "w" else black_player

    if ", " in player_field:
        last_name_field, first_name_field = player_field.split(", ", 1)
    else:
        last_name_field, first_name_field = player_field, ""

    first_name_matches = first_name.lower() in first_name_field.lower()
    last_name_matches = last_name.lower() in last_name_field.lower()

    return first_name_matches and last_name_matches




foldername = ''.join(c for c in name if c.isalnum())

if not os.path.exists(foldername):
    os.makedirs(foldername)

try:
    first_name, last_name = name.split()
    cleanfirstname = quote(first_name, safe=":/=&")
    cleanlastname = quote(last_name, safe=":/=&")

    namestring = f"{last_name}+{first_name}"
except ValueError:
    print("Please enter a name in the format: FirstName LastName")

print(namestring)

target = f"{site}{namestring}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",  # Generic Firefox User-Agent
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}



try:
    response = requests.get(target, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    pgn_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.htm')]


    if not pgn_links:
        print("no links found - check the username is spelled correctly maybe?")
    else:
        print(pgn_links)
        for link in pgn_links:
            if not link.startswith("http"):
                link = requests.compat.urljoin(site, link)
            print(f"Processing: {link}")

            try:
                page_response = requests.get(link, headers=headers)
                page_response.raise_for_status()
                page_soup = BeautifulSoup(page_response.text, 'html.parser')

                # Extract the comment at the end of the page
                comments = page_soup.find_all(string=lambda text: isinstance(text, Comment))
                if comments:
                    comment_text = comments[-1].strip()  # Get the last comment
                    comment_text = comment_text[6:]

                    if match_comment_color(comment_text,color,first_name,last_name):

                        valid = bool(re.search(r'}\s*1\.', comment_text))

                        if valid:
                            # Save to a .pgn file
                            filename = os.path.join(foldername, os.path.basename(link).replace('.htm', '.pgn'))
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(comment_text)
                                print(f"Saved comment to {filename}")
                        else:
                            print("no moves in pgn (result only), skipping")
                    else:
                        print("skipped, wrong colour")
                else:
                    print(f"No comments found in {link}")
            except requests.RequestException as e:
                print(f"Error fetching {link}: {e}")




except requests.RequestException as e:
    print(f"An error occured: {e}")



if os.path.exists(foldername):
    files = glob.glob(os.path.join(foldername,"*.pgn"))
    if not files:
        print("no pgn files found")
    else:
        colour = "black" if color=="b" else "white"
        output_file = f"{foldername}_{colour}.pgn"
        with open(output_file, "w") as outfile:
            for file in files:
                with open(file, "r") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")  # Separate games
        print("merged")
    shutil.rmtree(foldername)
else:
    print("folder not found")

