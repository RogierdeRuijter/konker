#import json 

class BerekenScore():
	def __init__(self,rooster,ledenLijst):
		self.checkValidityScoreFile(ledenLijst)

	def loadScoreFile(self):
		import ast
		f = open("scoreHorecaLeden","r")
		content = f.read()
		f.close()
		return content

	def checkValidityScoreFile(self,ledenLijst):
		scoreFile = self.loadScoreFile()
		for lid in ledenLijst:
			if lid not in scoreFile:
				self.fixValidityScoreFile(lid)

	def fixValidityScoreFile(self,lid):
		with open('scoreHorecaLeden','w') as f:
			data = json.load(f)
			f.close()
			return data

	def updateScoreFile(self,rooster):
		scoreFile = self.loadScoreFile()

		valueVoorKutShift = 2
		valueVoorNormaleShift = 1

		for shift,ledenInDezeShift in rooster.items():
			if shift == 0 or shift == len(rooster) - 1:
				toegevoegdeScore = valueVoorKutShift
			else:
				toegevoegdeScore = valueVoorNormaleShift

			for lid in ledenInDezeShift:
				pass
				#haal score van lid uit scoreFile
				#voeg "toegevoegdeScore" toe
				#schrijf score terug

