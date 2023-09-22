from src.providers import Javdatabase, R18, Javlibrary
import concurrent.futures

r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()

#TODO: all of these providers has a common method `search`. Now create a function which searches all of them using python's co