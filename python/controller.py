#open-webpage.py
import urllib2
import config
import xlwt
import re
import sys
import time
from key import key,keyplaces

import googlemaps
from datetime import datetime

'''
Er wordt met tijd gerekend op een schaal van 100

Er zijn twee globale dics, teamLijst en ledenLijst
teamLijst heeft heeft de volgende structuur:
	
	teamLijst{team:'teamnaam',compleet:False}
	of
	teamLijst{team:'teamnaam',compleet:True,beschikbaarheid:[x1,..,x(9 of 10)}
	
	Als compleet de waarde False heeft dat is er iets fout gegaan in het vergaren van de informatie
	over dat team. Door de Controller class heen zijn er meerdere momenten waarop de waarde naar False kan gaan.

LedenLijst heeft deze structuur,
	
	ledenLijst[lid:'lidNaam':team: 'teamnaam']

	De ledenLijst dic wordt gevult met de informatie uit de file 'HorecaLeden'


TODO: 
	- Scoren per lid
	- Een rooster maken
	- Rekening houden dat er info over op welk veld er wordt gespeeld bij kan zitten 
	- Verifiy in en parse
	- Informatie opslaan waar compleet naar False wordt gezet. Kan via een lijst, dat elke False assignment plek een nummer heeft, 
		zodat je precies kan printen aan het einde van de code kan printen waar het in de code is mis gegaan. 
		zo kan de code ook cleaner worden omdat alle error print statements naar 1 functie verdwijnen 
'''
class Controller:
	def __init__(self):
		#global variables read from config file
		#can this go into a struct?
		self.debug = config.debug
		self.outputUser = config.outputUser
		self.downloadWebPage = config.downloadWebPage
		self.saveWebPage = config.saveWebPage
		
		self.thuisAdress = config.thuisAdress

		self.blokSize = config.blokSize
		#self.gevondenInfo = config.gevondenInfo

		self.verzameltijd = config.verzameltijd
		self.wedstrijdtijd = config.wedstrijdtijd
		self.shiftTijd = config.shiftTijd
		self.beginTijdDag = config.beginTijdDag
		self.shifts = config.shifts
		self.url = config.url
		self.horecaLeden = config.horecaLeden

		#empty global variables for later assignment
		self.teamLijst = {}
		self.ledenLijst = {}
		self.cleantext = ""

	
	def getPersonenLijst(self):
		return self.teamLijst

	def cleanhtml(self,raw_html):
  		cleanr = re.compile('<.*?>')
  		cleantext = re.sub(cleanr, '', raw_html)
  		return cleantext

  	def getWebPage(self):
		if self.downloadWebPage:
			response = urllib2.urlopen(self.url)
			webContent = response.read()
			self.cleantext = self.cleanhtml(webContent)
			if self.saveWebPage:
				savedWebPage = open("savedWebPage","w")
				savedWebPage.write(self.cleantext)
				savedWebPage.close()
		else:
			f = open("savedWebPage","r")
			self.cleantext = self.cleanhtml(f.read())
			f.close()


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
		#init teamLijst voor team(x)
		if team not in self.teamLijst:
			self.teamLijst[team] = {}
			self.teamLijst[team]['compleet'] = True
		#save lid globaal
		self.ledenLijst[naam] = team
		return {'naam':naam,'team':team}
	
	def preProcessInputData(self,blok):
		inputList = []
		if(blok == ''):
			return []

		blok = blok.replace(' ',',')
		new = ''
		#dit wordt raar gedaan omdat de data die in 'blok' zit kanker vaag is
		
		for char in blok:
			if char.isdigit() or char.isalpha() or char == ',' or char == ':':
				new += char
			if char == '\n': 
				new += ','
		#to remove double qoutes if there are mutliple newlines next to eachother
			if new[-2:] == ',,':
				new = new[:-1]
		
		inputString = new + ','
		entry = ''
		
		if self.debug:
			print inputString

		for x in inputString:
			if x != ',':
				entry += x
			else:
				inputList.append(entry)
				entry = ''
		
		if self.debug:
			print str(inputList)
		
		return inputList
		#TODO
	def parseInputData(self,verifiedData):
		teamInfo = {}

		tegenstander = ""
		tempTeamInfo = verifiedData[:]

		for entry in parsedData: #team nummer van tegenstander wordt weggegooid
			if entry.isalpha():
				tegenstander += entry + ' '
				tempTeamInfo.remove(entry)
			else:
				tempTeamInfo.remove(entry)
				break
		verifiedData = tempTeamInfo
		teamInfo['tegenstander'] = tegenstander[:-1]

		teamInfo['speeltijd'] = parsedData[0]
		parsedData.remove(parsedData[0]) 

	def verifyInputData(self,parsedData,infoHorecaLid):
		if parsedData == []:
			print "De team informatie voor " + infoHorecaLid['team'] + " is niet gevonden"
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False

		if not parsedData[0] == infoHorecaLid['team'][:-3]:
			print 'parsedData and horecaLid komen niet overeen'
			print parsedData[0] + infoHorecaLid['team'][:-3]
			#self.teamLijst[infoHorecaLid[infoHorecaLid['team']]['compleet']] = False
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False

		if not parsedData[1] == infoHorecaLid['team'][-2:]:
			print 'parsedData and horecaLid komen niet overeen'
			print parsedData[1] + infoHorecaLid['team'][-2:]
			#self.teamLijst[infoHorecaLid[infoHorecaLid['team']]['compleet']] = False
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			return infoHorecaLid

		#teamInfo['team'] = infoHorecaLid['team']

		parsedData.remove(infoHorecaLid['team'][:-3])
		parsedData.remove(infoHorecaLid['team'][-2:])

		tegenstander = ""
		tempTeamInfo = parsedData[:]
		for entry in parsedData: #team nummer van tegenstander wordt weggegooid
			if entry.isalpha():
				tegenstander += entry + ' '
				tempTeamInfo.remove(entry)
			else:
				tempTeamInfo.remove(entry)
				break
		parsedData = tempTeamInfo
		teamInfo['tegenstander'] = tegenstander[:-1]

		if not parsedData[0].find(':') == 2 or not parsedData[0][:2].isdigit() or not parsedData[0][-2:].isdigit():
			print "er is iets mis met de ingelezen tijd"
			if parsedData[0] == 'nnb':
				print 'de tijd voor ' + infoHorecaLid['team'] + ' staat nog niet op de gchc site. Probeer het later nog eens of vul het zelf in.'
			else:
				print parsedData[0] + infoHorecaLid['team']
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			parsedData.remove(parsedData[0]) 
		else:
			teamInfo['speeltijd'] = parsedData[0]
			parsedData.remove(parsedData[0]) 

		if parsedData[0][:1].isalpha() and parsedData[0][1:].isdigit():
			parsedData.remove(parsedData[0])

		if parsedData[0].lower() != 'thuis' and parsedData[0].lower() != 'uit':
			print "Er klopt iets niet met de plek waar er gespeeld wordt"
			print parsedData[0]
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			parsedData.remove(parsedData[0])
		else:
			teamInfo['speelplek'] = parsedData[0].lower()
			parsedData.remove(parsedData[0])

		if not parsedData == []:
			print 'de parsedData lijst is niet leeg'
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			print parsedData
			print teamInfo

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

	def findBlokSize(self,teamCharNum):
		laatsteWoorden = ['Thuis','Uit']
		blok = ''
		for i,char in enumerate(self.cleantext[teamCharNum:]):
			if laatsteWoorden[0] in blok or laatsteWoorden[1] in blok:
				break
			blok += char
		return len(blok)

	def getInputData(self,teamCharNum):
		bloksize = self.findBlokSize(teamCharNum)
		blok = self.cleantext[teamCharNum:teamCharNum+bloksize]
		
		if self.debug:
			print blok
		
		return blok

	def getInfoTeamHorecaLid(self,infoHorecaLid):
		teamCharNum = self.cleantext.find(infoHorecaLid['team'])
		
		dataInBlok = self.getInputData(teamCharNum)

		preProcessInputData = self.preProcessInputData(dataInBlok)
		
		verifiedData = self.verifyInputData(preProcessInputData,infoHorecaLid)
		exit()

		parsedData = self.parseInputData()


		if self.teamLijst[infoHorecaLid['team']]['compleet'] == False:
			return infoHorecaLid

		return verifiedData

	def findnth(self,haystack, needle, n):
	    parts= haystack.split(needle, n+1)
	    if len(parts)<=n+1:
	        return -1
	    return len(haystack)-len(parts[-1])-len(needle)

	def getReistijd(self,teamInfo):
		#wanner ga je op de fiets en wanneer met he ov of met de auto
		reistijd = ''
		tegenstander = teamInfo['tegenstander']+',hockey'
		f = open('addressLijst', 'r+')
		addressLijst = f.read()
		place = {}
		tegenstander_adress = {}

		if self.debug:
			print "begin getReistijd"
		if tegenstander in addressLijst:
			num = addressLijst.find(tegenstander)
			addressLine = addressLijst[num:num+addressLijst.find('\n')]
			tegenstander = addressLine[self.findnth(addressLine,',,',0)+2:self.findnth(addressLine,',,',1)]
			tegenstander_adress = addressLine[self.findnth(addressLine,',,',1)+2:addressLine.find('\n')]
			place['status'] = 'INLIJST'
		else:
			oldtegenstander = tegenstander
			time.sleep(5)
			places = googlemaps.Client(keyplaces)
			place = places.places(tegenstander)
			if place['status'] == 'ZERO_RESULTS':
				print 'kan tegenstander niet vinden ' + tegenstander
				reistijd = '0'	
			else:
				tegenstander = place['results'][0]['name']
				tegenstander_adress = place['results'][0]['formatted_address']
				f.write(oldtegenstander + ',,'  + tegenstander + ',,' + tegenstander_adress + '\n')
		f.close()	
		f = open("reistijdClubs","r+")
		reistijdClubs = f.read()
		if tegenstander in reistijdClubs:
			num = reistijdClubs.find(tegenstander)
			clubLine = reistijdClubs[num:]
			clubLine = clubLine[:clubLine.find('\n')]
			for char in clubLine:
				if char.isdigit():
					if len(reistijd) == 2:
						reistijd += '.'
					reistijd += char
		else:
			gmaps = googlemaps.Client(key)
			directions_result = {}
			if place['status'] == 'OK' or place['status'] == 'INLIJST':
				while tegenstander_adress != '':
					try:
						directions_result = gmaps.directions(self.thuisAdress,tegenstander_adress,mode="driving",region='nl') 
					except Exception:
						time.sleep(2)
						numNieuwWoord = tegenstander_adress.find(' ')
						tegenstander_adress = tegenstander_adress[numNieuwWoord+1:]
						print tegenstander_adress
					else:
						break
			if self.debug and directions_result != []:
				print '\tdirections_result[0][legs][0][duration]: ' + str(directions_result[0]['legs'][0]['duration'])
				print '\tdirections_result[0][legs][0][duration][text]: ' + str(directions_result[0]['legs'][0]['duration']['text'])

			reistijd = directions_result[0]['legs'][0]['duration']['value'] if directions_result != [] else 0 
			if reistijd != 0: 
				reistijd /= 60.0 #van sec naar min
				reistijd = (reistijd/60.0)*100 #naar base 100


			f.write(tegenstander + " " + str(reistijd) + "\n")
		f.close()
		if self.debug:
			print "\ttegenstander: " + tegenstander + '\n' + '\treistijd: ' + str(reistijd)
			print "einde getReistijd()"
		return int(float(reistijd)) if reistijd != '' else 0

	def printBeschikbaarheidsLijst(self):
		beginTijdPrint = self.beginTijdDag
		eindTijdPrint = beginTijdPrint + self.shiftTijd
		#print "Dit is de beschikbaarheids lijst van " + naam + ":" 
		for team in self.teamLijst:
			print 'Beschikbaarheid voor horecaleden uit ' + team
			for x in range(0,self.shifts):
				beginTijdPrint = beginTijdPrint%2400
				eindTijdPrint = eindTijdPrint%2400
				
				if beginTijdPrint < 1000:
					sys.stdout.write('0')
				sys.stdout.write(str(beginTijdPrint) + ":")
				if eindTijdPrint < 1000:
					sys.stdout.write('0')
				sys.stdout.write(str(eindTijdPrint) + "->" + str(self.teamLijst[team][x]) + '\n')
				sys.stdout.flush()

				beginTijdPrint += self.shiftTijd
				eindTijdPrint += self.shiftTijd

	def determineBeschikbaarheid(self):
		self.getWebPage()
		for lid in self.horecaLeden.readlines():
			teamInfo = self.getInfoTeamHorecaLid(self.persoonInfo(lid))
			if self.teamLijst[teamInfo['team']]['compleet'] and 'beschikbaarheid' not in self.teamLijst[teamInfo['team']]:
				reistijd = self.getReistijd(teamInfo)
				speelTijd = self.speelTijdTeam(teamInfo['speeltijd'])

				nietBeschikbaar = {'begin':speelTijd - self.verzameltijd + reistijd,'einde':speelTijd + self.wedstrijdtijd + reistijd}

				if self.debug:
					print 'begin determineBeschikbaarheid '
					print "\tniet beschikbaar van " + str(nietBeschikbaar['begin']) + " tot " + str(nietBeschikbaar['einde'])
							
				beginShift = self.beginTijdDag
				beschikbaarheid = []

				for x in range(0,self.shifts):
					eindeShift = beginShift + self.shiftTijd
					if eindeShift < nietBeschikbaar['begin'] or nietBeschikbaar['einde'] - beginShift < 0:
						beschikbaarheid.append(True)
					else:
						beschikbaarheid.append(False)
					'''if self.debug:
						print "\tbeginShift: " + str(beginShift)
						print "\teindShift: " + str(eindeShift)
						print "\tbeginNietBeschikbaar: " + str(nietBeschikbaar['begin'])
						print "\teindeShift < beginNietBeschikbaar: " + str(eindeShift < nietBeschikbaar['begin'])
						print "\tbeginNietBeschikbaar - eindeShift < 0: " + str(nietBeschikbaar['einde'] - beginShift < 0)
						print "\teindeShift < beginNietBeschikbaar or eindNietBeschikbaar - beginShift > 0: " + str(eindeShift < nietBeschikbaar['begin'] or nietBeschikbaar['einde'] - beginShift < 0)
					'''
					beginShift += self.shiftTijd
				self.teamLijst[teamInfo['team']]['beschikbaarheid'] = beschikbaarheid
				beginShift = self.beginTijdDag

				if self.debug:
					print 'einde determineBeschikbaarheid'
		
		print 'voor deze leden is de beschikbaarheid bepaald: '
		for lid in self.ledenLijst:
			if self.teamLijst[self.ledenLijst[lid]]['compleet'] == True:
				if self.ledenLijst[lid] not in self.teamLijst.keys():
					print "\t" + self.ledenLijst[lid] + ' kwam helemaal niet voor in de gedownloade webpagina'
				else:
					print "\t" + lid  + ', ' + self.ledenLijst[lid] 

		print 'voor deze leden kon geen correct beschikbaarheid bepaald worden: '
		for lid in self.ledenLijst:
			if self.teamLijst[self.ledenLijst[lid]]['compleet'] == False:
				if self.ledenLijst[lid] not in self.teamLijst.keys():
					print "\t" + self.ledenLijst[lid] + ' kwam helemaal niet voor in de gedownloade webpagina'
				else:
					print "\t" + lid  + ', ' + self.ledenLijst[lid] 
		

	def outputRooster(self):
		filename = 'rooster'
		sheet = '(datum volgende zondag)'

		book = xlwt.Workbook()
		sh = book.add_sheet(sheet)

		beginTijdPrint = self.beginTijdDag
		eindTijdPrint = beginTijdPrint + self.shiftTijd
		sh.write(0,0,'shifts')
		
		for x in range(0,self.shifts):
			beginTijdPrint = beginTijdPrint%2400
			eindTijdPrint = eindTijdPrint%2400
			var = ''
			
			if beginTijdPrint < 1000:
				var += '0'
			var += str(beginTijdPrint) + ":"
			
			if eindTijdPrint < 1000:
				var += '0'
			var += str(eindTijdPrint)
			
			sh.write(0,x+1,var)

			beginTijdPrint += self.shiftTijd
			eindTijdPrint += self.shiftTijd
		for r,lid in enumerate(self.ledenLijst):
			sh.write(r+1,0,lid)
			if self.teamLijst.has_key(self.ledenLijst[lid]) and self.teamLijst[self.ledenLijst[lid]]['compleet']:
				for c,beschikbaar in enumerate(self.teamLijst[self.ledenLijst[lid]]['beschikbaarheid']):
					sh.write(r+1,c+1,beschikbaar)

		book.save(filename+'.xls')