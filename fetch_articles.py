import requests
import json
import re
from bs4 import BeautifulSoup
from utilities import int2roman

def scrape_by_class(url: str, class_: str):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup.find_all("div", class_=class_)


def fetch_meditations():
    book = {}

    for i in range(1, 13):
        print(f"Fetching Book {i} of 12", end="\r")
        url = f"https://en.wikisource.org/wiki/The_Meditations_of_the_Emperor_Marcus_Antoninus/Book_{i}"
        results = scrape_by_class(url, "prp-pages-output")
        text = results[-1].text
        
        chapter = {}
        txt_split = re.split("\d+\.", text)[1:]
        for ps, t in enumerate(txt_split):
            chapter[ps + 1] = t.replace("\u200b", "").strip()
        book[i] = chapter

    with open("books/meditations.json", "w") as f:
        f.write(json.dumps(book, indent="\t"))

def fetch_enchiridion():
    book = {}

    url = f"https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments/Manual"
    results = scrape_by_class(url, "prp-pages-output")
    references = results[-1].find_all("sup", class_="reference")
    for r in references: r.extract()
    text = results[-1].text

    txt_split = re.split("\n\d+\.", text)[1:]
    for ps, t in enumerate(txt_split):
        book[ps + 1] = t.strip()

    with open("books/enchiridion.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))

def fetch_letters():
    book = {}

    for i in range(1, 125):
        print(f"Fetching Letter {i} of 124", end="\r")
        url = f"https://en.wikisource.org/wiki/Moral_letters_to_Lucilius/Letter_{i}"
        results = scrape_by_class(url, "mw-parser-output")
        text = results[-1].text
        text = text.split("[edit]", maxsplit=1)[-1]
        text = text.split("Footnotes", maxsplit=1)[0]

        chapter = {}
        txt_split = re.split("\d+\.\s", text)
        for ps, t in enumerate(txt_split):
            passage = re.sub("[\d+]", "", t.lstrip()).replace("[]", "")
            if passage:
                chapter[ps] = passage
        book[i] = chapter

    with open("books/letters.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))

def fetch_happylife():
    book = {}

    for i in range(1, 29):
        print(f"Fetching \"Of a Happy Life\" {i} of 28", end="\r")
        url = f"https://en.wikisource.org/wiki/Of_a_Happy_Life/Book_{int2roman(i)}"
        results = scrape_by_class(url, "mw-parser-output")

        # Remove superfluous stuff
        headerContainer = results[0].find_all("div", class_="ws-noexport noprint dynlayout-exempt")
        headerContainer[0].extract()
        licenseContainer = results[0].find_all("div", class_="licenseContainer licenseBanner dynlayout-exempt")
        licenseContainer[0].extract()
        references = results[0].find_all("sup", class_="reference")
        for r in references: r.extract()

        text = results[-1].text
        text = text.split("Footnotes", maxsplit=1)[0]
        text = text.split(f"{int2roman(i)}.", maxsplit=1)[-1]
        book[i] = text.strip()

    with open("books/happylife.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))

def fetch_shortness():
    book = {}

    for i in range(1, 21):
        print(f"Fetching \"On the shortness of life\" {i} of 20", end="\r")
        url = f"https://en.wikisource.org/wiki/On_the_shortness_of_life/Chapter_{int2roman(i)}"
        results = scrape_by_class(url, "mw-parser-output")

        # Remove superfluous stuff
        headerContainer = results[0].find_all("div", class_="ws-noexport noprint dynlayout-exempt")
        headerContainer[0].extract()
        references = results[0].find_all("sup", class_="reference")
        for r in references: r.extract()

        text = results[-1].text
        text = text.split("Footnotes", maxsplit=1)[0]
        text = text.split(f"{i}.", maxsplit=1)[-1]
        book[i] = text.strip()

    with open("books/shortness.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))

fetch_meditations()
fetch_enchiridion()
fetch_letters()
fetch_happylife()
fetch_shortness()