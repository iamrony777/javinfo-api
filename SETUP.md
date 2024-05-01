# Using pipenv [source](https://pipenv.pypa.io/en/latest/)


```bash
pip install --user pipenv
```


# basic structure explaination

```bash
src/api -> api related folder (e.g. routers, auths)
src/providers -> basically websracpers
src/common -> commonly used modules
sr/app.py
```

# misc
file: `.env`

```env
PRIORITY_LIST="['r18', 'jvdtbs', 'jvlib', 'javdb']"

# proxy config (currently only javlibrary uses proxy)
HTTP_PROXY=""
HTTPS_PROXY=""
```
# javdb.com cookies

1. Login into javdb.com
2. Open developer tools (Right click -> Inspect / Ctrl + Shift + I )
3. Navigate to Storage -> Cookies -> `https://javdb.com`
4. Now copy `_jdb_session` and `remember_me_token` key's values save in corresponding environment variables

```env
JDB_SESSION=""
REMEMBER_ME_TOKEN=""
```

* Remeber to copy decoded values
![show url decoded](./images/show-url-decoded.png)