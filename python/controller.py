#open-webpage.py
import config
import xlwt
import sys
import time
from key import key,keyplaces
import handelinputdata
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
		
		self.thuisAdress = config.thuisAdress

		self.blokSize = config.blokSize
		#self.gevondenInfo = config.gevondenInfo

		self.verzameltijd = config.verzameltijd
		self.wedstrijdtijd = config.wedstrijdtijd
		self.shiftTijd = config.shiftTijd
		self.beginTijdDag = config.beginTijdDag
		self.shifts = config.shifts
		self.horecaLeden = config.horecaLeden

		#empty global variables for later assignment
		self.teamLijst = {}
		self.ledenLijst = {}

	
	def getPersonenLijst(self):
		return self.teamLijst

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


	def getInfoTeamHorecaLid(self,infoHorecaLid):
		h = handelinputdata.Handelinputdata(infoHorecaLid)
		return h.handel()

	def findnth(self,haystack, needle, n):
	    parts= haystack.split(needle, n+1)
	    if len(parts)<=n+1:
	        return -1
	    return len(haystack)-len(parts[-1])-len(needle)

	def getContentFile(self,filenaam):
		f = open(filenaam,"r")
		contentFile = f.read()
		f.close()
		return contentFile

	def writeLineInFile(self,filenaam,stringToWrite):
		f = open(filenaam, 'r+')
		f.write(stringToWrite)
		f.close()

	def adressFromFile(self,tegenstander):
		addressLijst = self.getContentFile('addressLijst')
		num = addressLijst.find(tegenstander)
		addressLine = addressLijst[num:num+addressLijst.find('\n')]
		tegenstander = addressLine[self.findnth(addressLine,',,',0)+2:self.findnth(addressLine,',,',1)]
		tegenstander_adress = addressLine[self.findnth(addressLine,',,',1)+2:addressLine.find('\n')]
		
		return {'adress':tegenstander_adress,'naam':tegenstander,'status':'ok'}

	def adressFromGoogle(self,tegenstander):
		oldtegenstander = tegenstander		
		places = googlemaps.Client(keyplaces)
		place = places.places(tegenstander)
		time.sleep(5)

		if place['status'] == 'ZERO_RESULTS':
			return {'status':'error'}	
		else:
			tegenstander = place['results'][0]['name']
			tegenstander_adress = place['results'][0]['formatted_address']	
			self.writeLineInFile('addressLijst',oldtegenstander + ',,'  + tegenstander + ',,' + tegenstander_adress + '\n')
			return {'adress':tegenstander_adress,'naam':tegenstander,'status':'ok'}



	def getAdressTegenstander(self,teamInfo):
		tegenstander = teamInfo['tegenstander'] + ',hockey'

		if tegenstander in self.getContentFile('addressLijst'): #Oppassen
			return self.adressFromFile(tegenstander)	
		else:
			return self.adressFromGoogle(tegenstander)
	
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

	def reistijdFromGoogle(self,naam,adress):
		gmaps = googlemaps.Client(key)
		directions = {}

		while adress != 'Netherlands':
			try:
				directions = gmaps.directions(self.thuisAdress,adress,mode="driving",region='nl') 
			except Exception:
				time.sleep(5)
				numNieuwWoord = adress.find(' ')
				adress = adress[numNieuwWoord+1:]
				print adress
			else:
				break

		if directions != []:
			return -1

		if self.debug:
			print '\directions[0][legs][0][duration]: ' + str(directions[0]['legs'][0]['duration'])
			print '\directions[0][legs][0][duration][text]: ' + str(directions[0]['legs'][0]['duration']['text'])

		reistijd = float(directions[0]['legs'][0]['duration']['value'])
		
		if reistijd != 0: 
			reistijd /= 60.0 #van sec naar min
			reistijd = (reistijd/60.0)*100 #naar base 100

		if self.debug:
			print "\ttegenstander: " + tegenstanderInfo['naam'] + '\n' + '\treistijd: ' + str(reistijd)
			print "einde getReistijd()"	

		self.writeLineInFile('reistijdClubs',tegenstanderInfo['naam'] + " " + str(reistijd) + "\n")

		return int(reistijd)
	

	def getReistijd(self,teamInfo):
		#wanner ga je op de fiets en wanneer met he ov of met de auto
		tegenstanderInfo = self.getAdressTegenstander(teamInfo)
		
		if self.debug:
			print "begin getReistijd"

		if tegenstanderInfo['status'] == 'error':
			#errormessage
			pass

		if tegenstanderInfo['naam'] in self.getContentFile('reistijdClubs'):
			return self.reistijdFromFile(tegenstanderInfo['naam'])
		else:
			return self.reistijdFromGoogle(tegenstanderInfo['naam'],tegenstanderInfo['adress'])

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

	def printInfoSuccesfullness(self):
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
		
	def determineBeschikbaarheid(self):
		for lid in self.horecaLeden.readlines():
			teamInfo = self.getInfoTeamHorecaLid(self.persoonInfo(lid))
			if teamInfo['status'] == 'OK' and 'beschikbaarheid' not in self.teamLijst[teamInfo['team']]:
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

			self.printInfoSuccesfullness()
		

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