import re
def filter_string(name):
    """Filter string."""
    patterns = [r'[@|-|_]?[a-zA-Z_0-9]+(\.com|\.net|\.tk)[_|-]?',
                '^_',
                '^[0-9]{4}',
                '069-3XPLANET-',
                'Watch18plus-',
                r'\[(.*?)\]',
                '^@',
                '[a-zA-Z]$',
                '-[a-zA-Z]$',
                'hhd800@',
                'FHD-',
                'FHD_',
                'HD_',
                'fhd',
                'Watch ',
                '-h264',
                '_4K',
                r'\.(?!part|pt|cd).*$',
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
                r'\.HD',
                '-HD',
                '_',
                r'-$',]

    for pattern in patterns:
        name = re.sub(pattern, '', name)

    name = list(name)
    for char in name:
        if not char.isalpha() \
                and not char.isdigit() \
                and char != '-':
            name.remove(char)

    return ''.join(name)


if __name__ == '__main__':
    print(filter_string('EBOD-304-C'))
