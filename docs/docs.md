##  Quick Preview

|     Provider    |       Query      |   Actress Data   |    Movie Data    | Screenshots      |
|:---------------:|:----------------:|:----------------:|:----------------:|------------------|
|     `javdb`     | :material-check: | :material-close: | :material-check: | :material-close: |
|   `javlibrary`  | :material-check: | :material-check: | :material-check: | :material-close: |
|  `javdatabase`  | :material-check: | :material-check: | :material-check: | :material-close: |
| `r18` (default) | :material-check: | :material-check: | :material-check: | :material-check: |
|    Boobpedia    | :material-close: | :material-check: | :material-close: | :material-close: |


----
# Request Examples

### Using [HTTPie](https://httpie.io/)

=== "ID"

    ```bash
    https --auth "${API_USER}:${API_PASS}" \
    POST javinfo-api.up.railway.app/search \
    id==JAV_ID
    ```
=== "ID , Provider"

    ```bash
    https --auth "${API_USER}:${API_PASS}" \
    POST javinfo-api.up.railway.app/search \
    id==JAV_ID provider=PROVIDER
    ```

----

### Using [cURL]()

=== "ID"

    ```bash
    curl -X "POST" "https://javinfo-api.up.railway.app/search?id=JAV_ID" \
        --header "Accept: application/json" \
        --user "${API_USER}:${API_PASS}"
    ```

=== "ID , Provider"

    ```bash
    curl -X "POST" "https://javinfo-api.up.railway.app/search?id=JAV_ID&provider=PROVIDER" \
        --header "Accept: application/json" \
        --user "${API_USER}:${API_PASS}"
    ```

----
#### Query parameters 

__id__=_JAV_ID_ `required`

__provider__=_PROVIDER_ `optional`


- `JAV_ID` example = `EBOD-391` / `ebod00391` / `ebod-391` / `ebod391`

- `PROVIDER` example = `javdb` / `javlibrary` / `javdatabase` / `r18` (default)


----
# Response


```json

{
  "id": "EBOD-391",
  "title": "Real Breast Milk Married Woman - Ema Kisaki",
  "poster": "https://pics.r18.com/digital/video/ebod00391/ebod00391pl.jpg",
  "extra_details": {
    "Director": "Hao * Minami",
    "Release Date": "2014-08-09",
    "Runtime": "119",
    "Studio": "E-BODY"
  },
  "actress": [
    {
      "name": "Ema Kisaki",
      "image": "https://www.boobpedia.com/wiki/images/6/64/Ema_Kisaki.jpg",
      "image2": "https://pics.r18.com/mono/actjpgs/kisaki_ema.jpg",
      "details": {
        "Also known as": "Haruki Kato, HARUKI",
        "Born": "August 30, 1989 (1989-08-30) (age 32)",
        "Ethnicity": "Asian",
        "Nationality": "Japanese",
        "Measurements": "95-62-89cm",
        "Bra/cup size": "G metric",
        "Boobs": "Enhanced",
        "Height": "1.52 m (4 ft 12 in)",
        "Weight": "47 kg (103 lb)",
        "Body type": "Slim",
        "Eye color": "Black",
        "Hair": "Brown, Blonde",
        "Blood group": "A",
        "Shown": "Topless, Bush, Full frontal, Pink",
        "Solo": "Masturbation, Dildo",
        "Girl/girl": "Softcore, Dildo, Fisting",
        "Boy/girl": "Blowjob, Vaginal, Anal, Double penetration, Fisting",
        "Special": "Bondage, Watersports"
      }
    }
  ],
  "screenshots": [
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-1.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-2.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-3.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-4.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-5.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-6.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-7.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-8.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-9.jpg",
    "https://pics.r18.com/digital/video/ebod00391/ebod00391jp-10.jpg"
  ]
}
```

