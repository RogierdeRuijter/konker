#open-webpage.py
import urllib2
import config
import re
import sys

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

class Persoon:
	def __init__(self,naam):
		self.naam = naam
		self.beschikbaarheid = []

debug = False
outputUser = True

loadWebPage = False
saveWebPage = True

horecalijst = open('horecalijst','r')
blokSize = 100
verzameltijd = 50
wedstrijdtijd = 200
shiftTijd = 200
beginTijd = 900

shifts = 10

personenLijst = []
cleantext = ""
url = 'http://gchc.nl/site/default.asp?option=100&menu=1#vTLkcFk9kmFqTzSy.97'

if loadWebPage:
	response = urllib2.urlopen(url)
	webContent = response.read()
	cleantext = cleanhtml(webContent)
	if saveWebPage:
		savedWebPage = open("savedWebPage","w")
		savedWebPage.write(cleantext)
		savedWebPage.close()
else:
	f = open("savedWebPage","r")
	cleantext = f.read()
	f.close()

iter=0
for line in horecalijst.readlines():
	splitNum = line.find(',')
	NewLineNum = line.find('\n')

	team = line[splitNum+1:NewLineNum]
	naam = line[:splitNum]

	if debug:
		print "naam: " + naam
		print "team: " + team

	teamCharNum = cleantext.find(team)

	teamInfo = cleantext[teamCharNum:teamCharNum+blokSize]

	if debug:
		print "This is the teamInfo: "
		print teamInfo

	timeCharNumTeam = teamInfo.find(':')
	speeltijdTeam = teamInfo[timeCharNumTeam-2:timeCharNumTeam+3]
	
	if debug:
		print "speelTijdTeam: " + speeltijdTeam

	uur = int(speeltijdTeam[:2]) * 100
	minuten = int(speeltijdTeam[3:])

	tijd = uur + minuten 

	reistijd = 0 #heeft een opvraag van de reistijd nodig in combinatie met de tegenstander naam, als er uit gespeeld word
	
	if not teamInfo.find("Uit") == -1:
		#reistijd = een google opvraag van de afstand of een opgeslagen reistijd?
		pass 
	beginNietBeschikbaar = tijd - verzameltijd + reistijd 
	eindNietBeschikbaar = tijd + wedstrijdtijd + reistijd
	if debug:
		print "niet beschikbaar van " + str(beginNietBeschikbaar) + " tot " + str(eindNietBeschikbaar)
	
	persoon = Persoon(naam)
	personenLijst.append(persoon)

	for x in range(0,shifts):
		eindeShift = beginTijd + shiftTijd
		if eindeShift < beginNietBeschikbaar or eindNietBeschikbaar - beginTijd < 0:
			personenLijst[iter].beschikbaarheid.append(True)
		else: 
			personenLijst[iter].beschikbaarheid.append(False)
		if debug:
			print "beginTijd: " + str(beginTijd)
			print "eindShift: " + str(eindeShift)
			print "beginNietBeschikbaar: " + str(beginNietBeschikbaar)
			print "eindeShift < beginNietBeschikbaar: " + str(eindeShift < beginNietBeschikbaar)
			print "beginNietBeschikbaar - eindeShift < 0: " + str(eindNietBeschikbaar - beginTijd < 0)
			print "eindeShift < beginNietBeschikbaar or eindNietBeschikbaar - beginTijd > 0: " + str(eindeShift < beginNietBeschikbaar or eindNietBeschikbaar - beginTijd < 0)
		beginTijd += shiftTijd

	if outputUser:
		beginTijdPrint = 900
		eindTijdPrint = beginTijdPrint + shiftTijd
		print "Dit is de beschikbaarheids lijst van " + naam + ":" 
		for x in range(0,shifts):
			beginTijdPrint = beginTijdPrint%2400
			eindTijdPrint = eindTijdPrint%2400
			if beginTijdPrint < 1000:
				beginTijdPrint
			print beginTijdPrint + ":" + eindTijdPrint + "->" + str(personenLijst[iter].beschikbaarheid[x])
			beginTijdPrint += shiftTijd
			eindTijdPrint += shiftTijd

	streepNum = teamInfo.find('-')
	tegenstander = teamInfo[streepNum+2:streepNum+19]

	if debug: 
		if not teamInfo.find("Thuis") == -1:
			print naam + " speelt thuis tegen " + tegenstander + ", om " + speeltijdTeam
		else:
			print naam + " speelt uit tegen " + tegenstander + ", om " + speeltijdTeam
	iter+=1
	beginTijd = 900