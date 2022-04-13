# JavInfo - `API to fetch JPN AV info`

> Deploy

    - Procfile
    web: python3 main.py

    - PORT default 8000  

- Railway
    
    `MONGODB_URL` : to fetch `JAVDB_COOKIES` and `HEADERS (optional)`
    
    `PORT` : 8000

- Heroku 

    `MONGODB_URL` : to fetch `JAVDB_COOKIES` and `HEADERS (optional)`

    edit [main.py](https://github.com/iamrony777/JavInfo-api/blob/02b278777cedf6462121e112ff5e1691099c31ba/main.py#L64)
    
    ```port = os.environ['PORT]```

> Docs

Swagger API Docs : `/docs`

> Providers

- [Javdb.com](https://javdb.com/)
- [Javlibrary.com](https://www.javdatabase.com/)
- [Javdatabase.com](https://www.javlibrary.com/)