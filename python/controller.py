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
	teamLijst{team:'teamnaam',compleet:True,beschikbaarheid:[x1,..,x10]}
	
	Als compleet de waarde False heeft dat is er iets fout gegaan in het vergaren van de informatie
	over dat team. Door de Controller class heen zijn er meerdere momenten waarop de waarde naar False kan gaan.

LedenLijst heeft deze structuur,
	
	ledenLijst[lid:'lidNaam':team: 'teamnaam']

	De ledenLijst dic wordt gevult met de informatie uit de file 'HorecaLeden'
'''

#TODO: 
#	- Scoren per lid
#	- Een rooster maken
#	- Rekening houden dat er info over op welk veld er wordt gespeeld bij kan zitten 
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
	
	def listMetTeamInfo(self,team):
		teamCharNum = self.cleantext.find(team)
		
		blok = self.cleantext[teamCharNum:teamCharNum+(self.blokSize)]

		if(blok == ''):
			print "De team informatie voor " + team + " is niet gevonden"
			self.teamLijst[team]['compleet'] = False
			return
		else:
			if self.debug:
				print 'begin listMetTeamInfo'
				print blok
			#opdelen in inspectBlok() en parseBlok()

			blok = blok.replace('\t','')
			blok = blok.replace('-', '')
			blok = blok.replace(' ',',')
			
			new = ''
			#dit wordt raar gedaan omdat de data die in 'blok' zit kanker vaag is
			for char in blok:
				if char.isdigit() or char.isalpha() or char == ',' or char == ':':
					new += char
				#to remove double qoutes if there are mutliple newlines next to eachother
				if char == '\n' and new[len(new)-1:len(new)] != ',': 
					new += ','
			
			tempList = []
			entry = ''
			#zet alle info in een lijst
			for x in new:
				if x != ',':
					entry += x
				else:
					tempList.append(entry)
					entry = ''
			
			if '' in tempList:
				tempList.remove('')
			if self.debug:
				print '\t' + str(tempList)
				print 'einde listMetTeamInfo'
			return tempList

	#transformeer tijd naar base 100
	def speelTijdTeam(self,speeltijdTeam):
		if self.debug:
			print 'begin speelTijdTeam'
			print "\tspeelTijdTeam: " + speeltijdTeam

		uur = int(speeltijdTeam[:2]) * 100

		minuten = int(speeltijdTeam[3:])

		if minuten != 0:
			minuten = (minuten /60.0)*100
		
		if self.debug:
			print '\tuur: ' + str(uur)
			print '\tminuten: '+ str(minuten)
			print 'einde speelTijdTeam'

		return int(round(uur) + round(minuten))

	def getInfoTeamHorecaLid(self,infoHorecaLid):
		listInfoTeam = self.listMetTeamInfo(infoHorecaLid['team'])
		teamInfo = {}
		if self.teamLijst[infoHorecaLid['team']]['compleet'] == False:
			return infoHorecaLid
		if not listInfoTeam[0] == infoHorecaLid['team'][:-3]:
			print 'listInfoTeam and horecaLid komen niet overeen'
			print listInfoTeam[0] + infoHorecaLid['team'][:-3]
			exit()
		if not listInfoTeam[1] == infoHorecaLid['team'][-2:]:
			print 'listInfoTeam and horecaLid komen niet overeen'
			print listInfoTeam[1] + infoHorecaLid['team'][-2:]
			exit()

		teamInfo['team'] = infoHorecaLid['team']

		listInfoTeam.remove(infoHorecaLid['team'][:-3])
		listInfoTeam.remove(infoHorecaLid['team'][-2:])

		tegenstander = ""
		tempTeamInfo = listInfoTeam[:]
		for entry in listInfoTeam: #team nummer van tegenstander wordt weggegooid
			if entry.isalpha():
				tegenstander += entry + ' '
				tempTeamInfo.remove(entry)
			else:
				tempTeamInfo.remove(entry)
				break
		listInfoTeam = tempTeamInfo
		teamInfo['tegenstander'] = tegenstander[:-1]
		
		if not listInfoTeam[0].find(':') == 2 or not listInfoTeam[0][:2].isdigit() or not listInfoTeam[0][-2:].isdigit():
			print "er is iets mis met de ingelezen tijd"
			if listInfoTeam[0] == 'nnb':
				print 'de tijd voor ' + teamInfo['team'] + ' staat nog niet op de gchc site. Probeer het later nog eens of vul het zelf in.'
			else:
				print listInfoTeam[0] + teamInfo['team']
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			listInfoTeam.remove(listInfoTeam[0]) 
		else:
			teamInfo['speeltijd'] = listInfoTeam[0]
			listInfoTeam.remove(listInfoTeam[0]) 
		
		if listInfoTeam[0].lower() != 'thuis' and listInfoTeam[0].lower() != 'uit':
			print "Er klopt iets niet met de plek waar er gespeeld wordt"
			print listInfoTeam[0]
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			listInfoTeam.remove(listInfoTeam[0])
		else:
			teamInfo['speelplek'] = listInfoTeam[0].lower()
			listInfoTeam.remove(listInfoTeam[0])

		if not listInfoTeam == []:
			print 'de listInfoTeam lijst is niet leeg'
			self.teamLijst[infoHorecaLid['team']]['compleet'] = False
			print listInfoTeam
			print teamInfo

		return teamInfo

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
			time.sleep(10)
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

		print tegenstander
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
				directions_result = gmaps.directions(self.thuisAdress,tegenstander_adress,mode="driving",region='nl') 

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