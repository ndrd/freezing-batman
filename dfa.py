#!/usr/bin/env python
# -*- coding: utf8 -*-
import json, copy

class Dfa (object):
	# todo funciona con cadenas
	def __init__(self):
		self.estados = []
		self.estados_finales = []
		self.sigma = []
		self.estado_inicial = ""
		self.delta = {}

	def cargar_desde_archivo_txt(self, nombre_archivo):
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

	def cargar_desde_json(self, nombre_archivo):
		archivo = open(nombre_archivo)
		datos = None
		try:
			datos = json.load(archivo)
		except Exception, e:
			print "Archivo invalido " + nombre_archivo

		if datos:
			try:
				self.estados = datos['estados'] 
				self.delta = datos['delta'] 
				self.sigma = datos['sigma'] 
				self.estado_inicial = datos['estado_inicial'] 
				self.estados = datos['estados_finales'] 
			except Exception, e:
				print "Archivo mal formado"
			
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
		alcanzables = [self.estado_inicial]
		a_verificar = [self.estado_inicial]

		while a_verificar:
			estado = a_verificar.pop(0)
			for simbolo in self.sigma:
				alcanzado  = self.aplicar_delta(estado, simbolo)
				if alcanzado and not alcanzado in alcanzables:
					a_verificar.append(alcanzado)
					alcanzables.append(alcanzado)
		
		return alcanzables

	def minimizar(self):
		alcanzables = self.estados_alcanzables()
		estados = list(set(alcanzables)  & set(self.estados))
		estados_finales = list(set(alcanzables) & set(self.estados_finales))

		p0 = [estados_finales, list(set(estados) - set(estados_finales))]
			
		clases_distinguidas = self.particiones_sucesivas(p0)
		clases_distinguidas = self.dic_distinguidas(clases_distinguidas)
		nuevos_estados = self.nuevos_estados(clases_distinguidas)
		nuevos_finales = self.nuevos_estados_finales(clases_distinguidas)
		nuevo_inicial = self.nuevo_estado_inicial(clases_distinguidas)

		dfa_minimizado = Dfa()
		dfa_minimizado.sigma = self.sigma
		dfa_minimizado.estados = nuevos_estados
		dfa_minimizado.estados_finales = nuevos_finales
		dfa_minimizado.estado_inicial = nuevo_inicial
		self.nueva_delta(dfa_minimizado, clases_distinguidas)

		return dfa_minimizado


	def dic_distinguidas(self, clases_distinguidas):
		estados = {}
		for i in range(len(clases_distinguidas)):
			estados.update({i : clases_distinguidas[i]})
		return estados

	def nuevos_estados_finales(self, dic_distinguidas):
		finales = []
		
		for estado in self.estados_finales:
			nuevo_final = self.indice_nueva_clase(estado, dic_distinguidas)
			if nuevo_final != None and nuevo_final not in finales:
				finales.append(nuevo_final)

		return finales

	def nuevo_estado_inicial(self, dic_distinguidas):
		return self.indice_nueva_clase(self.estado_inicial, dic_distinguidas)

	def nuevos_estados(self, dic_distinguidas):
		estados = []
		
		for estado in self.estados:
			estado_nuevo = self.indice_nueva_clase(estado, dic_distinguidas)
			if estado_nuevo != None and estado_nuevo not in estados:
				estados.append(estado_nuevo)

		return estados

	def nueva_delta(self, min_dfa, dic_distinguidas):
		
		for estado in dic_distinguidas.keys():
			viejo_estado = dic_distinguidas[estado][0]

			for simbolo in self.sigma:
				viejo_destino = self.aplicar_delta(viejo_estado, simbolo)
				nuevo_destino = self.indice_nueva_clase(viejo_destino, dic_distinguidas)
				min_dfa.agrega_transicion(estado, simbolo, nuevo_destino)


	def indice_nueva_clase(self, simbolo, dic_distinguidas):
		for k in dic_distinguidas.keys():
			if simbolo in dic_distinguidas[k]:
				return k
		return None

	def particiones_sucesivas(self, p0):
		p1 = self.distingue(p0)
		if p1 == p0:
			return p1
		else:
			return self.particiones_sucesivas(p1)
		
	def distingue(self, p0):
		nueva_particion = []
		particion = copy.deepcopy(p0)

		for clase_equivalencia in particion:
			if len(clase_equivalencia) > 1:

				nueva_clase = [clase_equivalencia.pop(0)]
				elementos_a_comparar = [nueva_clase[0], clase_equivalencia.pop(0)]
				
				while len(elementos_a_comparar) == 2:
					a = elementos_a_comparar.pop(0)
					b = elementos_a_comparar.pop(0)

					distinguible = False

					for simbolo in self.sigma:
						estado_a = self.aplicar_delta(a, simbolo)
						estado_b = self.aplicar_delta(b, simbolo)

						if estado_a == None or estado_b == None:
							continue
						elif self.indice(estado_a, p0) != self.indice(estado_b, p0):
							nueva_particion.append([b])
							distinguible = True
						
					if not distinguible:
						nueva_clase.append(b)
						
					if clase_equivalencia:
						elementos_a_comparar.append(a)
						elementos_a_comparar.append(clase_equivalencia.pop(0))	

				nueva_particion.append(nueva_clase)

			else:
				nueva_particion.append(clase_equivalencia)
		return nueva_particion


	def to_json(self):
		return json.dumps(self.__dict__)

	
	def __repr__(self):
		s  = "estados: " + str(self.estados)
		s  = "estados finales: " + str(self.estados_finales)
		s += "\nsigma : " + str(self.sigma) 
		s += "\nestado inicial : " + self.estado_inicial 
		return s

	def indice(self, elemento, particion):
		for i in range(len(particion)):
			clase = particion[i]
			if elemento in clase:
				return i
		return -1

if __name__ == '__main__':
	dfa =  Dfa()
	dfa.cargar_desde_archivo_txt("example.txt")
	print dfa.to_json()
	mini = dfa.minimizar()
	print "\n\n\n"
	print mini.to_json()
