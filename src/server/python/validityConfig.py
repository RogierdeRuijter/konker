import config
class ValidityConfig():
	def __init__(self):
		vtor = Validator()
		try:
			vtor.check('boolean', config.debug)
		except ValidateError:
			print 'Check Failed.'
		else:
			print 'Check passed.'
	def check(type,value):