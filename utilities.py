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
        (1, "I")
)

def int2roman(n: int) -> str:
    global ROMAN_INTS
    # Converts an integer to a roman numeral as string
    roman = ""
    r = n # Remainer
    for i, num in ROMAN_INTS:
        mult = r // i
        if mult:
            roman += mult * num
            r = r % (mult * i)
            if r == 0:
                break
    return roman

def split_within(text: str, max_len: int, delim: str):
    # Splits a long text into two strings such that both string are within max_len length.
    splitted = text.split(delim)

    test_txt = ""
    for i in range(1, len(splitted)):
        if len(delim.join(splitted[:i])) > max_len:
            i -= 1
            break
    
    part1 = delim.join(splitted[:i])
    part2 = delim.join(splitted[i:])
    return (part1, part2)