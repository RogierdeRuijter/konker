import config
import urllib2
import re

class Handelinputdata():
	def __init__(self,infoHorecaLid):
		self.downloadWebPage = config.downloadWebPage
		self.saveWebPage = config.saveWebPage
		self.infoHorecaLid = infoHorecaLid
		self.url = config.url
		self.debug = config.debug

	def handel(self):
		data = self.getInputData()
		preProcessedInputData = self.preProcessInputData(data)
		v = VerifyData(preProcessedInputData,self.infoHorecaLid)
		if v.verify():
			teamInfo = self.parse(preProcessedInputData)
			teamInfo.update({'status':'OK'})
			return teamInfo
		else:
			return {'status':'error'}

 	def getWebPage(self):
 		cleantext = ''
		if self.downloadWebPage:
			response = urllib2.urlopen(self.url)
			webContent = response.read()
			cleantext = self.cleanhtml(webContent)
			if self.saveWebPage:
				savedWebPage = open("savedWebPage","w")
				savedWebPage.write(cleantext)
				savedWebPage.close()
		else:
			f = open("savedWebPage","r")
			cleantext = self.cleanhtml(f.read())
			f.close()
		return cleantext

	def cleanhtml(self,raw_html):
  		cleanr = re.compile('<.*?>')
  		cleantext = re.sub(cleanr, '', raw_html)
  		return cleantext


	def preProcessInputData(self,blok):
		inputList = []
		if(blok == ''):
			print 'Er is geen data gevonden voor dit team'
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
	def parse(self,verifiedData):
		teamInfo = {}
		if self.debug:
			print verifiedData
		teamInfo['team'] = str(verifiedData[0] + ' ' +  verifiedData[1])

		verifiedData.remove(verifiedData[0])
		verifiedData.remove(verifiedData[0])

		tegenstander = ""
		tempTeamInfo = verifiedData[:]
		for entry in verifiedData:
			if entry.isalpha():
				tegenstander += entry + ' '
				tempTeamInfo.remove(entry)
			else:
				tempTeamInfo.remove(entry) #team nummer van tegenstander wordt weggegooid
				break

		verifiedData = tempTeamInfo

		teamInfo['tegenstander'] = tegenstander[:-1]

		teamInfo['speeltijd'] = verifiedData[0]
		verifiedData.remove(verifiedData[0]) 

		teamInfo['speelplek'] = verifiedData[0].lower()
		verifiedData.remove(verifiedData[0])
		print teamInfo
		return teamInfo
	

	def findBlokSize(self,teamCharNum,cleanhtml):
		laatsteWoordenInBlok = ['Thuis','Uit']
		blok = ''
		for i,char in enumerate(cleanhtml[teamCharNum:]):
			if laatsteWoordenInBlok[0] in blok or laatsteWoordenInBlok[1] in blok:
				break
			blok += char
		return len(blok)

	def getInputData(self):
		cleanhtml = self.getWebPage()
		teamCharNum = cleanhtml.find(self.infoHorecaLid['team'])
		bloksize = self.findBlokSize(teamCharNum,cleanhtml)
		blok = cleanhtml[teamCharNum:teamCharNum+bloksize]
		
		if self.debug:
			print blok
		return blok 

class VerifyData():
	def __init__(self,preProcessedInputData,infoHorecaLid):
		self.preProcessedInputData = preProcessedInputData
		self.verifyList = preProcessedInputData[:]	
		self.compleet = True
		self.team = infoHorecaLid['team']
		self.errorLijst = []

	def verifyTeamNaamEnNummer(self):
		if not self.verifyList[0] == self.team[:-3]:
			self.errorLijst.append(2)

		if not self.verifyList[1] == self.team[-2:]:
			self.errorLijst.append(3)

		self.verifyList.remove(self.team[:-3])
		self.verifyList.remove(self.team[-2:])

	def verifyTegenstander(self):
		#Er is geen check voor de tegestander
		tegenstander = ""
		tempTeamInfo = self.verifyList[:]
		for entry in self.verifyList: #team nummer van tegenstander wordt weggegooid
			if entry.isalpha():
				tegenstander += entry + ' '
				tempTeamInfo.remove(entry)
			else:
				tempTeamInfo.remove(entry)
				break
		self.verifyList = tempTeamInfo

	def verifySpeeltijd(self):
		if not self.verifyList[0].find(':') == 2 or not self.verifyList[0][:2].isdigit() or not self.verifyList[0][-2:].isdigit():
			self.errorLijst.append(4)
			if self.verifyList[0] == 'nnb':
				self.errorLijst.append(5)
		self.verifyList.remove(self.verifyList[0]) 

	def checkveld(self):
		if self.verifyList[0][:1].isalpha() and self.verifyList[0][1:].isdigit():
			self.preProcessedInputData.remove(self.verifyList[0])			
			self.verifyList.remove(self.verifyList[0])

	def verifySpeelplek(self):
		if self.verifyList[0].lower() != 'thuis' and self.verifyList[0].lower() != 'uit':
			self.errorLijst.append(6)
		self.verifyList.remove(self.verifyList[0])


	def ispreproccesdInputLeeg(self):
		if self.verifyList == []:
			return True
		return False

	
	def errormessages(self,error):
		if error == 1:
			print "De team informatie voor " + self.team + " is niet gevonden"
		if error == 2:
			print 'Het team in preProcessedInputData and horecaLid komen niet overeen'
			#print self.preProcessedInputData[0] + self.team[:-3]
		if error == 3:
			print 'het teamnummer in preProcessedInputData and horecaLid komen niet overeen'
			#print self.preProcessedInputData[1] + self.team[-2:]
		if error == 4:
			print "de ingelezen tijd is niet in het 'xx:xx' format"
			#print self.preProcessedInputData[0] + self.team
		if error == 5:
			print 'de tijd voor ' + self.team + ' staat nog niet op de gchc site. Probeer het later nog eens of vul het zelf in.'
		if error == 6:
			print "De speel locatie is niet 'thuis' of 'uit'"
			#print self.preProcessedInputData[0]
		if error == 7:
			print 'de preProcessedInputData lijst is niet leeg'
			print self.verifyList


	def displayerror(self):
		#error 1 er zit aan het begin van het verifvyen niks in de pre-processed lijst
		#error 2 de team naar in infoHorecaLid en de pre-processed lijst komen niet overeen
		#error 3 het team nummer in infoHorecaLid komt niet overeen met het nummer in de pre-processed lijst
		#error 4 de ingelezen tijd uit pre-processed data is niet in het xx:xx format
		#error 5 de ingelezen tijd is 'nnb', dit betekent dat hij nog niet bekend is op de gchc site
		#error 6 de ingelezen speelplek is niet 'Thuis' of 'Uit'
		#error 7 er is informatie in de preprocessed lijst die niet geverified kan worden

		if self.errorLijst == []:
			return
		else:
			for error in self.errorLijst:
				self.errormessages(error)

		self.compleet = False

	def verifyInputPropertiesList(self):
		if self.ispreproccesdInputLeeg():
			self.errorLijst.append(1)

	def verifyOutputPropertiesList(self):
		if not self.ispreproccesdInputLeeg():
			self.errorLijst.append(7)

	def verify(self):
		self.verifyInputPropertiesList()
		
		self.verifyTeamNaamEnNummer()
		self.verifyTegenstander()
		self.verifySpeeltijd()
		self.checkveld()
		self.verifySpeelplek()

		self.verifyOutputPropertiesList()

		self.displayerror()

		return self.compleet