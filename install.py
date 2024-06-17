# Distributed under the terms of the GNU Public License (GPLv3)

from weecfg.extension import ExtensionInstaller


def loader():
    return AmbientWeatherApiInstaller()


class AmbientWeatherApiInstaller(ExtensionInstaller):
    def __init__(self):
        super(AmbientWeatherApiInstaller, self).__init__(
            version="0.0.12",
            name='ambientweatherapi',
            description='WeeWx AmbientWeather API Driver.',
            author="Karl Moos",
            config={
                'ambientweatherapi': {
                    'driver': 'user.ambientweatherapi',
                    'loop_interval': '120',
                    'api_url': 'https://api.ambientweather.net/v1',
                    'api_app_key': 'xxxxxx',
                    'api_key': 'xxxxxx',
                    'hardware': 'My Weather Station'}},
            files=[('bin/user', ['bin/user/ambientweatherapi.py'])]
        )
