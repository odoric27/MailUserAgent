class AuthError(RuntimeError):
	def __init__(self, message=None):
		if message:
			self.message = message
		else:
			self.message = "Authentication Error: " + \
			"Please check your credentials and try again.\n"
