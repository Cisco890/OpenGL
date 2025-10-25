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

skyboxTextures = ["skybox/right.jpg",
				  "skybox/left.jpg",
				  "skybox/top.jpg",
				  "skybox/bottom.jpg",
				  "skybox/front.jpg",
				  "skybox/back.jpg"]

rend.CreateSkybox(skyboxTextures)


faceModel = Model("models/hola.obj")
faceModel.AddTexture("textures/hola.bmp")
faceModel.position.z = -5

rend.scene.append(faceModel)

isRunning = True

while isRunning:

	deltaTime = clock.tick(60) / 1000

	rend.elapsedTime += deltaTime

	keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			isRunning = False

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				rend.ToggleFilledMode()

			# Fragment Shaders
			if event.key == pygame.K_1:
				# K1: fragment_shader normal
				currFragmentShader = fragment_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

			if event.key == pygame.K_2:
				# K2: radioactive_shader (fucsia transparente)
				currFragmentShader = radioactive_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=True)

			if event.key == pygame.K_3:
				# K3: glitch_shader (corrupción digital)
				currFragmentShader = glitch_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

			# Vertex Shaders
			if event.key == pygame.K_5:
				# K5: vertex_shader normal
				currVertexShader = vertex_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=(currFragmentShader == radioactive_shader))

			if event.key == pygame.K_6:
				# K6: wave_shader (glitch distortion)
				currVertexShader = wave_shader
				rend.SetShaders(currVertexShader, currFragmentShader, useBlending=(currFragmentShader == radioactive_shader))





	if keys[K_UP]:
		rend.camera.position.z += 1 * deltaTime

	if keys[K_DOWN]:
		rend.camera.position.z -= 1 * deltaTime

	if keys[K_RIGHT]:
		rend.camera.position.x += 1 * deltaTime

	if keys[K_LEFT]:
		rend.camera.position.x -= 1 * deltaTime



	if keys[K_w]:
		rend.pointLight.z -= 10 * deltaTime

	if keys[K_s]:
		rend.pointLight.z += 10 * deltaTime

	if keys[K_a]:
		rend.pointLight.x -= 10 * deltaTime

	if keys[K_d]:
		rend.pointLight.x += 10 * deltaTime

	if keys[K_q]:
		rend.pointLight.y -= 10 * deltaTime

	if keys[K_e]:
		rend.pointLight.y += 10 * deltaTime


	if keys[K_z]:
		if rend.value > 0.0:
			rend.value -= 1 * deltaTime

	if keys[K_x]:
		if rend.value < 1.0:
			rend.value += 1 * deltaTime



	faceModel.rotation.y += 45 * deltaTime


	rend.Render()
	pygame.display.flip()

pygame.quit()