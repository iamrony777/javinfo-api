![javinfo](https://javinfo.dev/apple-touch-icon.png/?ref=github.com)

# javinfo-api

> **This project has moved.** `javinfo-api` has been handed over to the **[JAVINFO](https://github.com/javinfo)** organization, where it is being rebuilt and actively developed.

The original code that lived here (the pre-2024 Python/FastAPI version) has been archived. Development now continues under the JAVINFO org as a new, faster, rewritten service.

## Use the new service: **[javinfo.dev](https://javinfo.dev)**

**javinfo** is metadata and magnet search for JAV releases. Send a DVD ID (e.g. `SSIS-001`, `CAWD-001`) and get back one clean JSON object — title, cast, maker, series, cover art, runtime, and download/magnet links. Results are cached server-side, so repeated lookups are fast.

- **Web app:** [javinfo.dev](https://javinfo.dev)
- **Get a key / billing:** [app.javinfo.dev](https://app.javinfo.dev)
- **Company / new repos:** [github.com/javinfo](https://github.com/javinfo)
- **API host:** `https://api.javinfo.dev`

$50+ top-ups get 5--50% bonus. No charge on non-200 responses.

### Two endpoints

| Endpoint | What it does | Cost |
|----------|--------------|------|
| `POST /movie` | Single best match for a DVD ID | $0.001/success |
| `POST /query` | List of matching releases | $0.0002/call |

### Quick start

**curl:**
```bash
curl -X POST "https://api.javinfo.dev/movie" \
  -H "x-javinfo-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "q": "SSIS-001" }'
```

**JavaScript (fetch):**
```js
const res = await fetch("https://api.javinfo.dev/movie", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-javinfo-key": "YOUR_KEY",
  },
  body: JSON.stringify({ q: "CAWD-001" }),
});
const data = await res.json();
```

**Python (requests):**
```python
import requests

res = requests.post(
    "https://api.javinfo.dev/movie",
    headers={"x-javinfo-key": "YOUR_KEY"},
    json={"q": "CAWD-001"},
)
data = res.json()
```

### Providers

All providers are available on every tier. No content gating.

| Provider | Data |
|----------|------|
| `r18` | Bilingual metadata, covers, trailers, gallery |
| `javdb` | Metadata + magnet / PikPak download links |
| `missav` | Metadata + HLS stream URLs (.m3u8) |
| `javdatabase` | Metadata + descriptions, sample images, trailers |
| `javlibrary` | Coming soon |

### Auth

Send your app key in the `x-javinfo-key` header. (On RapidAPI, use `X-RapidAPI-Key` + `X-RapidAPI-Host` instead; javinfo is also available there.)

---

Thanks to everyone who starred and used the original `javinfo-api`. The new build at **[javinfo.dev](https://javinfo.dev)** carries it forward.
