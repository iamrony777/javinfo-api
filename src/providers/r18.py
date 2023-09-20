from src.providers import CustomSession


class R18:
    def __init__(self, base_url: str = "https://r18.dev") -> None:
        self.base_url = base_url
        self.client = CustomSession(base_url=base_url)

    def __getJsonResult(self, data: dict[str]):
        result = {"id": data["dvd_id"]}
        result["title"] = data["title_en"]
        result["title_ja"] = data["title_ja"]
        result[
            "page"
        ] = f"https://r18.dev/videos/vod/movies/detail/-/id={data['content_id']}/"
        result["poster"] = data.get("jacket_full_url", None)
        result["preview"] = data.get("sample_url", None)

        ## result.details
        result["details"] = {
            "director": None,
            "release_date": None,
            "runtime": None,
            "studio": None,
        }

        result["details"]["director"] = (
            data["directors"][0]["name_romaji"] if data["directors"] else None
        )
        result["details"]["release_date"] = data.get("release_date", None)
        result["details"]["runtime"] = data.get("runtime_mins", None)
        result["details"]["studio"] = data.get("maker_name_en", None)

        
        return result

    def search(self, code: str):
        resp = self.client.get(url=f"/videos/vod/movies/detail/-/dvd_id={code}/json")
        if resp.ok:
            resp = self.client.get(
                url=f"/videos/vod/movies/detail/-/combined={resp.json()['content_id']}/json"
            )
            return self.__getJsonResult(resp.json())
        else:
            return {"statusCode": resp.status_code}


if __name__ == "__main__":
    print(R18().search("EBOD-391"))
