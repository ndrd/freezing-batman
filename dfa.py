#!/usr/bin/env python
# -*- coding: utf8 -*-

class Dfa (object):
	# todo funciona con cadenas
	def __init__(self):
		self.estados = []
		self.estados_finales = []
		self.sigma = []
		self.estado_inicial = ''
		self.delta = {}

	def cargar_desde_archivo(self, nombre_archivo):
		archivo = open(nombre_archivo)
		tuplas = [];
		
		while True:
			linea = archivo.readline()

			if not linea:
				break

			if linea[0] == "*" or linea[0] == '\n' :
				linea = None

			elif linea[0:2] == '#T':
				tabla = ""
				while True:
				 	l = archivo.readline()
				 	if not l or l[0] == "*" or l[0] == '\n':
				 		break
				 	
				 	elif l[0] == '#' and l[0:2] != '##':
				 		linea = l
				 		break
				 	else:
				 		tabla += l
				tuplas.append((linea, tabla))
				linea = None

			if linea:
				tuplas.append((linea, archivo.readline()))
		self.__tupla_a_dfa(tuplas)

	
	def __tupla_a_dfa(self, tuplas):

		parse = {
			'S' : self.set_sigma,
			'Q' : self.set_estados,
			'I' : self.set_estado_inicial,
			'F' : self.set_estados_finales,
			'T' : self.contruir_tabla
		}

		for tupla in tuplas:
			elemento = str(tupla[0]).split("#")[-1]
			elemento = elemento.split("\n")[0]
			elemento = elemento.split(" ")[0]
			try:
				parse[elemento](tupla[1])
			except Exception, e:
				print e
				print "Elemento desconocido " + elemento

	def set_estados(self, estados):
		estados  = estados.split(",")
		for estado in estados:
			estado = estado.split("\n")[0]
			if estado != '' :
				self.estados.append(estado)

	def set_sigma(self, sigma):
		sigma  = sigma.split(",")
		for simbolo in sigma:
			simbolo = simbolo.split("\n")[0]
			if simbolo != '' :
				self.sigma.append(simbolo)

	def set_estado_inicial(self, estado_inicial):
		self.estado_inicial = str(estado_inicial).split("\n")[0]

	def set_estados_finales(self, estados):
		estados  = estados.split(",")
		for estado in estados:
			estado = estado.split("\n")[0]
			if estado != '' :
				self.estados_finales.append(estado)

	def contruir_tabla(self, tabla):
		transiciones = tabla.split("\n")
		for transicion in transiciones:
			f = transicion.split(",")
			if len(f) == 3:
			 	origen = f[0].split(" ")[0]
			 	simbolo = f[1].split(" ")[0]
			 	destino = f[2].split(" ")[0]
			 	self.agrega_transicion(origen, simbolo, destino)
		print self.delta

	def agrega_transicion(self, origen, simbolo, destino):
		if self.delta.has_key(origen):
			self.delta[origen].update({simbolo :  destino})
		else:
			self.delta[origen] = {simbolo : destino}
	
	def aplicar_delta(self, estado, simbolo):
		if self.delta.has_key(estado):
			if self.delta[estado].has_key(simbolo):
				return self.delta[estado][simbolo]
		return None

	def estados_alcanzables(self):
		alcanzables = {self.estado_inicial:0}
		a_verificar = [self.estado_inicial]

		while a_verificar:
			estado = a_verificar.pop()
			for simbolo in self.sigma:
				alcanzado  = self.aplicar_delta(estado, simbolo)
				if alcanzado and not alcanzables.has_key(alcanzado):
					print "d(" + estado + ", " + simbolo + ") -> " + alcanzado
					a_verificar.append(alcanzado)
					alcanzables.update({alcanzado:0})
		
		return alcanzables.keys()		

	
	def __repr__(self):
		s  = "estados: " + str(self.estados)
		s  = "estados finales: " + str(self.estados_finales)
		s += "\nsigma : " + str(self.sigma) 
		s += "\nestado inicial : " + self.estado_inicial 
		return s

if __name__ == '__main__':
	dfa =  Dfa()
	dfa.cargar_desde_archivo("example.txt")
	print dfa.estados_alcanzables()
	print dfa