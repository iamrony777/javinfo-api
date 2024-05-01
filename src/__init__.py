import ast
# import json
from src.providers import Javdatabase, R18, Javlibrary, Javdb
import concurrent.futures
import os
# import logging

if os.path.isfile(".env"):
    from dotenv import load_dotenv

    load_dotenv(".env")

r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()
javdbProvider = Javdb()

priority = {
    "r18": 1,
    "jvdtbs": 2,
    "jvlib": 3,
    "javdb": 4,
}


def search_all_providers(code: str, provider: str = "all"):
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
            if (
                os.getenv("PRIORITY_LIST") is not None
                and os.getenv("PRIORITY_LIST") != ""
            ):
                print("Using priority list: " + os.getenv("PRIORITY_LIST"))
                providers = ast.literal_eval(os.getenv("PRIORITY_LIST"))
            else:
                print("Using default priority list")
                providers = sorted(priority.keys(), key=lambda x: priority[x])

            for provider in providers:
                if provider == "r18":
                    executors_list.append(executor.submit(r18Provider.search, code))
                elif provider == "jvdtbs":
                    executors_list.append(executor.submit(jvdtbsProvider.search, code))
                elif provider == "jvlib":
                    executors_list.append(executor.submit(jvlibProvideer.search, code))
                elif provider == "javdb":
                    executors_list.append(executor.submit(javdbProvider.search, code))

        concurrent.futures.wait(
            executors_list,
            return_when=concurrent.futures.ALL_COMPLETED,
        )

        results = [future.result() for future in executors_list]

        # print(json.dumps(results, indent=2, ensure_ascii=False))

        if results:
            for result in results:
                if "statusCode" not in result:
                    return result
            return results[0]
