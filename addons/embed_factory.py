from discord import Embed

class EmbedFactory:
	# TODO: move default color to config yaml
	DEFAULT_COLOR = 0xA36CFD
	ERROR_COLOR = 0xFF0000

	@staticmethod
	def info(title, message="", color=DEFAULT_COLOR):
		return Embed(title=title, description=message, color=color)

	@staticmethod
	def error(title="An error has occurred", message="Please contact a server Administrator.", color=ERROR_COLOR):
		return Embed(title=title, description=message, color=color)
