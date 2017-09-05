import beschikbaarheid
import output

'''
	TODO: 
		- Scoren per lid
	'''
#import validityConfig
#check validity of the config file
#validityConfig.ValidityConfig() 
#figure out how to do this

b = beschikbaarheid.Beschikbaarheid()
beschikbaarheidsLijst = b.determineBeschikbaarheid()

o = output.Output(beschikbaarheidsLijst)

rooster = o.genereerRooster()
o.writeDictToExcelFile(rooster)
ledenLijst = o.getLedenLijst()