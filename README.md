# javinfo-api

> **This project has moved.** `javinfo-api` has been handed over to the **[JAVINFO](https://github.com/javinfo)** organization, where it is being rebuilt and actively developed.

The original code that lived here (the pre-2024 Python/FastAPI version) has been archived. Development now continues under the JAVINFO org as a new, faster, rewritten service.

## 👉 Use the new service: **[javinfo.eu.org](https://javinfo.eu.org)**

**javinfo** is metadata and magnet search for JAV releases. Send a DVD ID (e.g. `SSIS-001`, `CAWD-001`) and get back one clean JSON object — title, cast, maker, series, cover art, runtime, and (on paid plans) download / magnet links. Results are cached server-side, so repeated lookups are fast.

- 🌐 **Web app:** [javinfo.eu.org](https://javinfo.eu.org)
- 🧩 **Org / new repos:** [github.com/javinfo](https://github.com/javinfo)
- ⚡ **API:** single `POST /search` endpoint, available on RapidAPI

```bash
curl -X POST 'https://javinfo-search.p.rapidapi.com/search' \
  -H 'Content-Type: application/json' \
  -H 'X-RapidAPI-Key: YOUR_RAPIDAPI_KEY' \
  -H 'X-RapidAPI-Host: javinfo-search.p.rapidapi.com' \
  -d '{ "q": "SSIS-001" }'
```

---

Thanks to everyone who starred and used the original `javinfo-api`. The new build at **[javinfo.eu.org](https://javinfo.eu.org)** carries it forward. 🙏
