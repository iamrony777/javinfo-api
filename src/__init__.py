from src.providers import Javdatabase, R18, Javlibrary
import concurrent.futures

r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()


def search_all_providers(code: str):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        r18_search = executor.submit(r18Provider.search, code)
        jvdtbs_search = executor.submit(jvdtbsProvider.search, code)
        jvlib_search = executor.submit(jvlibProvideer.search, code)

        completed, _ = concurrent.futures.wait(
            [r18_search, jvdtbs_search, jvlib_search],
            return_when=concurrent.futures.FIRST_COMPLETED,
        )

        for task in completed:
            result = task.result()
            if "statusCode" in result:
                continue

            return result
