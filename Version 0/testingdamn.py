string1 = "!label"
string2 = "!frame"

if any([x in string1 for x in ["!label","!frame"]]):
    print(string1)