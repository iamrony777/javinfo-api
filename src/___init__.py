from src.providers import Javdatabase, R18, Javlibrary
import concurrent.futures

r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()



r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()

def search_all_providers(code: str):
    providers = [r18Provider, jvdtbsProvider, jvlibProvideer]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(provider.search, code) for provider in providers]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    return min(results, key=lambda result: result)


if __name__ == "__main__":
    print(search_all_providers('EBOD-391'))