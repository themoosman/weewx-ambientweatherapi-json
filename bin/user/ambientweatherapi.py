""" weewx Driver for the Ambient Weather API

    Karl Moos
    https://github.com/themoosman

"""

from __future__ import with_statement
from ambient_api.ambientapi import AmbientAPI
import time
import syslog
import logging
import weedb
import weewx.drivers
import weeutil.weeutil
import weewx.wxformulas
import tempfile
import os.path
from os import path

DRIVER_NAME = 'ambientweatherapi'
DRIVER_VERSION = '0.0.10'


def loader(config_dict, engine):
    station = AmbientWeatherAPI(**config_dict[DRIVER_NAME])
    return station


class AmbientWeatherAPI(weewx.drivers.AbstractDevice):
    """Custom driver for Ambient Weather API."""

    def __init__(self, **stn_dict):
        rainfile = "%s_%s_rain.txt" % (DRIVER_NAME, DRIVER_VERSION)
        self.log_file = stn_dict.get('log_file', None)
        self.loop_interval = float(stn_dict.get('loop_interval', 60))
        self.log_level = stn_dict.get('log_level', 'ERROR')

        if self.log_file and self.log_level != 'console':
            logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s',
                                filemode='w',
                                filename=self.log_file,
                                level=getattr(logging, self.log_level.upper(), 'ERROR'))

        self.api_url = stn_dict.get('api_url', 'https://api.ambientweather.net/v1')
        self.api_key = stn_dict.get('api_key')
        self.api_app_key = stn_dict.get('api_app_key')
        self.station_hardware = stn_dict.get('hardware', 'Undefined')
        self.safe_humidity = float(stn_dict.get('safe_humidity', 60))
        self.max_humidity = float(stn_dict.get('max_humidity', 38))
        self.use_meteobridge = bool(stn_dict.get('use_meteobridge', False))
        logging.info('use_meteobridge: %s' % str(self.use_meteobridge))
        self.station_mac = stn_dict.get('station_mac', '')
        self.use_station_mac = False
        if not self.station_mac:
            logging.info("No Station MAC specified.")
        else:
            self.use_station_mac = True
        self.rainfilepath = os.path.join(tempfile.gettempdir(), rainfile)
        logging.info('Starting: %s, version: %s' % (DRIVER_NAME, DRIVER_VERSION))
        logging.debug("Exiting init()")

    @property
    def hardware_name(self):
        """Returns the type of station."""
        logging.debug("calling: hardware_name")
        return self.station_hardware

    @property
    def archive_interval1(self):
        """Returns the archive internal."""
        logging.debug("calling: archive_interval")
        return self.loop_interval

    def calc_target_humidity(self, external_temp_f):
        """Converts the optimal indoor humidity.  Drop target humidity 5% for every 5degree C drop below 0"""
        external_temp_c = (external_temp_f - 32) * 5.0 / 9.0
        if external_temp_c >= 0:
            return self.max_humidity
        else:
            target = max(0, self.max_humidity + external_temp_c)
            if external_temp_c <= -15:
                target = target + 2.5
            if external_temp_c <= -20:
                target = target + 2.5
            if external_temp_c <= -25:
                target = target + 2.5
            if external_temp_c <= -30:
                target = target + 2.5
            return target

    def convert_epoch_ms_to_sec(self, epoch_ms):
        """Converts a epoch that's in ms to sec.
        AmbientAPI returns the epoch time in ms not sec"""
        logging.debug("calling: convert_epoch_ms_to_sec")
        utc_epoch_sec = epoch_ms / 1000
        return utc_epoch_sec

    def print_dict(self, data_dict):
        """Prints a dict."""
        if logging.DEBUG >= logging.root.level:
            logging.debug("calling: print_dict")
            for key in data_dict:
                logging.debug(key + " = " + str(data_dict[key]))

    def get_value(self, data_dict, key):
        """Gets the value from a dict, returns None if the key does not exist."""
        if logging.DEBUG >= logging.root.level:
            logging.debug("calling: get_value")
        return data_dict.get(key, None)

    def get_float(self, value):
        """Checks if a value is not, if not it performs a converstion to a float()"""
        # logging.debug("calling: get_float")
        if value is None:
            return value
        else:
            return float(value)

    def get_battery_status(self, value):
        """Converts the AM API battery status to somthing weewx likes."""
        # logging.debug("calling: get_battery_status")
        if value is None:
            return None
        if (value <= 0):
            if self.use_meteobridge:
                logging.debug("use_meteobridge flip bit to 0.0")
                return 0.0
            else:
                return 1.0
        else:
            if self.use_meteobridge:
                logging.debug("use_meteobridge flip bit to 1.0")
                return 1.0
            else:
                return 0.0

    def check_rain_rate(self, dailyrainin):
        """Read previous daily rain total, and write most recent daily rain back to file"""
        correctedRain = dailyrainin
        try:
            if path.exists(self.rainfilepath):
                logging.debug('Opening file: %s' % (self.rainfilepath))
                intervalRain = open(self.rainfilepath, 'r')
                try:
                    lastRain = float(intervalRain.read())
                except ValueError:
                    logging.error('String value found. Assuming zero interval rain and recording current value')
                    lastRain = dailyrainin
                intervalRain.close()
                logging.debug('Previous daily rain: %s' % str(lastRain))
            else:
                logging.debug('No previous value found for rain, assuming interval of 0 and recording daily value')
                lastRain = dailyrainin

            logging.debug('Reported daily rain: %s' % str(dailyrainin))

            if lastRain > dailyrainin:
                correctedRain = dailyrainin
                logging.debug('Recorded rain is more than reported rain; using reported rain')
            else:
                correctedRain = dailyrainin - lastRain
                # temp
                # logging.info('Previous daily rain: %s' % str(lastRain))
                # logging.info('Reported daily rain: %s' % str(dailyrainin))
                # logging.info('Calculated interval rain: %s' % str(correctedRain))

            logging.debug('Calculated interval rain: %s' % str(correctedRain))
            intervalRain = open(self.rainfilepath, 'w')
            intervalRain.write(str(dailyrainin))
            intervalRain.close()

        except Exception as e:
            logging.error("%s driver, function: %s encountered an error." % (DRIVER_NAME, "check_rain_rate"))
            logging.error("Error caught was: %s" % e)
        finally:
            return correctedRain

    def get_packet_mapping(self):
        """Gets the mapping of weewx values (key) to AmbientAPI values (value)."""
        return {
            'barometer': 'baromrelin',
            'batteryStatus1': 'batt1',
            'batteryStatus2': 'batt2',
            'batteryStatus3': 'batt3',
            'batteryStatus4': 'batt4',
            'batteryStatus5': 'batt5',
            'batteryStatus6': 'batt6',
            'batteryStatus7': 'batt7',
            'batteryStatus8': 'batt8',
            'batt1': 'batt1',
            'batt2': 'batt2',
            'batt3': 'batt3',
            'batt4': 'batt4',
            'batt5': 'batt5',
            'batt6': 'batt6',
            'batt7': 'batt7',
            'batt8': 'batt8',
            'batt_25': 'batt_co2',
            'co2': 'co2_in_aqin',
            'co2_24': 'co2_in_24h_aqin',
            'dewPoint': 'dewPoint',
            'dewPointin': 'dewPointin',
            'extraDewpoint1': 'dewPoint1',
            'extraDewpoint2': 'dewPoint2',
            'extraDewpoint3': 'dewPoint3',
            'extraDewpoint4': 'dewPoint4',
            'extraDewpoint5': 'dewPoint5',
            'extraDewpoint6': 'dewPoint6',
            'extraDewpoint7': 'dewPoint7',
            'extraDewpoint8': 'dewPoint8',
            'extraHumid1': 'humidity1',
            'extraHumid2': 'humidity2',
            'extraHumid3': 'humidity3',
            'extraHumid4': 'humidity4',
            'extraHumid5': 'humidity5',
            'extraHumid6': 'humidity6',
            'extraHumid7': 'humidity7',
            'extraHumid8': 'humidity8',
            'extraTemp1': 'temp1f',
            'extraTemp2': 'temp2f',
            'extraTemp3': 'temp3f',
            'extraTemp4': 'temp4f',
            'extraTemp5': 'temp5f',
            'extraTemp6': 'temp6f',
            'extraTemp7': 'temp7f',
            'extraTemp8': 'temp8f',
            'feelsLike': 'feelsLike',
            'feelsLikein': 'feelsLikein',
            'feelsLike1': 'feelsLike1',
            'feelsLike2': 'feelsLike2',
            'feelsLike3': 'feelsLike3',
            'feelsLike4': 'feelsLike4',
            'feelsLike5': 'feelsLike5',
            'feelsLike6': 'feelsLike6',
            'feelsLike7': 'feelsLike7',
            'feelsLike8': 'feelsLike8',
            'inDewpoint': 'dewPointin',
            'inHumidity': 'humidityin',
            'inTemp': 'tempinf',
            'inTempBatteryStatus': 'battin',
            'leafWet1': 'leafwetness1',
            'leafWet2': 'leafwetness2',
            'lightning_distance': 'lightning_distance',
            'lightning_disturber_count': 'lightning_time',
            'lightning_noise_count': 'lightning_day',
            'lightning_strike_count': 'lightning_hour',
            'outHumidity': 'humidity',
            'outTemp': 'tempf',
            'outTempBatteryStatus': 'battout',
            'pm2_5_aqi': 'aqi_pm25_aqin',
            'pm2_5': 'pm25_in_aqin',
            'pm10_0_aqi': 'aqi_pm10_aqin',
            'pm10_0': 'pm10_in_aqin',
            'pm2_5_24': 'pm25_in_24h_aqin',
            'pm10_0_24': 'pm10_in_24h_aqin',
            'pm2_5_aqi_24': 'aqi_pm25_24h_aqin',
            'appTemp1': 'pm_in_temp_aqin',
            'humidex1': 'pm_in_humidity_aqin',
            'pressure': 'baromabsin',
            'radiation': 'solarradiation',
            'rainRate': 'hourlyrainin',
            'soilMoist1': 'soilhum1',
            'soilMoist2': 'soilhum2',
            'soilMoist3': 'soilhum3',
            'soilMoist4': 'soilhum4',
            'soilMoist5': 'soilhum5',
            'soilMoist6': 'soilhum6',
            'soilMoist7': 'soilhum7',
            'soilMoist8': 'soilhum8',
            'soilTemp1': 'soiltemp1f',
            'soilTemp2': 'soiltemp2f',
            'soilTemp3': 'soiltemp3f',
            'soilTemp4': 'soiltemp4f',
            'windDir': 'winddir',
            'windGust': 'windgustmph',
            'windSpeed': 'windspeedmph',
            'UV': 'uv'
        }

    def genLoopPackets(self):
        logging.debug("calling: genLoopPackets")

        while True:
            # Query the API to get the latest reading.
            try:
                error_occured = False
                logging.debug("starting getLoopPackets")

                # Adding an extra buffer so the API throttle limit isn't hit
                logging.debug("sleeping an extra 3 seconds to not hit API throttle limit.")
                time.sleep(3)

                # init the API
                weather = AmbientAPI(AMBIENT_ENDPOINT=self.api_url,
                                     AMBIENT_API_KEY=self.api_key,
                                     AMBIENT_APPLICATION_KEY=self.api_app_key)
                logging.debug("Init API call returned")

                # get the first device
                devices = weather.get_devices()
                logging.debug("Got weather devices")
                if not devices:
                    logging.error('AmbientAPI get_devices() returned empty dict')
                    raise Exception('AmbientAPI get_devices() returned empty dict')
                else:
                    logging.debug('Weather get_devices() payload not empty')

                # get the last report dict
                data = devices[0].last_data
                if self.use_station_mac:
                    logging.debug('Looking for specific Station MAC')
                    for device in devices:
                        if device.macAddress == self.station_mac:
                            logging.info("Found station mac: %s", self.station_mac)
                            data = device.last_data
                            break
                        else:
                            logging.debug('No specific MAC specified, using first station.')
                # info = devices[0].info
                logging.debug("Got last report")

                # Convert the epoch to the format weewx wants.
                current_observation = self.convert_epoch_ms_to_sec(data["dateutc"])

                # output the observation
                self.print_dict(data)

            except Exception as e:
                syslog.syslog(DRIVER_NAME + " driver encountered an error.")
                logging.error(DRIVER_NAME + " driver encountered an error.")
                syslog.syslog("Error caught was: %s" % e)
                logging.error("Error caught was: %s" % e)
                error_occured = True

            # build the packet data
            try:
                logging.debug("============Starting Packet Build============")
                if error_occured:
                    error_occured = False
                    raise Exception('Previous error occured, skipping packet build.')

                dailyrainin = 0.0
                # Check the API for dai
                if 'dailyrainin' in data.keys():
                    dailyrainin = self.get_float(data['dailyrainin'])

                # Create the initial packet dict
                _packet = {
                    'dateTime': current_observation,
                    'usUnits': weewx.US,
                    'rain': self.check_rain_rate(dailyrainin),
                }

                # Key is weewx packet, value is Ambient value
                # Loop the values in the mapping and look for actual values in the API data
                mapping = self.get_packet_mapping()
                for key, value in mapping.items():
                    is_battery = value.startswith('batt')
                    if value in data:
                        logging.debug("Setting Weewx value: '%s' to: %s using Ambient field: '%s'" %
                                      (key, str(data[value]), value))
                        if is_battery:
                            _packet[key] = self.get_battery_status(data[value])
                        else:
                            _packet[key] = self.get_float(data[value])
                    else:
                        logging.debug("Dropping Ambient value: '%s' from Weewx packet." % (value))

                self.print_dict(_packet)
                logging.debug("============Completed Packet Build============")
                yield _packet
                logging.info("loopPacket Accepted")
            except Exception as e:
                syslog.syslog(DRIVER_NAME + " driver had an error sending data to weewx.")
                logging.error(DRIVER_NAME + " driver had an error sending data to weewx.")
                syslog.syslog("Error caught was: %s" % e)
                logging.error("Error caught was: %s" % e)

            # Sleepy Time
            logging.debug("Going to sleep")
            time.sleep(self.loop_interval)
            logging.debug("Mom, I'm up!")


if __name__ == "__main__":
    driver = AmbientWeatherAPI()
    for packet in driver.genLoopPackets():
        print(weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet)
