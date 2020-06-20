""" weewx Driver for the Ambient Weather API

	Karl Moos
	https://github.com/themoosman

"""

from __future__ import with_statement
from ambient_api.ambientapi import AmbientAPI
import time
import json
import syslog
import logging
import weedb
import weewx.drivers
import weeutil.weeutil
import weewx.wxformulas
import os.path
from os import path

this_file = os.path.join(os.getcwd(), __file__)
this_dir = os.path.abspath(os.path.dirname(this_file))
os.chdir(this_dir)

DRIVER_NAME = 'ambientweatherapi'
DRIVER_VERSION = '0.1'

def loader(config_dict, engine):
	station = AmbientWeatherAPI(**config_dict[DRIVER_NAME])
	return station

class AmbientWeatherAPI(weewx.drivers.AbstractDevice):
	"""Custom driver for Ambient Weather API."""

	def __init__(self, **stn_dict):

		self.log_file = stn_dict.get('log_file', None)
		self.loop_interval = float(stn_dict.get('loop_interval', 60))
		self.log_level = stn_dict.get('log_level', 'ERROR')

		if self.log_file and self.log_level != 'console':
				logging.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s', filemode='w', filename=self.log_file, level=getattr(logging, self.log_level.upper(), 'ERROR'))

		self.api_url = stn_dict.get('api_url', 'https://api.ambientweather.net/v1')
		self.api_key = stn_dict.get('api_key')
		self.api_app_key = stn_dict.get('api_app_key')
		self.station_hardware = stn_dict.get('hardware', 'Undefined')
		self.safe_humidity = float(stn_dict.get('safe_humidity', 60))
		self.max_humidity = float(stn_dict.get('max_humidity', 38))
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
		external_temp_c = (external_temp_f - 32) * 5.0/9.0
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
		logging.debug("calling: print_dict")
		for key in data_dict:
			logging.debug(key + " = " + str(data_dict[key]))

	def get_value(self, data_dict, key):
		"""Gets the value from a dict, returns None if the key does not exist."""
		logging.debug("calling: get_value")
		return data_dict.get(key, None)

	def get_float(self, value):
		"""Checks if a value is not, if not it performs a converstion to a float()"""
		logging.debug("calling: get_float")
		if value is None:
			return value
		else:
			return float(value)

	def get_battery_status(self, value):
		"""Converts the AM API battery status to somthing weewx likes."""
		logging.debug("calling: get_battery_status")
		if value is None:
			return None
		if (value <= 0):
			return 1.0
		else:
			return 0.0
	


	def genLoopPackets(self):
		logging.debug("calling: genLoopPackets")

		while True:
			# Query the API to get the latest reading.
			try:
				error_occured = False
				logging.debug("starting getLoopPackets")

				#Adding an extra buffer so the API throttle limit isn't hit
				logging.debug("sleeping an extra 3 seconds to not hit API throttle limit.")
				time.sleep(3)

				#init the API
				weather = AmbientAPI(AMBIENT_ENDPOINT=self.api_url, AMBIENT_API_KEY=self.api_key, AMBIENT_APPLICATION_KEY=self.api_app_key)
				logging.debug("Init API call returned")

				#get the first device
				devices = weather.get_devices()
				logging.debug("Got weather devices")

				if not devices:
					logging.error('AmbientAPI get_devices() returned empty dict')
					raise Exception('AmbientAPI get_devices() returned empty dict')
				else:
					logging.debug('Weather get_devices() payload not empty')

				#get the last report
				data = devices[0].last_data
				#info = devices[0].info
				logging.debug("Got last report")

				#Convert the epoch to the format weewx wants.
				current_observation = self.convert_epoch_ms_to_sec(data["dateutc"])

				#output the observation
				# logging.debug("Print Dict")
				# self.print_dict(data)

				##parse the Data
				#battery
				battout = self.get_battery_status(self.get_value(data, "battout"))
				battin = self.get_battery_status(self.get_value(data, "battin"))
				batt1 = self.get_battery_status(self.get_value(data, "batt1"))
				batt2 = self.get_battery_status(self.get_value(data, "batt2"))
				batt3 = self.get_battery_status(self.get_value(data, "batt3"))
				#temp
				tempf = self.get_value(data, "tempf")
				tempinf= self.get_value(data, "tempinf")
				temp1f = self.get_value(data, "temp1f")
				temp2f = self.get_value(data, "temp2f")
				temp3f = self.get_value(data, "temp3f")
				#humidity
				humidity = self.get_value(data, "humidity")
				humidityin = self.get_value(data, "humidityin")
				humidity1 = self.get_value(data, "humidity1")
				humidity2 = self.get_value(data, "humidity2")
				humidity3 = self.get_value(data, "humidity3")
				#feelsLike
				feelsLike = self.get_value(data, "feelsLike")
				feelsLikein = self.get_value(data, "feelsLikein")
				feelsLike1 = self.get_value(data, "feelsLike1")
				feelsLike2 = self.get_value(data, "feelsLike2")
				feelsLike3 = self.get_value(data, "feelsLike3")
				#dewpoint
				dewPoint = self.get_value(data, "dewPoint")
				dewPointin = self.get_value(data, "dewPointin")
				dewPoint1 = self.get_value(data, "dewPoint1")
				dewPoint2 = self.get_value(data, "dewPoint2")
				dewPoint3 = self.get_value(data, "dewPoint3")
				#pressure
				baromrelin = data["baromrelin"] #relative
				baromabsin = data["baromabsin"] #pressure
				#wind
				winddir = data["winddir"]
				windspeedmph = data["windspeedmph"]
				windgustmph = data["windgustmph"]
				maxdailygust = data["maxdailygust"]
				#solar
				solarradiation = data["solarradiation"]
				uv = data["uv"]
				#rain
				hourlyrainin = data["hourlyrainin"]
				eventrainin = data["eventrainin"]
				dailyrainin = data["dailyrainin"]
				weeklyrainin = data["weeklyrainin"]
				monthlyrainin = data["monthlyrainin"]
				#yearlyrainin = data["yearlyrainin"]
				totalrainin = data["totalrainin"]
				#other
				#pm25 = self.get_value(data, "pm25")

			except Exception as e:
				syslog.syslog(DRIVER_NAME + " driver encountered an error.")
				logging.error(DRIVER_NAME + " driver encountered an error.")
				syslog.syslog("Error caught was: %s" % e)
				logging.error("Error caught was: %s" % e)
				error_occured = True

			#build the packet data
			try:
				logging.debug("============Starting Packet Build============")
				if error_occured:
					error_occured = False
					raise Exception('Previous error occured, skipping packet build.')

				# Read previous daily rain total, and write most recent daily rain back to file
				if path.exists('rain.txt') == True:
					logging.debug('Opening file')
					intervalRain = open('rain.txt', 'r')
					try:
						lastRain = float(intervalRain.read())
					except ValueError:
						logging.debug('String value found instead. Assuming zero interval rain and recording current value')
						lastRain = self.get_float(dailyrainin)
					intervalRain.close()
					logging.debug('Previous daily rain: ', lastRain)
				else:
					logging.debug('No previous value found for rain, assuming interval of 0 and recording daily value')
					lastRain = self.get_float(dailyrainin)
				logging.debug('Reported daily rain: ', self.get_float(dailyrainin))
				if lastRain > self.get_float(dailyrainin):
					correctedRain = self.get_float(dailyrainin)
					logging.debug('Recorded rain is more than reported rain; using reported rain')
				else:
					correctedRain = self.get_float(dailyrainin) - lastRain
				logging.debug('Calculated interval rain: ', correctedRain)
				intervalRain = open('rain.txt', 'w')
				intervalRain.write(str(dailyrainin))
				intervalRain.close()

				_packet = {
					'dateTime' : current_observation,
					'usUnits' : weewx.US,
					'outTemp' : self.get_float(tempf),
					'inTemp' : self.get_float(tempinf),
					'extraTemp1' : self.get_float(temp1f),
					'extraTemp2' : self.get_float(temp2f),
					'extraTemp3' : self.get_float(temp3f),
					'outHumidity' : self.get_float(humidity),
					'inHumidity' : self.get_float(humidityin),
					'extraHumid1' : self.get_float(humidity1),
					'extraHumid2' : self.get_float(humidity2),
					'extraHumid3' : self.get_float(humidity3),
					'feelsLike' : self.get_float(feelsLike),
					'feelsLikein' : self.get_float(feelsLikein),
					'feelsLike1' : self.get_float(feelsLike1),
					'feelsLike2' : self.get_float(feelsLike2),
					'feelsLike3' : self.get_float(feelsLike3),
					'dewPoint' : self.get_float(dewPoint),
					'dewPointin' : self.get_float(dewPointin),
					'extraDewpoint1' : self.get_float(dewPoint1),
					'extraDewpoint2' : self.get_float(dewPoint2),
					'extraDewpoint3' : self.get_float(dewPoint3),
					'batt1' : self.get_float(batt1),
					'batt2' : self.get_float(batt2),
					'batt3' : self.get_float(batt3),
					'pressure' : self.get_float(baromabsin),
					'barometer' : self.get_float(baromrelin),
					'rain': correctedRain, 
					'rainRate': self.get_float(hourlyrainin),
					'windDir' : self.get_float(winddir),
					'windSpeed' : self.get_float(windspeedmph),
					'windGust' : self.get_float(windgustmph),
					'radiation' : self.get_float(solarradiation),
					'UV' : self.get_float(uv),
					'outTempBatteryStatus' : self.get_float(battout),
					'inTempBatteryStatus' : self.get_float(battin),
					#'pm25' : self.get_float(pm25)
				}
				#self.print_dict(_packet)
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
