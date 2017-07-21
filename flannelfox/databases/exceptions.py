class DatabaseException(Exception):
	# TODO: Depreciate and remove

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)