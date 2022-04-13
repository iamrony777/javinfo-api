import re


def filter(name): # Filter the id and start search
    patterns = ['[@|-|_]?[a-zA-Z_0-9]+(\.com|\.net|\.tk)[_|-]?',
                '^_',
                '^[0-9]{4}',
                '069-3XPLANET-',
                'Watch18plus-',
                '\[(.*?)\]',
                '^@',
                'FHD-',
                'FHD_',
                'fhd',
                'Watch ',
                '-h264',
                '_4K',
                '\.(?!part|pt|cd).*$',
                '-AV',
                '_www.avcens.download',
                '_JAV.1399.net',
                '_JAV-Video.net',
                '-VIDEOAV.NET',
                '-JAVTEG.NET',
                '.hevc.',
                '.javaddiction',
                'SmallJAV',
                'AVFUL.TK',
                'INCESTING.TK',
                'javnasty.tk',
                'javhd21.com',
                'avfullhd.tk',
                '.1080p',
                '.720p',
                '.480p',
                '\.HD',
                '-HD',
                '_']
   
    for pattern in patterns:
        name = re.sub(pattern, '', name)

    name = name.split()
    for x in name:
        if x == int:
            name.remove(x)
        elif x == str:
            break
    return name[0]

