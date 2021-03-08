![](https://github.com/themoosman/weewx-ambientweatherapi-json/workflows/flake8%20Lint/badge.svg)
# weewx AmbientWeather API Driver

This is an AmbientWeather API driver for weewx.  This will work with any AmbientWeather stations that uploads data to ambientweather.net.  I decided to go this route as the only way to get access to some infomration is via the Ambinent Weather API.  Since I have a number of external temperature sensors I wrote this driver so I could pull that data into weewx.

This driver uses the [AmbientAPI](https://github.com/avryhof/ambient_api) Python3 package to make the API calls.

This driver only works with Weewx 4.0+ and Python3.

## Install

1) Install the necessary Python packages
````bash
sudo -H pip3 install -r requirements.txt
````

2) Copy `bin/user/ambientweatherapi.py` to the `bin/user` directory.  The directory location depends on your install type.  See [here](http://www.weewx.com/docs/) for more informaiton.
3) Modify `weewx.conf` using the snippets in this repo's `weeex.conf`
4) Restart `weewx`

## weewx.conf Overview

The following table outlines the `weewx.conf` station variables.

| Variable | Description |
| --- | --- |
| loop_interval | How often the driver will make an API call.  Becareful as Ambient Weather has [limits](https://ambientweather.docs.apiary.io/#) |
| log_level | Driver log level  |
| log_file | Location where the driver will log data.  This can be `None` |
| api_url | Ambient Weather API endpoint.  You probably don't need to change this. |
| api_app_key | API Application Key from your ambientweather.net [website](https://ambientweather.docs.apiary.io/#) |
| api_key | API Key from your ambientweather.net [website](https://ambientweather.docs.apiary.io/#) |
| use_meteobridge | Set to `True` if using Meteobridge, `False` is the default |
| hardware | String to identify the hardware used |
| driver | Don't change this value |

## TODO
1) Automate the install using `wee_extension`
