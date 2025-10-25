from OpenGL.GL import *
from obj import Obj
from buffer import Buffer

import glm

import pygame
import os

class Model(object):
	def __init__(self, filename):
		self.objFile = Obj(filename)

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)

		self.BuildBuffers()

		self.textures = []

	def GetModelMatrix(self):

		identity = glm.mat4(1)

		translateMat = glm.translate(identity, self.position)

		pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
		yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
		rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

		rotationMat = pitchMat * yawMat * rollMat

		scaleMat = glm.scale(identity, self.scale)

		return translateMat * rotationMat * scaleMat


	def BuildBuffers(self):

		positions = []
		texCoords = []
		normals = []

		self.vertexCount = 0

		for face in self.objFile.faces:

			facePositions = []
			faceTexCoords = []
			faceNormals = []

			# Helper defaults
			default_tex = [0.0, 0.0]
			default_norm = [0.0, 0.0, 1.0]

			for i in range(len(face)):
				fv = face[i]
				# vertex index (required)
				v_idx = fv[0] - 1
				facePositions.append(self.objFile.vertices[v_idx])

				# texcoord index (optional)
				if len(fv) > 1 and fv[1] is not None:
					try:
						vt = self.objFile.texCoords[fv[1] - 1]
					except Exception:
						vt = default_tex
				else:
					vt = default_tex
				faceTexCoords.append(vt)

				# normal index (optional)
				if len(fv) > 2 and fv[2] is not None:
					try:
						vn = self.objFile.normals[fv[2] - 1]
					except Exception:
						vn = default_norm
				else:
					vn = default_norm
				faceNormals.append(vn)


			# Append triangle (3 verts) data
			for value in facePositions[0]: positions.append(value)
			for value in facePositions[1]: positions.append(value)
			for value in facePositions[2]: positions.append(value)

			for value in faceTexCoords[0]: texCoords.append(value)
			for value in faceTexCoords[1]: texCoords.append(value)
			for value in faceTexCoords[2]: texCoords.append(value)

			for value in faceNormals[0]: normals.append(value)
			for value in faceNormals[1]: normals.append(value)
			for value in faceNormals[2]: normals.append(value)

			self.vertexCount += 3

			if len(face) == 4:
				for value in facePositions[0]: positions.append(value)
				for value in facePositions[2]: positions.append(value)
				for value in facePositions[3]: positions.append(value)

				for value in faceTexCoords[0]: texCoords.append(value)
				for value in faceTexCoords[2]: texCoords.append(value)
				for value in faceTexCoords[3]: texCoords.append(value)

				for value in faceNormals[0]: normals.append(value)
				for value in faceNormals[2]: normals.append(value)
				for value in faceNormals[3]: normals.append(value)

				self.vertexCount += 3


		self.posBuffer = Buffer(positions)
		self.texCoordsBuffer = Buffer(texCoords)
		self.normalsBuffer = Buffer(normals)


	def AddTexture(self, filename):
		# Buscar la textura en varias ubicaciones razonables antes de fallar
		candidates = [filename]
		# Ruta relativa a este archivo (script) -> proyecto/textures/...
		script_dir = os.path.dirname(os.path.abspath(__file__))
		candidates.append(os.path.join(script_dir, filename))
		# Si el usuario pasó solo el nombre, buscar en carpeta textures
		base = os.path.basename(filename)
		candidates.append(os.path.join(script_dir, 'textures', base))
		# también probar en cwd/textures
		candidates.append(os.path.join(os.getcwd(), filename))
		candidates.append(os.path.join(os.getcwd(), 'textures', base))

		found = None
		for path in candidates:
			if path and os.path.exists(path):
				found = path
				break

		if not found:
			raise FileNotFoundError(f"Texture file '{filename}' not found. Tried: {candidates}")

		try:
			textureSurface = pygame.image.load(found)
		except Exception as e:
			raise RuntimeError(f"Failed to load texture '{found}': {e}")

		textureData = pygame.image.tostring(textureSurface, "RGB", True)

		texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D,
				 0,
				  GL_RGB,
				  textureSurface.get_width(),
				  textureSurface.get_height(),
				  0,
				  GL_RGB,
				  GL_UNSIGNED_BYTE,
				  textureData)

		glGenerateMipmap(GL_TEXTURE_2D)

		self.textures.append(texture)


	def Render(self):

		# Dar la textura
		for i in range(len(self.textures)):
			glActiveTexture(GL_TEXTURE0 + i)
			glBindTexture(GL_TEXTURE_2D, self.textures[i])


		self.posBuffer.Use(0, 3)
		self.texCoordsBuffer.Use(1, 2)
		self.normalsBuffer.Use(2, 3)


		glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

		glDisableVertexAttribArray(0)
		glDisableVertexAttribArray(1)
		glDisableVertexAttribArray(2)




