"""
Controles:
- F: Toggle Filled Mode

Shaders:
- 1-4: Fragment Shaders (1: Normal, 2: Radioactive, 3: Glitch, 4: Threshold)
- 5-8: Vertex Shaders (5: Normal, 6: Wave, 7: Expand, 8: Slime)

Modelos:
- P: Modelo 1 (hola.obj)
- O: Modelo 2 (among.obj)
- I: Modelo 3 (DJ.obj)

Cámara (Teclado):
- Flechas ←→: Rotar horizontalmente alrededor del modelo
- Flechas ↑↓: Rotar verticalmente alrededor del modelo
- Q/E: Zoom in/out

Cámara (Mouse):
- Click izquierdo + Arrastrar: Rotar cámara alrededor del modelo
- Scroll: Zoom in/out

Otros:
- W/A/S/D: Mover luz
- Z/X: Ajustar valor de shader
"""

import pygame
import pygame.display
from pygame.locals import *

import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from vertexShaders import *
from fragmentShaders import *

width = 960
height = 540

deltaTime = 0.0


screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()


rend = Renderer(screen)
rend.pointLight = glm.vec3(1,1,1)

currVertexShader = vertex_shader
currFragmentShader = fragment_shader

rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

skyboxTextures = ["skybox/posx.jpg",
				  "skybox/negx.jpg",
				  "skybox/posy.jpg",
				  "skybox/negy.jpg",
				  "skybox/posz.jpg",
				  "skybox/negz.jpg"]

rend.CreateSkybox(skyboxTextures)


# Crear los 3 modelos
model1 = Model("models/hola.obj")
model1.AddTexture("textures/hola.bmp")

model2 = Model("models/among.obj")
model2.AddTexture("textures/among_t.bmp")

model3 = Model("models/DJ.obj")
model3.AddTexture("textures/Dj_t.bmp")

# Lista de modelos y configuraciones de transformación
models = [model1, model2, model3]

modelScales = [
	0.6,    # Hola
	0.004,  # Among (reducido para encuadrar en cámara)
	0.0025  # DJ
]

# Altura donde queremos que descanse la base de cada modelo (mundo)
modelBaseHeights = [
	-1.1,
	-1.1,
	-1.05
]

# Ajuste en Z relativo al punto de mira de la cámara
modelZOffsets = [
	-0.6,
	-0.8,
	-1.0
]

# Rotaciones iniciales opcionales (en grados)
modelRotations = [
	(0.0, 20.0, 0.0),   # Hola ligeramente girado
	(0.0, 160.0, 0.0),  # Among mirando hacia la cámara
	(0.0, 180.0, 0.0)   # DJ centrado
]

def apply_model_transform(index: int) -> None:
	"""Restablece posición, escala y rotación del modelo activo."""
	model = models[index]
	scale_value = modelScales[index]
	model.scale = glm.vec3(scale_value)
	model.rotation = glm.vec3(*modelRotations[index])

	# Colocar el centro del modelo en frente de la cámara y ajustar su altura
	camera_focus = rend.camera.target
	model_half_height = model.boundsHalfExtent.y * scale_value
	center_y = modelBaseHeights[index] + model_half_height

	model.position = glm.vec3(
		camera_focus.x,
		center_y,
		camera_focus.z + modelZOffsets[index]
	)

for idx in range(len(models)):
	apply_model_transform(idx)

currentModelIndex = 0

# Agregar solo el primer modelo a la escena
rend.scene.append(models[currentModelIndex])

# Variables para control del mouse
mousePressed = False
lastMouseX = 0
lastMouseY = 0

isRunning = True

while isRunning:

	deltaTime = clock.tick(60) / 1000

	rend.elapsedTime += deltaTime

	keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			isRunning = False

		# Control con el mouse
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:  # Botón izquierdo
				mousePressed = True
				lastMouseX, lastMouseY = event.pos
			elif event.button == 4:  # Scroll hacia arriba (Zoom in)
				rend.camera.Zoom(-1)
			elif event.button == 5:  # Scroll hacia abajo (Zoom out)
				rend.camera.Zoom(1)

		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				mousePressed = False

		elif event.type == pygame.MOUSEMOTION:
			if mousePressed:
				mouseX, mouseY = event.pos
				deltaX = mouseX - lastMouseX
				deltaY = mouseY - lastMouseY
				
				# Movimiento horizontal (órbita)
				rend.camera.OrbitHorizontal(deltaX)
				# Movimiento vertical (arriba/abajo)
				rend.camera.OrbitVertical(-deltaY)
				
				lastMouseX = mouseX
				lastMouseY = mouseY

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				rend.ToggleFilledMode()

			# Fragment Shaders
			if event.key == pygame.K_1:
				currFragmentShader = fragment_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

			if event.key == pygame.K_2:
				currFragmentShader = radioactive_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=True)

			if event.key == pygame.K_3:
				currFragmentShader = glitch_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

			if event.key == pygame.K_4:
				currFragmentShader = threshold_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

			# Vertex Shaders
			if event.key == pygame.K_5:
				currVertexShader = vertex_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=(currFragmentShader == radioactive_shader))

			if event.key == pygame.K_6:
				currVertexShader = wave_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=(currFragmentShader == radioactive_shader))

			if event.key == pygame.K_7:
				currVertexShader = expand_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=(currFragmentShader == radioactive_shader))

			if event.key == pygame.K_8:
				currVertexShader = slime_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=(currFragmentShader == radioactive_shader))

			# Cambio de modelos con P, O, I
			if event.key == pygame.K_p:
				# Remover modelo actual de la escena
				rend.scene.remove(models[currentModelIndex])
				# Cambiar al modelo 1 (hola.obj)
				currentModelIndex = 0
				# Restablecer transformaciones predeterminadas y agregarlo
				apply_model_transform(currentModelIndex)
				rend.scene.append(models[currentModelIndex])

			if event.key == pygame.K_o:
				# Remover modelo actual de la escena
				rend.scene.remove(models[currentModelIndex])
				# Cambiar al modelo 2 (among.obj)
				currentModelIndex = 1
				apply_model_transform(currentModelIndex)
				rend.scene.append(models[currentModelIndex])

			if event.key == pygame.K_i:
				# Remover modelo actual de la escena
				rend.scene.remove(models[currentModelIndex])
				# Cambiar al modelo 3 (DJ.obj)
				currentModelIndex = 2
				apply_model_transform(currentModelIndex)
				rend.scene.append(models[currentModelIndex])





	# Controles de teclado para la cámara orbital
	# Flechas: Rotar alrededor del modelo
	if keys[pygame.K_LEFT]:
		rend.camera.OrbitHorizontal(-100 * deltaTime)

	if keys[pygame.K_RIGHT]:
		rend.camera.OrbitHorizontal(100 * deltaTime)

	if keys[pygame.K_UP]:
		rend.camera.OrbitVertical(100 * deltaTime)

	if keys[pygame.K_DOWN]:
		rend.camera.OrbitVertical(-100 * deltaTime)

	# Q/E: Zoom in/out
	if keys[pygame.K_q]:
		rend.camera.Zoom(-5 * deltaTime)

	if keys[pygame.K_e]:
		rend.camera.Zoom(5 * deltaTime)


	# W/A/S/D: Mover luz
	if keys[pygame.K_w]:
		rend.pointLight.z -= 10 * deltaTime

	if keys[pygame.K_s]:
		rend.pointLight.z += 10 * deltaTime

	if keys[pygame.K_a]:
		rend.pointLight.x -= 10 * deltaTime

	if keys[pygame.K_d]:
		rend.pointLight.x += 10 * deltaTime


	# Z/X: Ajustar valor de shaders
	if keys[pygame.K_z]:
		if rend.value > 0.0:
			rend.value -= 1 * deltaTime

	if keys[pygame.K_x]:
		if rend.value < 1.0:
			rend.value += 1 * deltaTime



	# Rotar el modelo actual
	models[currentModelIndex].rotation.y += 45 * deltaTime


	rend.Render()
	pygame.display.flip()

pygame.quit()