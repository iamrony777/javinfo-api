import json
from providers import Javdatabase, R18, Javlibrary
import concurrent.futures

r18Provider = R18()
jvdtbsProvider = Javdatabase()
jvlibProvideer = Javlibrary()

#TODO: all of these providers has a common method `search`. Now create a function which searches all of them using python's `concurrent.futures`. and make the logic like this, whichever provider returns the result first, then return it. dont wait for other providers to finish. if this is not possible with `concurrent.futures` then you're free to use other libraries.

def search_all_providers(code: str):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the search tasks to the executor
        r18_search = executor.submit(r18Provider.search, code)
        jvdtbs_search = executor.submit(jvdtbsProvider.search, code)
        jvlib_search = executor.submit(jvlibProvideer.search, code)

        # Wait for any of the tasks to complete
        completed, _ = concurrent.futures.wait(
            [r18_search, jvdtbs_search, jvlib_search],
            return_when=concurrent.futures.ALL_COMPLETED
        )

        # Get the result from the completed task
        for task in completed:
            result = task.result()
            if "statusCode" in result:
                continue
            return result

if __name__ == "__main__":
    # Call the function to perform the search
    result = search_all_providers(code="EBOD-875")
    print(result)