class dfa(Object):
	# todo funciona con cadenas
	__init__(self):
		self.estados = []
		self.sigma = []
		self.estado_inicial = ''
		self.estados_finales = []

	def cargar_desde_archivo(nombre_archivo):
		archivo = open(nombre_archivo)


if __name__ == '__main__':
	dfa =  dfa()
	dfa.cargar_desde_archivo("automatas.txt")