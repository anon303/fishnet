def sluggify(s):
    """
    Changes a string into it's slugged variety.
    """
    slug = replace(s.lower(), {" ": "_", "'": "", '"': ""})
    return slug


def replace(s, dic):
    """
    Replace all chars in s corresponding with the keys in dic, and susbsitute
    them with the values in  dic.
    """
    for original_char, replacement_char in dic.iteritems():
        s = s.replace(original_char, replacement_char)
    return s


def truncate(s, output_length, ellipsis_count=3):
    """
    Truncate strings if neccesary; if so, we append a user-specifiable
    amount of ellipsis to indicate that the string has been truncated.
    """
    if len(s) > output_length:
        return s[:output_length - ellipsis_count] + ellipsis_count * '.'
    else:
        return s
