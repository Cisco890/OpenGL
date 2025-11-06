import glm
import math

class Camera(object):
	def __init__(self, width, height):

		self.screenWidth = width
		self.screenHeight = height
		
		self.position = glm.vec3(0,0,0)

		# Angulos de Euler
		self.rotation = glm.vec3(0,0,0)

		self.viewMatrix = None

		# Parámetros para cámara orbital
		self.target = glm.vec3(0, 0, -5)  # Punto al que mira la cámara (centro del modelo)
		self.distance = 4.0  # Distancia desde el target
		self.orbitAngleX = 0.0  # Ángulo horizontal (0° = frente)
		self.orbitAngleY = 15.0  # Ángulo vertical (ligeramente desde arriba)
		
		# Límites de la cámara
		self.minDistance = 1.0
		self.maxDistance = 50.0
		self.minOrbitY = -85.0  # Límite inferior (grados)
		self.maxOrbitY = 85.0   # Límite superior (grados)
		
		# Sensibilidad
		self.rotationSensitivity = 0.5
		self.zoomSensitivity = 0.5

		self.CreateProjectionMatrix(60, 0.1, 1000)


	def Update(self):
		# Limitar ángulos
		self.orbitAngleY = max(self.minOrbitY, min(self.maxOrbitY, self.orbitAngleY))
		self.distance = max(self.minDistance, min(self.maxDistance, self.distance))
		
		# Calcular posición de la cámara basada en órbita
		radX = math.radians(self.orbitAngleX)
		radY = math.radians(self.orbitAngleY)
		
		# Posición en coordenadas esféricas
		x = self.target.x + self.distance * math.cos(radY) * math.sin(radX)
		y = self.target.y + self.distance * math.sin(radY)
		z = self.target.z + self.distance * math.cos(radY) * math.cos(radX)
		
		self.position = glm.vec3(x, y, z)
		
		# Crear matriz de vista mirando al target
		self.viewMatrix = glm.lookAt(self.position, self.target, glm.vec3(0, 1, 0))


	def OrbitHorizontal(self, angle):
		"""Rotar la cámara horizontalmente alrededor del modelo"""
		self.orbitAngleX += angle * self.rotationSensitivity

	def OrbitVertical(self, angle):
		"""Rotar la cámara verticalmente alrededor del modelo"""
		self.orbitAngleY += angle * self.rotationSensitivity

	def Zoom(self, amount):
		"""Acercar o alejar la cámara del modelo"""
		self.distance += amount * self.zoomSensitivity

	def SetTarget(self, target):
		"""Establecer el punto al que mira la cámara"""
		self.target = target


	def CreateProjectionMatrix(self, fov, nearPlane, farPlane):
		self.projectionMatrix = glm.perspective( glm.radians(fov), self.screenWidth / self.screenHeight, nearPlane, farPlane)