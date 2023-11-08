# Distributed under the terms of the GNU Public License (GPLv3)

from weecfg.extension import ExtensionInstaller


def loader():
    return AmbientWeatherApiInstaller()


class AmbientWeatherApiInstaller(ExtensionInstaller):
    def __init__(self):
        super(AmbientWeatherApiInstaller, self).__init__(
            version="0.0.8",
            name='ambientweatherapi',
            description='WeeWx AmbientWeather API Driver.',
            author="Karl Moos",
            restful_services='user.ambientweatherapi.AmbientWeatherAPI',
            files=[('bin/user', ['bin/user/ambientweatherapi.py'])]
        )
