
![Logo](./src/img/logo.png)


<b>JAVINFO API | Backend for JAVINFO CLI</b>


| Provider                                        | Query  | Actress Data    | Movie Data  | Image Data  | Screenshots  |
|------------------------------------------------ |------- |---------------- |------------ |------------ |------------  |
| [Javdb](https://javdb.com/)                     | Y      | N               | Y           | Y           |  N           |
| [Javlibrary](https://www.javdatabase.com/)      | Y      | Y               | Y           | N           |  N           |
| [Javdatabase](https://www.javlibrary.com/)      | Y      | Y               | Y           | Y           |  N           |
| [r18](http://r18.com/)    (Default)             | Y      | Y               | Y           | Y           |  Y           |
| [Boobpedia](https://www.boobpedia.com/)         | N      | Y               | N           | Y           |  N           |

<br>

___
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cb1802908a6e419a946e1f7f163d2055)](https://app.codacy.com/gh/iamrony777/JavInfo-api?utm_source=github.com&utm_medium=referral&utm_content=iamrony777/JavInfo-api&utm_campaign=Badge_Grade_Settings)
[![READ DOCS](https://img.shields.io/badge/READ-DOCS-blueviolet?style=for-the-badge&logo=data:image/png;base64,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)](https://javinfo-api.up.railway.app/docs)
[![DEMO/MONITOR](https://img.shields.io/website?down_color=red&down_message=API%20IS%20DOWN&label=JAVINFO-API&logo=railway&style=for-the-badge&up_color=darkviolet&up_message=TRY%20DEMO%20%21&url=https://javinfo-api.up.railway.app%2Fcheck)](https://javinfo-api.up.railway.app/demo)
![VERSION](https://img.shields.io/endpoint?url=https://javinfo-api.up.railway.app/version)

---
[![wakatime](https://wakatime.com/badge/user/b5fd871e-e348-4c6e-9ae5-306590243750/project/5ccc4d18-5f78-4674-bd77-57a94ae53215.svg?style=for-the-badge)](https://wakatime.com/badge/user/b5fd871e-e348-4c6e-9ae5-306590243750/project/5ccc4d18-5f78-4674-bd77-57a94ae53215)
