import requests
from functools import cache


URL = 'https://counterstrike.fandom.com/wiki/Category:Active_Duty_Group'


def get_page(url):
    page = requests.get(url)
    return page.text


@cache
def get_active_duty():
    page = get_page(URL)
    lines = page.splitlines()
    ad = []
    for idx, line in enumerate(lines):
        if 'Current Map' in line:
            for line in lines[idx:]:
                if 'Map Pool History' in line:
                    return ad
                if 'href="/wiki/' in line:
                    ad.append(line.split('"')[1].removeprefix('/wiki/'))


def main():
    AD = get_active_duty()
    print(AD)


if __name__ == '__main__':
    main()
