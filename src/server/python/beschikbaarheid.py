#open-webpage.py
import googlemaps
import time

import config
import handelinputdata
from key import key, keyplaces

'''
Er wordt met tijd gerekend op een schaal van 100

'''

class Beschikbaarheid:
	def __init__(self):
		self.debug = config.debug
		#self.extractAddressFile()
		#self.addressen = self.extractAddressFile()
		#self.reistijden = self.extractReistijdenFile()

	def determineBeschikbaarheid(self):
		verzameltijd = config.verzameltijd
		wedstrijdtijd = config.wedstrijdtijd
		info = handelinputdata.Handelinputdata()

		teamLijst = self.getTeamsinHoreca()

		#lid consits of the name of the member and its team
		for team in teamLijst:
			#returns a dict with the team info gathered from the HTML file. It has the following form:
			# {'status': 'OK' v 'error', 'tegenstander': tegenstander, 'speeltijd': tijd, 'speelplek': thuis v uit, 'team': team}
			teamInfo = info.handel(team)
			if teamInfo['status'] == 'error':
				#een lege value betekent dus dat er een error is opgetreden
				continue
			#reistijd naar de tegenstander bepalen
			#if teamInfo['speelplek'] == 'uit':
			reistijd = self.getReistijd(teamInfo) 
			#speeltijd converten van string naar rekenbare tijd. v.b, 14:15 -> 1425
			speelTijd = self.speelTijdTeam(teamInfo['speeltijd'])
			#Berekenen wanneer de leden die in dit spelen niet beschikbaar zijn aan de hand van volgende formule
			nietBeschikbaar = {'begin':speelTijd - (verzameltijd + reistijd),'einde':speelTijd + wedstrijdtijd + reistijd}

			if self.debug:
				print 'begin determineBeschikbaarheid '
				print "\tniet beschikbaar van " + str(nietBeschikbaar['begin']) + " tot " + str(nietBeschikbaar['einde'])
				print 'einde determineBeschikbaarheid'

			#Bepalen voor welke shifts de leden van dit team wel en niet kunnen draaien			
			teamLijst[team]['beschikbaarheid'] = self.setShiftBeschikbaarheid(nietBeschikbaar,team)
		return teamLijst
	
	def getTeamsinHoreca(self):
		teamLijst = {}
		horecaleden = open('horecaLeden',"r")

		for lid in horecaleden.readlines():
			#returns a dict in the following form {'naam':naam,'team':team}
			lidInfo = self.persoonInfo(lid)
			if lidInfo['team'] in teamLijst:
				continue
			else:
				teamLijst[lidInfo['team']] = {}

		horecaleden.close()
		return teamLijst	

	def setShiftBeschikbaarheid(self,nietBeschikbaar,team):				
		beginShift = config.beginTijdDag
		shiftTijd = config.shiftTijd
		shifts = config.shifts

		beschikbaarheid = []

		for x in range(0,shifts):
			eindeShift = beginShift + shiftTijd
			if eindeShift < nietBeschikbaar['begin'] or nietBeschikbaar['einde'] - beginShift < 0:
				beschikbaarheid.append(True)
			else:
				beschikbaarheid.append(False)

			'''
			if self.debug:
				print "\tbeginShift: " + str(beginShift)
				print "\teindShift: " + str(eindeShift)
				print "\tbeginNietBeschikbaar: " + str(nietBeschikbaar['begin'])
				print "\teindeShift < beginNietBeschikbaar: " + str(eindeShift < nietBeschikbaar['begin'])
				print "\tbeginNietBeschikbaar - eindeShift < 0: " + str(nietBeschikbaar['einde'] - beginShift < 0)
				print "\teindeShift < nietBeschikbaar['begin'] or nietBeschikbaar['einde'] - beginShift < 0: " + str(eindeShift < nietBeschikbaar['begin'] or nietBeschikbaar['einde'] - beginShift < 0)
			'''

			beginShift += shiftTijd
		return beschikbaarheid

	def persoonInfo(self,line):
		splitNum = line.find(',')
		NewLineNum = line.find('\n')
		team = line[splitNum+1:NewLineNum]
		naam = line[:splitNum]

		if self.debug:
			print 'start persoonInfo'
			print "\tnaam: " + naam
			print "\tteam: " + team
			print 'einde persoonInfo'

		return {'naam':naam,'team':team}
	

	#transformeer tijd naar base 100
	def speelTijdTeam(self,speeltijdTeam):
		if self.debug:
			print 'begin speelTijdTeam'
			print "\tspeelTijdTeam: " + speeltijdTeam

		uur = int(speeltijdTeam[:2]) * 100 #e.g. 14 wordt 1400

		minuten = int(speeltijdTeam[3:])

		if minuten != 0:
			minuten = (minuten /60.0)*100 #door het delen wordt het een float
		
		if self.debug:
			print '\tuur: ' + str(uur)
			print '\tminuten: '+ str(minuten)
			print 'einde speelTijdTeam'

		return int(round(uur) + round(minuten)) #wel weer doorrekenen met ints


	def getReistijd(self,teamInfo):
		#wanner ga je op de fiets en wanneer met he ov of met de auto?
		tegenstanderInfo = self.getAddressTegenstander(teamInfo['tegenstander'])
		
		if self.debug:
			print "begin getReistijd"

		if tegenstanderInfo['status'] == 'error':
			pass

		if tegenstanderInfo['naam'] in self.getContentFile('reistijdClubs'):
			if self.debug:
				print 'Haal reistijd uit file'
			return self.reistijdFromFile(tegenstanderInfo['naam'])
		else:
			if self.debug:
				print 'Haal reistijd via google maps'
			return self.reistijdFromGoogle(tegenstanderInfo['naam'],tegenstanderInfo['address'])
	
	def reistijdFromFile(self,naam):
		reistijdClubs = self.getContentFile('reistijdClubs')
		reistijd = ''

		num = reistijdClubs.find(naam)
		clubLine = reistijdClubs[num:]
		clubLine = clubLine[:clubLine.find('\n')]
		for char in clubLine:
			if char.isdigit():
				if len(reistijd) == 2:
					reistijd += '.'
				reistijd += char
		return int(float(reistijd))

	def reistijdFromGoogle(self,naam,address):
		gmaps = googlemaps.Client(key)
		thuisAddress= config.thuisAddress
		directions = {}

		while address != 'Netherlands':
			try:
				directions = gmaps.directions(thuisAddress,address,mode="driving",region='nl') 
			except Exception:
				time.sleep(5)
				numNieuwWoord = address.find(' ')
				address = address[numNieuwWoord+1:]
				print address
			else:
				break

		if directions == []:
			return -1

		if self.debug:
			print address
			print '\directions[0][legs][0][duration]: ' + str(directions[0]['legs'][0]['duration'])
			print '\directions[0][legs][0][duration][text]: ' + str(directions[0]['legs'][0]['duration']['text'])

		reistijd = float(directions[0]['legs'][0]['duration']['value'])
		
		if reistijd != 0: 
			reistijd /= 60.0 #van sec naar min
			reistijd = (reistijd/60.0)*100 #naar base 100

		if self.debug:
			print "\ttegenstander: " + naam + '\n' + '\treistijd: ' + str(reistijd)
			print "einde getReistijd()"	

		self.writeLineInFile('reistijdClubs',naam + " " + str(reistijd) + "\n")

		return int(reistijd)	

	def myfilter(self,fnc,addressenList):
		pass

	def extractAddressFile(self):
		sepMarker = [',,','\n']		
		addressFile = self.getContentFile('addressLijst')
		addressenList = self.split(addressFile,sepMarker)
		if self.debug:
			for itr,item in enumerate(addressenList):
				print 'itr: {}, item: {}'.format(itr,item)

		filteredAdrs = filter( (lambda x: x % 3),range(0,len(addressenList)) )
		filteredValues = filter((lambda x: x % 2), range(0,len(filteredAdrs)))
		
		if self.debug:
			print filteredAdrs

		addressenDict = {}
		
		if self.debug:
			print '{key = value}'
		
		for idxAdress in filteredValues:
			idxClubNaam = idxAdress-1
			key = addressenList[filteredAdrs[idxClubNaam]]
			value = addressenList[filteredAdrs[idxAdress]]
			if self.debug:
				print '{} = {}'.format(key,value)
			addressenDict[key] = value
 		
 		if self.debug:
 			print addressenDict
	
	def getAddressTegenstander(self,tegenstander):
		tegenstander += ',hockey'

		if tegenstander in self.getContentFile('addressLijst'): 
			if self.debug:
				print 'Haal address tegenstander uit file'
			return self.addressFromFile(tegenstander)	
		else:
			if self.debug:
				print 'Haal address tegenstander uit de google api'
		
			return self.addressFromGoogle(tegenstander)

	def split(self,txt, seps):
		default_sep = seps[0]
		# we skip seps[0] because that's the default seperator
		for sep in seps[1:]:
			txt = txt.replace(sep, default_sep)
		return [i for i in txt.split(default_sep)]			

	def addressFromFile(self,tegenstander):
		sepMarker = ',,'
		addressLijst = self.getContentFile('addressLijst')
		tegInfo = addressLijst[addressLijst.find(tegenstander):]

		num1 = tegInfo.find(sepMarker)
		num2 = tegInfo.find(sepMarker,num1+len(sepMarker))
		newline = tegInfo.find('\n')

		naam = tegInfo[num1+len(sepMarker):num2]
		address = tegInfo[num2+len(sepMarker):newline]

		tegenstanderInfo = {'address':address,'naam':naam,'status':'ok'}
		return tegenstanderInfo

	def addressFromGoogle(self,tegenstander):
		oldtegenstander = tegenstander		
		places = googlemaps.Client(keyplaces)
		place = places.places(tegenstander)
		time.sleep(2)

		if place['status'] == 'ZERO_RESULTS':
			return {'status':'error'}	
		else:
			tegenstander = place['results'][0]['name']
			tegenstander_address = place['results'][0]['formatted_address']	
			self.writeLineInFile('addressLijst',oldtegenstander + ',,'  + tegenstander + ',,' + tegenstander_address + '\n')
			tegenstanderInfo = {'address':tegenstander_address,'naam':tegenstander,'status':'ok'}
			
			if self.debug:
				print tegenstanderInfo
			
			return tegenstanderInfo
		

	def findnth(self,haystack, needle, n):
	    parts= haystack.split(needle, n+1)
	    if len(parts) <= n+1:
	        return -1
	    return len(haystack)-len(parts[-1])-len(needle)

	def getContentFile(self,filenaam):
		f = open(filenaam,"r")
		contentFile = f.read()
		f.close()
		return contentFile

	def writeLineInFile(self,filenaam,stringToWrite):
		print stringToWrite
		f = open(filenaam, 'a')
		f.write(stringToWrite)
		f.close()

