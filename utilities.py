import random

ROMAN_INTS = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)


def int2roman(n: int) -> str:
    global ROMAN_INTS
    # Converts an integer to a roman numeral as string
    roman = ""
    r = n  # Remainer
    for i, num in ROMAN_INTS:
        mult = r // i
        if mult:
            roman += mult * num
            r = r % (mult * i)
            if r == 0:
                break
    return roman


def split_within(
    text: str, max_len: int, delims: str, keep_delim: bool = False
) -> list:
    # Splits a long text into parts such that all string are within max_len length.
    if len(text) <= max_len:
        return [text]

    delim = delims[0]

    spl = text.split(delim)

    splitted = []
    split_lens = []
    for i, s in enumerate(spl):
        if len(s) <= max_len:
            splitted.append(s)
        else:
            splitted_even_more = split_within(s, max_len, delims[1:], keep_delim)
            splitted.extend(splitted_even_more)

    split_lens = [len(s) for s in splitted]
    # print(split_lens)

    parts = []
    i = 0
    for j in range(1, len(split_lens) + 1):
        if sum(split_lens[i:j]) + (j - i) * len(delim) > max_len:
            part = delim.join(splitted[i : j - 1])
            if keep_delim:
                part = part + delim
            parts.append(part)
            i = j - 1

    parts.append(delim.join(splitted[i:]))
    return parts


def uniform_random_choice_from_dict(books: dict):
    # Chooses uniformly a random value from a two-layered dict with the structure (say)
    # books = {bk1: {cha11: v1, cha12: v2}, bk2: {cha21: v3}}
    # Returns the key-pair for that value
    bk = random.choices(
        list(books.keys()), weights=[len(v.keys()) for v in books.values()]
    )[0]
    chapters = list(books[bk].keys())
    cha = str(random.choice(chapters))
    return bk, cha
