import time
from key import key,keyplaces
import googlemaps
from datetime import datetime

import wx
class Functiontesting():
	def __init__(self):
		self.testPlacesEnRoute()

	def testPlacesEnRoute(self):
		f = open('dummpyplacesdata','r')
		
		for tegenstander in f.readlines():
			print tegenstander
			time.sleep(5)
			places = googlemaps.Client(keyplaces)
			plaats = places.places(tegenstander)
			if plaats['status'] == 'ZERO_RESULTS':
				print 'kan tegenstander niet vinden ' + tegenstander
				print '----------------------------------------------------------------'
				continue
			else:
				tegenstander = plaats['results'][0]['name']
				tegenstander_adress = plaats['results'][0]['formatted_address']
				print tegenstander_adress

			gmaps = googlemaps.Client(key)
			directions_result = {}
			if plaats['status'] == 'OK' or plaats['status'] == 'INLIJST':
				while tegenstander_adress != 'Netherlands':
					try:
						directions_result = gmaps.directions(self.thuisAdress,tegenstander_adress,mode="driving",region='nl') 
					except Exception:
						print 'kon ' + tegenstander_adress + ' niet vinden'
						time.sleep(2)
						numNieuwWoord = tegenstander_adress.find(' ')
						tegenstander_adress = tegenstander_adress[numNieuwWoord+1:]
						print 'nu proberen met ' + tegenstander_adress
					else:
						break
			print 'directions_result[0][legs][0][duration]: ' + str(directions_result[0]['legs'][0]['duration'])
			print 'directions_result[0][legs][0][duration][text]: ' + str(directions_result[0]['legs'][0]['duration']['text'])
			print '----------------------------------------------------------------'
		f.close()

Functiontesting()