from src.providers import Javdatabase, R18, Javlibrary
import concurrent.futures

r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()


def search_all_providers(code: str, includeActressUrl: bool = False):
    executors_list = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executors_list.append(executor.submit(r18Provider.search, code))
        executors_list.append(executor.submit(jvdtbsProvider.search, code))

        if not includeActressUrl:
            executors_list.append(executor.submit(jvlibProvideer.search, code))

        completed, _ = concurrent.futures.wait(
            executors_list,
            return_when=concurrent.futures.FIRST_COMPLETED,
        )

        for task in completed:
            result = task.result()
            if "statusCode" in result:
                continue

            return result
