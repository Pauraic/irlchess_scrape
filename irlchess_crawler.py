#https://www.irlchess.com/cgi-bin/searchforgames.pl?query=O%27Reilly+Conor

import os
import requests
from bs4 import BeautifulSoup,Comment
from urllib.parse import quote
import glob
import shutil


site = "https://www.irlchess.com/cgi-bin/searchforgames.pl?query="

name = input("Enter player name ( e.g. John Smith): ")

foldername = ''.join(c for c in name if c.isalnum())

#print(foldername)
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

                    # Save to a .pgn file
                    filename = os.path.join(foldername, os.path.basename(link).replace('.htm', '.pgn'))
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(comment_text)
                        print(f"Saved comment to {filename}")
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
        output_file = f"{foldername}.pgn"
        with open(output_file, "w") as outfile:
            for file in files:
                with open(file, "r") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")  # Separate games
        print("merged")
    shutil.rmtree(foldername)
else:
    print("folder not found")

