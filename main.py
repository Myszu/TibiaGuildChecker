import requests
import pandas as pd
from bs4 import BeautifulSoup
from progressbar import progressbar as pb
from datetime import datetime

# Local Imports
from modules import config as cfg

MEMBERS: list[dict] = []

def get_guild_members(guild) -> None:
    """Gets a list of guild members from `tibia.com`
    """
    params = {"GuildName": guild}
    response = requests.get("https://www.tibia.com/community/?subtopic=guilds&page=view", params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.select('table')
    try:
        for table in tables:
            if 'guild members' in table.text.lower():
                rows = table.select('tr')
        try:
            for row in rows:
                if 'subtopic=character' in str(row):
                    cells = row.select('td')
                    name = cells[1].select_one('a').text if cells[1].select_one('a').text != 'sort' else None
                    if name:
                        MEMBERS.append({
                                "name": name.replace('\xa0', ' '),
                                "link": cells[1].select_one('a')['href']
                            })
        except:
            print('Error on parsing list!')
    except:
        print('Member List not found!')
        return

def investigate_member(member: dict) -> dict:
    """Investigates a single member and tries to gather some basic info about him/her.

    Args:
        member (dict): Single member's record.

    Returns:
        dict: Same record enhanced with additional metrics.
    """
    response = requests.get(member['link'])
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.select('table')
    vocation = ''
    level = ''
    ap = ''
    residence = ''
    last_login = ''
    for table in tables:
        if 'character information' in table.text.lower():
            rows = table.select('tr')
            for row in rows[2::]:
                if 'vocation' in row.select('td')[0].text.lower():
                    vocation = row.select('td')[1].text
                    continue
                if 'level' in row.select('td')[0].text.lower():
                    level = row.select('td')[1].text
                    continue
                if 'achievement points' in row.select('td')[0].text.lower():
                    ap = row.select('td')[1].text
                    continue
                if 'residence' in row.select('td')[0].text.lower():
                    residence = row.select('td')[1].text
                    continue
                if 'last login' in row.select('td')[0].text.lower():
                    last_login = row.select('td')[1].text
            member['vocation'] = vocation.replace('\xa0', ' ')
            member['level'] = int(level)
            member['ap'] = int(ap)
            member['residence'] = residence.replace('\xa0', ' ')
            member['last_login'] = datetime.strptime(last_login.replace('\xa0', ' ').replace(' CEST', ''), "%b %d %Y, %H:%M:%S") if last_login else None
            return member
        
def save_to_file(file_path: str) -> None:
    """Saves a list of members to `CSV` file.

    Args:
        file_path (str): Full path of the file (with file's name).
    """
    
    df = pd.DataFrame(data=MEMBERS, columns=MEMBERS[0].keys())
    df = df.drop("link", axis=1)
    df.to_csv(file_path, sep=',', index=False, encoding='utf8')

if __name__ == "__main__":
    get_guild_members(cfg.GUILD)
    if MEMBERS:
        for member in pb(MEMBERS, 0, len(MEMBERS)):
            member = investigate_member(member)
            today = datetime.now().date()
            file_path = f'./output/{cfg.GUILD}_{today.strftime("%d%m%Y")}.csv'
            save_to_file(file_path)
        print(f'All done, created file {file_path}!')
    else:
        print("Couldn't get the members list.")