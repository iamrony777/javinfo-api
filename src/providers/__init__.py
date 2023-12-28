
from enum import Enum
from .javdatabase import Javdatabase
from .r18 import R18
from .javlibrary import Javlibrary
from .javdb import Javdb


class Providers(str, Enum):
    """
    Enumeration of providers for the API.

    This class represents the available providers for the API. Each provider has a unique value
    that can be used to identify it.
    """

    r18 = "r18"
    jvdtbs = "jvdtbs"
    jvlib = "jvlib"
    javdb = "javdb"
    all = "all"
