from src.providers import Javdatabase, R18, Javlibrary, Javdb
import concurrent.futures

from dotenv import load_dotenv
load_dotenv('.env')
r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()
javdbProvider = Javdb()


def search_all_providers(code: str, provider: str = "all", includeActressUrl: bool = False):
    executors_list = []


    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        if provider == "r18":
            executors_list.append(executor.submit(r18Provider.search, code))
        if provider == "jvdtbs":
            executors_list.append(executor.submit(jvdtbsProvider.search, code))
        if provider == "jvlib":
            executors_list.append(executor.submit(jvlibProvideer.search, code))
        if provider == "javdb":
            executors_list.append(executor.submit(javdbProvider.search, code))
        if provider == "all" or provider is None:
            executors_list.append(executor.submit(r18Provider.search, code))
            executors_list.append(executor.submit(jvdtbsProvider.search, code))
            executors_list.append(executor.submit(javdbProvider.search, code))

            if not includeActressUrl:
                executors_list.append(executor.submit(jvlibProvideer.search, code))

        completed, _ = concurrent.futures.wait(
            executors_list,
            return_when=concurrent.futures.ALL_COMPLETED,
        )

        for task in completed:
            result = task.result()
            if "statusCode" in result:
                continue

            return result
