import re


def filter_string(name: str):
    """Filter string."""
    name = name.upper()

    try:
        pattern = r"[a-zA-Z]{1,5}(-|\W)\d{3,6}"  # JAV code should be like this
        return re.match(pattern, "".join(name)).group()
    except AttributeError:
        return None
