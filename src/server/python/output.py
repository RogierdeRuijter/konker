import sys
import xlwt

import config


class Output:
	def __init__(self,beschikbaarheidsLijst):
		self.beschikbaarheidsLijst = beschikbaarheidsLijst
		self.beginTijdDag = config.beginTijdDag
		self.shiftTijd = config.shiftTijd
		self.shifts = config.shifts
		self.ledenLijst = self.createLedenLijst()

	def outputBeschikbaarheidInExcel(self):
		filename = 'beschikbaarheid'
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
			if self.beschikbaarheidsLijst.has_key(self.ledenLijst[lid]) and self.beschikbaarheidsLijst[self.ledenLijst[lid]] != {}:
				for c,beschikbaar in enumerate(self.beschikbaarheidsLijst[self.ledenLijst[lid]]['beschikbaarheid']):
					sh.write(r+1,c+1,beschikbaar)
		book.save(filename + '.xls')

	def writeDictToExcelFile(self,roosterDict):
		#Each row in the excel sheets starts of with the key in the first columns.
		#If the value contains a list each list entry will be placed in the next empty column
		filename = 'rooster'
		sheet = '(datum volgende zondag)'

		book = xlwt.Workbook()
		sh = book.add_sheet(sheet)

		beginTijdPrint = self.beginTijdDag
		eindTijdPrint = beginTijdPrint + self.shiftTijd
		sh.write(0,0,'shifts')

		for shift in range(0,self.shifts):
			beginTijdPrint = beginTijdPrint%2400
			eindTijdPrint = eindTijdPrint%2400
			var = ''
			
			if beginTijdPrint < 1000:
				var += '0'
			var += str(beginTijdPrint) + ":"
			
			if eindTijdPrint < 1000:
				var += '0'
			var += str(eindTijdPrint)
			
			sh.write(shift+1,0,var)

			for c,value in enumerate(roosterDict[shift]):
				sh.write(shift+1,c+1,value)

			beginTijdPrint += self.shiftTijd
			eindTijdPrint += self.shiftTijd
		book.save(filename + '.xls')
		
	def genereerRooster(self):
		aantalMensenPerShift = config.aantalMensenPerShift
		maxAantalShiftsPerDagPerPersoon = config.maxAantalShiftsPerDagPerPersoon
		
		#Komt later
		#horecaCommissarissen = config.horecaCommissarissen

		rooster = {}
		huidigeAantalShiftsPerPersoon = [0] * len(self.ledenLijst)
		for shift in range(0,self.shifts):
			rooster[shift] = []
			for itr,lid in enumerate(self.ledenLijst):
				teamVanLid = self.ledenLijst[lid]
				beschikbaarheidVanLid = self.beschikbaarheidsLijst[teamVanLid]['beschikbaarheid']

				if len(rooster[shift]) >= aantalMensenPerShift:
					break

				if beschikbaarheidVanLid[shift] == True and huidigeAantalShiftsPerPersoon[itr] < maxAantalShiftsPerDagPerPersoon:
					huidigeAantalShiftsPerPersoon[itr] += 1
					rooster[shift].append(lid)

		return rooster

	def printBeschikbaarheidsLijst(self):
		#print "Dit is de beschikbaarheids lijst van " + naam + ":" 
		for team in self.beschikbaarheidsLijst:
			beginTijdPrint = self.beginTijdDag
			eindTijdPrint = beginTijdPrint + self.shiftTijd			
			print 'Beschikbaarheid voor horecaleden uit ' + team
			for x in range(0,self.shifts):
				beginTijdPrint = beginTijdPrint%2400
				eindTijdPrint = eindTijdPrint%2400
				
				if beginTijdPrint < 1000:
					sys.stdout.write('0')
				sys.stdout.write(str(beginTijdPrint) + ":")
				if eindTijdPrint < 1000:
					sys.stdout.write('0')
				sys.stdout.write(str(eindTijdPrint) + "->" + str(self.beschikbaarheidsLijst[team]['beschikbaarheid'][x]) + '\n')
				sys.stdout.flush()

				beginTijdPrint += self.shiftTijd
				eindTijdPrint += self.shiftTijd

	def printInfoSuccesfullness(self):
		print 'voor deze leden is de beschikbaarheid bepaald: '
		for itr,lid in enumerate(self.ledenLijst):
			# Als het team in de beschikbaarheidsLijst niet gelijk is aan een lege dict dan is de beschikbaarheid succesvol bepaald
			if self.beschikbaarheidsLijst[self.ledenLijst[lid]] != {}:
				if self.ledenLijst[lid] not in self.beschikbaarheidsLijst.keys():
					print "\t" + self.ledenLijst[lid] + ' kwam helemaal niet voor in de gedownloade webpagina'
				else:
					print "\t" + lid  + ', ' + self.ledenLijst[lid] 
		if itr != len(self.ledenLijst) - 1:
			print 'voor deze leden kon geen correct beschikbaarheid bepaald worden: '
			for lid in self.ledenLijst:
				if self.beschikbaarheidsLijst[self.ledenLijst[lid]] == {}:
					if self.ledenLijst[lid] not in self.beschikbaarheidsLijst.keys():
						print "\t" + self.ledenLijst[lid] + ' kwam helemaal niet voor in de gedownloade webpagina'
					else:
						print "\t" + lid  + ', ' + self.ledenLijst[lid]

	def createLedenLijst(self):
		from beschikbaarheid import Beschikbaarheid
		ledenLijst = {}

		persoonInfo = getattr(Beschikbaarheid(), 'persoonInfo')
		horecaleden = open('horecaLeden',"r")

		for lid in horecaleden.readlines():
			#returns a dict in the following form {'naam':naam,'team':team}
			lidInfo = persoonInfo(lid)
			ledenLijst[lidInfo['naam']] = lidInfo['team'] 
		horecaleden.close()
		return ledenLijst
		
	def getLedenLijst(self):
		return self.ledenLijst