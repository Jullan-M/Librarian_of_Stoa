import json
import re

import requests
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
        txt_split = re.split("\d+[\. ]", text)[1:]
        for ps, t in enumerate(txt_split):
            chapter[ps + 1] = re.sub(
                "[\u200b\u200c\u200d\u2060]|\[\d+\]", "", t
            ).strip()
        book[i] = chapter

    with open("books/meditations.json", "w") as f:
        f.write(json.dumps(book, indent="\t"))


def fetch_enchiridion():
    book = {}

    url = f"https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments/Manual"
    results = scrape_by_class(url, "prp-pages-output")
    references = results[-1].find_all("sup", class_="reference")
    for r in references:
        r.extract()
    text = results[-1].text
    text = re.sub("[\u200b\u200c\u200d\u2060]", "", text)

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
        title, text = text.split("[edit]", maxsplit=1)
        title = title.rsplit("\n", maxsplit=1)[-1]
        text = text.split("Footnotes", maxsplit=1)[0]

        chapter = {}
        # Chapter 0 is the title of the letter
        chapter[0] = title.split(". ", maxsplit=1)[-1].replace("[1]", "")

        txt_split = re.split("\d+\.\s", text)
        for ps, t in enumerate(txt_split):
            passage = re.sub("\[\d+\]", "", t.lstrip())
            # Replace single linebreaks with double using regex negative lookbehind and lookahead
            passage = re.sub("(?<!\n)\n(?!\n)", "\n\n", passage)
            if passage:
                chapter[ps] = passage

        book[i] = chapter

    with open("books/letters.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))


def fetch_happylife():
    book = {}

    for i in range(1, 29):
        print(f'Fetching "Of a Happy Life" {i} of 28', end="\r")
        url = f"https://en.wikisource.org/wiki/Of_a_Happy_Life/Book_{int2roman(i)}"
        results = scrape_by_class(url, "mw-parser-output")

        # Remove superfluous stuff
        headerContainer = results[0].find_all(
            "div", class_="ws-noexport noprint dynlayout-exempt"
        )
        headerContainer[0].extract()
        licenseContainer = results[0].find_all(
            "div", class_="licenseContainer licenseBanner dynlayout-exempt"
        )
        licenseContainer[0].extract()
        references = results[0].find_all("sup", class_="reference")
        for r in references:
            r.extract()

        text = results[-1].text
        text = text.split("Footnotes", maxsplit=1)[0]
        text = text.split(f"{int2roman(i)}.", maxsplit=1)[-1]
        book[i] = text.strip()

    with open("books/happylife.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))


def fetch_shortness():
    book = {}

    for i in range(1, 21):
        print(f'Fetching "On the shortness of life" {i} of 20', end="\r")
        url = f"https://en.wikisource.org/wiki/On_the_shortness_of_life/Chapter_{int2roman(i)}"
        results = scrape_by_class(url, "mw-parser-output")

        # Remove superfluous stuff
        headerContainer = results[0].find_all(
            "div", class_="ws-noexport noprint dynlayout-exempt"
        )
        headerContainer[0].extract()
        references = results[0].find_all("sup", class_="reference")
        for r in references:
            r.extract()

        text = results[-1].text
        text = text.split("Footnotes", maxsplit=1)[0]
        text = text.split(f"{i}.", maxsplit=1)[-1]
        book[i] = text.strip()

    with open("books/shortness.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))


def fetch_discourses():
    books = {}
    chapters = [30, 26, 26, 13]

    for i, chaps in enumerate(chapters):
        books[i + 1] = {}
        for j in range(chaps):
            print(
                f'Fetching "Discourses" Book {i+1} Chapter {j+1}\tof {chaps}', end="\r"
            )
            url = f"https://en.wikisource.org/wiki/Epictetus,_the_Discourses_as_reported_by_Arrian,_the_Manual,_and_Fragments/Book_{i+1}/Chapter_{j+1}"
            results = scrape_by_class(url, "prp-pages-output")

            # Remove superfluous stuff
            references = results[-1].find_all("sup", class_="reference")
            for r in references:
                r.extract()
            for s in results[-1].select("sup"):
                s.extract()  # Remove green superscripted numbers
            text = results[-1].text
            text = re.sub("[\u200b\u200c\u200d\u2060]", "", text)
            text = re.sub(f"CHAPTER {int2roman(j+1)}\D", "", text)
            text = re.sub(f"\n\n\n", "\n\n", text)
            # Replace single linebreaks with double using regex negative lookbehind and lookahead
            text = re.sub("(?<!\n)\n(?!\n)", "\n\n", text)
            # txt_split = re.split("\n\d+\.", text)[1:]
            books[i + 1][j + 1] = text.strip()
        print()

    with open("books/discourses.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(books, indent="\t", ensure_ascii=False))


def fetch_anger():
    books = {}
    chapters = [21, 36, 43]

    for i, chaps in enumerate(chapters):
        print(f'Fetching "On Anger" Book {i+1}', end="\r")
        url = f"https://en.wikisource.org/wiki/Of_Anger/Book_{int2roman(i+1)}"
        results = scrape_by_class(url, "mw-parser-output")[-1]
        # Remove superfluous stuff
        results.find(
            "div", class_="ws-noexport noprint dynlayout-exempt"
        ).extract()  # Shave off book info
        front = results.find_all("div", class_="wst-center")
        edits = results.find_all("span", class_="mw-editsection")
        references = results.find_all("sup", class_="reference")
        for f in front:
            f.extract()  # Shave off frontmatter
        for e in edits:
            e.extract()  # Shave off "edit" prompts
        for r in references:
            r.extract()  # Shave off reference numbering
        results.find("table", class_="__smalltoc").extract()  # Shave off small toc
        results = results.find_all(
            ["h2", "p", "dd"]
        )  # Headers, paragraphs and centered quotes
        results = results[:-2]  # Shave off footnotes

        # Fill book
        book = {}
        headindex = 1
        text = ""
        for soup in results[1:]:
            if soup.find("span", class_="mw-headline"):
                # Replace single linebreaks with double using regex negative lookbehind and lookahead
                text = re.sub("(?<!\n)\n(?!\n)", "\n\n", text)
                book[headindex] = text.strip()
                text = ""
                headindex += 1
                continue

            if not (soup.text in text):
                if soup.find("dd") or soup.find("dl"):
                    text += soup.text + "\n"
                else:
                    text += soup.text

        book[headindex] = text.lstrip()  # Last page
        books[i + 1] = book

    with open("books/anger.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(books, indent="\t", ensure_ascii=False))


if __name__ == "__main__":
    to_fetch = [
        # fetch_meditations, # This wikisource primary text combines two chapter's into one paragraph.
        fetch_enchiridion,
        fetch_letters,
        fetch_happylife,
        fetch_shortness,
        fetch_discourses,
        fetch_anger,
    ]

    for f in to_fetch:
        f()
