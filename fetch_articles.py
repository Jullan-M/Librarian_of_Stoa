import requests
import json
import re
from bs4 import BeautifulSoup


def fetch_meditations():
    book = {}

    for i in range(1, 13):
        print(f"Fetching Book {i} of 12", end="\r")
        url = f"https://en.wikisource.org/wiki/The_Meditations_of_the_Emperor_Marcus_Antoninus/Book_{i}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("div", class_="prp-pages-output")
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
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_="prp-pages-output")
    text = results[-1].text

    txt_split = re.split("\n\d+\.", text)[1:]
    for ps, t in enumerate(txt_split):
        book[ps + 1] = re.sub("[\d+]", "", t.strip()).replace("[]", "")

    with open("books/enchiridion.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))

def fetch_letters():
    book = {}

    for i in range(1, 125):
        print(f"Fetching Letter {i} of 124", end="\r")
        url = f"https://en.wikisource.org/wiki/Moral_letters_to_Lucilius/Letter_{i}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all("div", class_="mw-parser-output")
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
fetch_meditations()
fetch_enchiridion()
fetch_letters()