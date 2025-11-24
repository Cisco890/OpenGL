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
from OpenGL.GL import glDisable, GL_CULL_FACE, glPolygonMode, GL_FRONT_AND_BACK, GL_FILL
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

# Disable face culling for testing (some models may have inconsistent winding)
glDisable(GL_CULL_FACE)
glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

currVertexShader = vertex_shader
currFragmentShader = flat_shader  # use flat shader to verify geometry rendering

rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

skyboxTextures = ["skybox/posx.jpg",
				  "skybox/negx.jpg",
				  "skybox/posy.jpg",
				  "skybox/negy.jpg",
				  "skybox/posz.jpg",
				  "skybox/negz.jpg"]

rend.CreateSkybox(skyboxTextures)

# Load Plants vs. Zombies models
plant1 = Model("source/plant1.obj")
plant1.AddTexture("textures/plant1_texture.bmp")
plant1.position = glm.vec3(-30, -1, -50)  # Updated position
plant1.scale = glm.vec3(0.5)  # Adjusted scale

plant2 = Model("source/plant2.obj")
plant2.AddTexture("textures/plant2_texture.bmp")
plant2.position = glm.vec3(-10, -1, -50)  # Updated position
plant2.scale = glm.vec3(0.5)  # Adjusted scale

plant3 = Model("source/plant3.obj")
plant3.AddTexture("textures/plant3_texture.bmp")
plant3.position = glm.vec3(-20, -1, -60)  # Updated position
plant3.scale = glm.vec3(0.5)  # Adjusted scale

zombie1 = Model("source/zombie1.obj")
zombie1.AddTexture("textures/zombie2_texture.bmp")
zombie1.position = glm.vec3(20, -1, -50)  # Updated position
zombie1.scale = glm.vec3(0.5)  # Adjusted scale

zombie2 = Model("source/zombie2.obj")
zombie2.AddTexture("textures/zombie2_texture.bmp")
zombie2.position = glm.vec3(40, -1, -60)  # Updated position
zombie2.scale = glm.vec3(0.5)  # Adjusted scale

# Define a models list to group all models (don't add to scene twice)
models = [plant1, plant2, plant3, zombie1, zombie2]

# Ensure the currentModelIndex is initialized properly
currentModelIndex = 0

# Variables para control del mouse
mousePressed = False
lastMouseX = 0
lastMouseY = 0

# Function to apply transformations to a model
def apply_model_transform(index: int) -> None:
    """Applies default transformations to the model at the given index."""
    model = models[index]
    model.scale = glm.vec3(1.0)  # Default scale
    model.rotation = glm.vec3(0.0, 0.0, 0.0)  # Default rotation
    model.position = glm.vec3(0.0, -1.0, -5.0)  # Default position

# Configure camera to orbit around the group center so all models stay in view
rend.camera.SetTarget(glm.vec3(0.0, -1.0, -20.0))
rend.camera.distance = 20.0
rend.camera.orbitAngleX = 0.0
rend.camera.orbitAngleY = 10.0

# Move the models far away to match the camera's new position
plant1.position = glm.vec3(-30, -1, -50)
plant2.position = glm.vec3(-10, -1, -50)
plant3.position = glm.vec3(-20, -1, -60)
zombie1.position = glm.vec3(20, -1, -50)
zombie2.position = glm.vec3(40, -1, -60)

# Ensure models are upright and aligned
plant1.rotation = glm.vec3(0, 0, 0)
plant2.rotation = glm.vec3(0, 0, 0)
plant3.rotation = glm.vec3(0, 0, 0)
zombie1.rotation = glm.vec3(0, 0, 0)
zombie2.rotation = glm.vec3(0, 0, 0)

# Adjust camera near and far planes to avoid clipping
rend.camera.nearPlane = 0.1
rend.camera.farPlane = 100.0

# Increase models' scale for better visibility
plant1.scale = glm.vec3(1.0)
plant2.scale = glm.vec3(1.0)
plant3.scale = glm.vec3(1.0)
zombie1.scale = glm.vec3(1.0)
zombie2.scale = glm.vec3(1.0)

# Keep the flat shader active for debugging geometry visibility.
# To restore textured rendering, press keys 1-4 in the application.
currVertexShader = vertex_shader
currFragmentShader = flat_shader
rend.SetShaders(currVertexShader, currFragmentShader, useBlending=False)

# Position models around the scene center (near the camera's target)
plant1.position = glm.vec3(-6, -1, -20)
plant2.position = glm.vec3(-2, -1, -20)
plant3.position = glm.vec3(-4, -1, -20)
zombie1.position = glm.vec3(2, -1, -20)
zombie2.position = glm.vec3(6, -1, -20)

# Normalize model scales so all models are a reasonable size and place their base at camera target height
desired_size = 4.0
for m in models:
	max_dim = max(m.boundsSize.x, m.boundsSize.y, m.boundsSize.z)
	if max_dim > 0:
		scale_factor = desired_size / max_dim
	else:
		scale_factor = 1.0
	m.scale = glm.vec3(scale_factor)
	# Place the model so its bottom rests near the camera target Y
	m.position.z = rend.camera.target.z
	m.position.y = rend.camera.target.y + (m.boundsHalfExtent.y * scale_factor)

# Populate the renderer scene once (clear previous entries to avoid duplicates)
rend.scene.clear()
rend.scene.extend(models)

# Compute world centers and frame camera to fit all models
world_centers = []
for m in models:
	wc = glm.vec3(
		m.position.x - (m.originOffset.x * m.scale.x),
		m.position.y - (m.originOffset.y * m.scale.y),
		m.position.z - (m.originOffset.z * m.scale.z)
	)
	world_centers.append(wc)

if len(world_centers) > 0:
	centroid = glm.vec3(0.0)
	for wc in world_centers:
		centroid += wc
	centroid /= len(world_centers)

	# compute max distance from centroid
	max_dist = 0.0
	for wc in world_centers:
		d = glm.length(wc - centroid)
		if d > max_dist:
			max_dist = d

	# place camera to look at centroid and set distance to fit all models
	rend.camera.SetTarget(centroid)
	# set a distance that fits the radius with some padding
	rend.camera.distance = max(5.0, max_dist * 3.0)
	print(f"[AUTOFRAME] centroid={centroid}, max_dist={max_dist}, camera.distance={rend.camera.distance}")

# --- Debug info: print scene and camera state to help diagnose visibility issues ---
print(f"[DEBUG] Scene model count: {len(rend.scene)}")
for i, m in enumerate(rend.scene):
	try:
		print(f"[DEBUG] Model {i}: pos={m.position}, scale={m.scale}, rotation={m.rotation}")
		print(f"[DEBUG]   boundsCenter={m.boundsCenter}, halfExtent={m.boundsHalfExtent}")
	except Exception as e:
		print(f"[DEBUG] Model {i}: failed to read properties: {e}")

print(f"[DEBUG] Camera target={rend.camera.target}, distance={rend.camera.distance}, orbitX={rend.camera.orbitAngleX}, orbitY={rend.camera.orbitAngleY}")
print(f"[DEBUG] Projection matrix: (first row) {rend.camera.projectionMatrix[0]}")

isRunning = True
printed_once = False

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



	rend.Render()
	pygame.display.flip()
	# One-time per-run debug: print camera position and model world centers
	if not printed_once:
		# Ensure camera is updated to compute position
		rend.camera.Update()
		print(f"[DBG] camera.position = {rend.camera.position}")
		for i, m in enumerate(models):
			# world_center = m.position + rotation * ( - originOffset * scale )
			# rotation is zero for these models, so skip rotation math
			world_center = glm.vec3(
				m.position.x - (m.originOffset.x * m.scale.x),
				m.position.y - (m.originOffset.y * m.scale.y),
				m.position.z - (m.originOffset.z * m.scale.z)
			)
			print(f"[DBG] model {i} world_center={world_center}")
			try:
				print(f"[DBG]  vertexCount={m.vertexCount}, textures={len(m.textures)}")
				# print first 3 vertices if available
				verts = getattr(m, 'objFile', None)
				if verts and len(verts.vertices) > 0:
					print(f"[DBG]  first verts: {verts.vertices[:3]}")
			except Exception as e:
				print(f"[DBG]  failed extra info: {e}")
			# compute clip/ndc coordinates for world_center to check frustum
			try:
				clip = rend.camera.projectionMatrix * rend.camera.viewMatrix * glm.vec4(world_center.x, world_center.y, world_center.z, 1.0)
				ndc = glm.vec3(clip.x / clip.w, clip.y / clip.w, clip.z / clip.w)
				print(f"[DBG]  ndc={ndc}")
				# convert to window pixels for convenience
				win_x = int((ndc.x * 0.5 + 0.5) * screen.get_width())
				win_y = int((1.0 - (ndc.y * 0.5 + 0.5)) * screen.get_height())
				print(f"[DBG]  pixel=({win_x},{win_y})")
			except Exception as e:
				print(f"[DBG]  ndc compute failed: {e}")
		printed_once = True

pygame.quit()