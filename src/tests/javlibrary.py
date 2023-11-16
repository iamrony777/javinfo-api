import pytest
import json
from src.providers import Javlibrary

# Define the codes to test
codes = ["ebod-391", "ssis-100", "doa-017", "ssis-001"]
provider = Javlibrary()


@pytest.mark.parametrize("code", codes)
def test_javlibrary(code: str):
    # Load the expected result from the json file
    with open(f"src/tests/data/r18.{code}.json", "r") as f:
        expected_result: str = f.read().strip()

    # Run the search function and get the result
    result = json.dumps(provider.search(code.upper()), indent=2, ensure_ascii=False)

    # Compare the result with the expected result
    assert (
        result == expected_result
    ), f"For code: {code}, expected: {expected_result}, but got: {result}"


# pytest.main(["-x", __file__])
