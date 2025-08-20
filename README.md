# weewx AmbientWeather API Driver

![Version](https://img.shields.io/github/v/release/themoosman/weewx-ambientweatherapi-json?sort=semver)
[![Linux CI](https://github.com/themoosman/weewx-ambientweatherapi-json/workflows/Linux%20CI/badge.svg)](https://github.com/themoosman/weewx-ambientweatherapi-json/actions?query=workflow%3A%22Linux+CI%22)
![Lint](https://github.com/themoosman/weewx-ambientweatherapi-json/workflows/flake8%20Lint/badge.svg)

This is an AmbientWeather API driver for weewx.  This will work with any AmbientWeather stations that uploads data to ambientweather.net.  I decided to go this route as the only way to get access to some infomration is via the Ambinent Weather API.  Since I have a number of external temperature sensors I wrote this driver so I could pull that data into weewx.

This driver uses the [AmbientAPI](https://github.com/avryhof/ambient_api) Python3 package to make the API calls.

This driver only works with Weewx 4.0+ and Python3.

## Install

1) Install the necessary Python packages
````bash
sudo -H pip3 install -r requirements.txt
````

2) Install the extension
````bash
weectl extension install https://github.com/themoosman/weewx-ambientweatherapi-json/archive/master.zip --yes
````

3) Modify `weewx.conf` using the snippets in this repo's `weeex.conf`
4) Restart `weewx`

## weewx.conf Overview

The following table outlines the `weewx.conf` station variables.

| Variable | Description |
| --- | --- |
| loop_interval | How often the driver will make an API call.  Be careful as Ambient Weather has [limits](https://ambientweather.docs.apiary.io/#) |
| api_url | Ambient Weather API endpoint.  You probably don't need to change this. |
| api_app_key | API Application Key from your ambientweather.net [website](https://ambientweather.docs.apiary.io/#) |
| api_key | API Key from your ambientweather.net [website](https://ambientweather.docs.apiary.io/#) |
| hardware | String to identify the hardware used |
| driver | Don't change this value |
| aw_debug | Optional:  Set to `1` to get verbose output from the Ambient API.  The default value is `0` |
| use_meteobridge | Optional: Set to `True` if using Meteobridge, `False` is the default or leave commented out |
| station_mac | Optional: Specify a specific station MAC address to return data.  If blank or unspecified, then the first station in the list is returned. |