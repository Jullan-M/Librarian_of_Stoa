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
        book[ps + 1] = re.sub("(?<!\n)\n(?!\n)", "\n\n", t).strip()

    with open("books/enchiridion.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book, indent="\t", ensure_ascii=False))


def fetch_letters():
    book = {}

    for i in range(1, 125):
        print(f"Fetching Letter {i} of 124", end="\n")
        url = f"https://en.wikisource.org/wiki/Moral_letters_to_Lucilius/Letter_{i}"
        results = scrape_by_class(url, "mw-parser-output")

        # Remove superfluous stuff
        headerContainer = results[0].find_all(
            "div",
            class_="ws-header wst-header-structure wst-unknown wst-header ws-header ws-noexport noprint dynlayout-exempt",
        )

        headerContainer[0].extract()

        titleContainer = results[0].find_all(
            "div",
            class_="wst-center tiInherit wst-center-nomargin",
        )

        title = titleContainer[1].text if i == 1 else titleContainer[0].text

        title = title.split(". ", maxsplit=1)[-1].replace("[1]", "").strip()
        for t in titleContainer:
            t.extract()

        references = results[0].find_all("div", class_="reflist")
        if references:
            references[0].extract()

        text = results[0].text.strip()

        chapter = {}
        # Chapter 0 is the title of the letter
        chapter[0] = title

        txt_split = re.split("\d+\.\s", text)
        for ps, t in enumerate(txt_split):
            passage = re.sub("\[\d+\]", "", t.lstrip())
            # Replace single linebreaks with double using regex negative lookbehind and lookahead
            passage = re.sub("(?<!\n)\n(?!\n)", "\n\n", passage)
            if passage and ps > 0:
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
            "div",
            class_="ws-header wst-header-structure wst-unknown wst-header ws-header ws-noexport noprint dynlayout-exempt",
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
        # Replace single lineshifts with double (only if there is single lineshift).
        book[i] = re.sub("\n\n\n", "\n\n", text).strip()

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
            "div",
            class_="ws-header wst-header-structure wst-unknown wst-header ws-header ws-noexport noprint dynlayout-exempt",
        )

        headerContainer[0].extract()
        references = results[0].find_all("sup", class_="reference")

        for r in references:
            r.extract()

        text = results[-1].text
        text = text.split("Footnotes", maxsplit=1)[0]
        text = text.split(f"{i}.", maxsplit=1)[-1]
        # Replace single lineshifts with double (only if there is single lineshift).
        book[i] = re.sub("(?<!\n)\n(?!\n)", "\n\n", text).strip()

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
        results = scrape_by_class(url, "mw-content-ltr mw-parser-output")[0]

        # Remove superfluous stuff
        results.find(
            "div",
            class_="ws-header wst-header-structure wst-unknown wst-header ws-header ws-noexport noprint dynlayout-exempt",
        ).extract()  # Shave off book info

        front = results.find_all(
            "div", class_="wst-center tiInherit wst-center-nomargin"
        )
        edits = results.find_all("span", class_="mw-editsection")
        references = results.find_all("sup", class_="reference")
        for f in front:
            f.extract()  # Shave off frontmatter
        for e in edits:
            e.extract()  # Shave off "edit" prompts
        for r in references:
            r.extract()  # Shave off reference numbering
        results.find(
            "table", class_="wst-small-toc wst-small-toc-center"
        ).extract()  # Shave off small toc
        results.find("div", class_="reflist").extract()  # Shave off Footnotes
        results.find(
            "div", class_="licenseContainer licenseBanner dynlayout-exempt"
        ).extract()
        results = results.find_all(
            ["h2", "p", "dd"]
        )  # Headers, paragraphs and centered quotes

        # Shave off some extra fluff (including footnotes headers)
        results = results[:-1] if i + 1 != 2 else results[:-2]

        # Fill book
        book = {}
        headindex = 0
        text = ""
        for soup in results:
            if soup.name == "h2":
                if headindex > 0:
                    book[headindex] = re.sub("(?<!\n)\n(?!\n)", "\n\n", text.strip())
                text = ""
                headindex += 1
            elif soup.name == "p":
                # Replace single linebreaks with double using regex negative lookbehind and lookahead
                text += soup.text
            elif soup.name == "dd" and soup.find_parent("dd"):
                # We have to do this otherwise it duplicates. the dd-dl tree coming from the findall above is nested
                if not soup.text in text:
                    text += soup.text + "\n"
        book[headindex] = text.strip()  # Last page
        books[i + 1] = book

    with open("books/anger.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(books, indent="\t", ensure_ascii=False))


def fetch_musonius():
    # Musonius Rufus' discourses

    def scrape_page(url: str):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup.find_all("div", class_="tyJCtd mGzaTb Depvyb baZpAe")[0].find_all(
            "p"
        )

    book = {}
    for i in range(1, 10):
        print(f"Fetching Musonius Rufus' - Lectures {i} of 21", end="\r")
        # Lecture i in book
        book[f"{i}"] = {}
        url = f"https://sites.google.com/site/thestoiclife/the_teachers/musonius-rufus/lectures/{i:02}"

        # Scrape the page
        results = scrape_page(url)

        title = f"Lecture {int2roman(i)} - {results[1].find("em").text}"
        book[f"{i}"]["0"] = title

        last_index = "1"
        for j in range(2, len(results)):
            if any(char in results[j].text for char in ["◄", "►"]):
                book[f"{i}"][f"{last_index}"] = book[f"{i}"][f"{last_index}"].rstrip()
                break

            text = re.sub("\[\d+\]", "", results[j].text)

            # Special case handling for lecture 7, 3rd paragraph
            m = (
                re.fullmatch(r"(\d+) (.+)", text)
                if not (i == 7 and j - 1 == 3)
                else re.fullmatch(r"(\d+)(.+)", text)
            )
            if m:
                if int(m[1]) > int(last_index):
                    book[f"{i}"][f"{last_index}"] = book[f"{i}"][f"{last_index}"] + "\n"

                last_index = m[1]

                book[f"{i}"][m[1]] = m[2] + "\n"
            else:
                book[f"{i}"][f"{last_index}"] = (
                    book[f"{i}"][f"{last_index}"].lstrip() + text + "\n"
                )

    for i in ["10", "11", "12", "13-0", "13-1", "14"]:
        print(f"Fetching Musonius Rufus' - Lectures {i} of 21", end="\r")
        # Lecture i in book
        book[i] = {}
        url = f"https://sites.google.com/site/thestoiclife/the_teachers/musonius-rufus/lectures/{i}"

        # Scrape the page
        results = scrape_page(url)

        title = f"Lecture {int2roman(int(i[:2]))} - {results[1].find("em").text}"
        book[f"{i}"]["0"] = title

        last_index = "1"
        for j in range(2, len(results)):
            if any(char in results[j].text for char in ["◄", "►"]) or (
                i == "11" and j >= 8
            ):
                book[i][f"{last_index}"] = book[i][f"{last_index}"].rstrip()
                break

            text = re.sub("\[\d+\]", "", results[j].text)
            matches = re.findall(r"(\d+)(\D+)", text)
            if matches:
                if int(matches[0][0]) > int(last_index):
                    book[f"{i}"][f"{last_index}"] = book[f"{i}"][f"{last_index}"] + "\n"
                for m in matches:
                    # Exception for lecture 11, paragragh 2, sentence 22
                    if i == "11" and j == 3 and m[0] == "2":
                        last_index = "23"
                        book[i]["23"] = m[1]
                        continue
                    last_index = m[0]
                    book[i][m[0]] = m[1]

            else:
                book[i][f"{last_index}"] = book[i][f"{last_index}"] + text
            # Add lineshift
            book[i][last_index] = book[i][last_index].rstrip() + "\n"

    # Merge entry 13-0 and 13-1 into one entry, remove their individual entries
    print("Merging 13-0 and 13-1")
    book["13"] = book["13-0"].copy()
    max_key = list(book["13"].keys())[-1]
    book["13"][f"{max_key}"] = (
        book["13"][f"{max_key}"]
        + "\n\n[... TIME DEVOURS ALL—THE WRITER, THE READER, THE PAGES. BUT FOR NOW, THE FOLLOWING SURVIVES. FOR NOW, SO DO YOU ...]\n\n"
    )

    for key, value in book["13-1"].items():
        if key == "0":
            continue
        book["13"][f"{int(max_key) + int(key)}"] = value
    del book["13-0"]
    del book["13-1"]

    for i in ["15", "16", "17", "18-0", "18-1", "19", "20", "21"]:
        print(f"Fetching Musonius Rufus' - Lectures {i} of 21", end="\r")
        # Lecture i in book
        book[f"{i}"] = {}
        url = f"https://sites.google.com/site/thestoiclife/the_teachers/musonius-rufus/lectures/{i}"

        # Scrape the page
        results = scrape_page(url)

        title = f"Lecture {int2roman(int(i[:2]))} - {results[1].find("em").text}"
        book[f"{i}"]["0"] = title
        book[f"{i}"]["1"] = ""
        last_index = 1
        for j in range(2, len(results)):
            index = j - 1
            if any(char in results[j].text for char in ["◄", "►"]):
                break
            text = re.sub("\[\d+\]", "", results[j].text)
            book[f"{i}"][f"{index}"] = text.rstrip() + "\n\n"
            last_index = index
        book[f"{i}"][f"{last_index}"] = book[f"{i}"][f"{last_index}"].rstrip()

    # Merge entry 18-0 and 18-1 into one entry, remove their individual entries
    print("Merging 18-0 and 18-1")
    book["18"] = book["18-0"].copy()
    max_key = list(book["18"].keys())[-1]
    book["18"][f"{max_key}"] = (
        book["18"][f"{max_key}"]
        + "\n\n[... LIKE THE WORDS OF WISDOM ONCE WRITTEN HERE, YOU TOO WILL ONE DAY BE FRAGMENTED—MAKE GOOD USE OF WHAT REMAINS ...]\n\n"
    )

    for key, value in book["18-1"].items():
        if key == "0":
            continue
        book["18"][f"{int(max_key) + int(key)}"] = value
    del book["18-0"]
    del book["18-1"]

    for i in range(22, 54):
        print(f"Fetching Musonius Rufus' - Fragments {i} of 53", end="\r")
        # Lecture i in book
        book[f"{i}"] = {}
        url = f"https://sites.google.com/site/thestoiclife/the_teachers/musonius-rufus/fragments/{i}"

        # Scrape the page
        results = scrape_page(url)

        title = (
            f"Fragment {int2roman(i)} - {results[1].find("em").text}"
            if results[1].find("em")
            else f"Fragment {int2roman(i)}"
        )
        book[f"{i}"]["0"] = title
        book[f"{i}"]["1"] = ""
        last_index = 1
        start_index = 1 if i in [36, 37, 43, 44, 45, 46, 47, 48, 50, 52, 53] else 2
        for j in range(start_index, len(results)):
            index = j if i in [36, 37, 43, 44, 45, 46, 47, 48, 50, 52, 53] else j - 1
            if any(char in results[j].text for char in ["◄", "►"]):
                break

            text = re.sub("\[\d+\]", "", results[j].text)
            book[f"{i}"][f"{index}"] = text.rstrip() + "\n"
            last_index = index
        book[f"{i}"][f"{last_index}"] = book[f"{i}"][f"{last_index}"].rstrip()

    with open("books/musonius.json", "w", encoding="utf-8") as f:
        json.dump(book, f, indent="\t", ensure_ascii=False)


if __name__ == "__main__":
    to_fetch = [
        # fetch_meditations, # This wikisource primary text combines two chapter's into one paragraph.
        fetch_enchiridion,
        fetch_letters,
        fetch_happylife,
        fetch_shortness,
        fetch_discourses,
        fetch_anger,
        fetch_musonius,
    ]

    for f in to_fetch:
        f()
