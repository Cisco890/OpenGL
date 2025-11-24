import glm # pip install PyGLM
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from camera import Camera
from skybox import Skybox
from buffer import Buffer

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()
        
        glClearColor(0.2, 0.2, 0.2, 1.0)

        glEnable(GL_DEPTH_TEST)
        glViewport(0,0, self.width, self.height)

        self.camera = Camera(self.width, self.height)

        self.scene = []
        

        self.filledMode = False
        self.ToggleFilledMode()

        self.activeShader = None
        self.useBlending = False

        self.skybox = None

        self.pointLight = glm.vec3(0,0,0)
        self.ambientLight = 0.1


        self.value = 0.0;
        self.elapsedTime = 0.0;

        # Simple shader to draw debug points at model centers
        self.point_vertex_shader = '''
#version 330 core
layout(location = 0) in vec3 inPosition;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
void main(){
    gl_Position = projectionMatrix * viewMatrix * vec4(inPosition, 1.0);
}
'''

        self.point_fragment_shader = '''
#version 330 core
out vec4 fragColor;
void main(){
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
'''

        try:
            self.pointProgram = compileProgram( compileShader(self.point_vertex_shader, GL_VERTEX_SHADER),
                                                compileShader(self.point_fragment_shader, GL_FRAGMENT_SHADER) )
        except Exception:
            self.pointProgram = None



    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera


    def ToggleFilledMode(self):
        self.filledMode = not self.filledMode

        if self.filledMode:
            glEnable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT, GL_FILL)
        else:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    def SetShaders(self, vertexShader, fragmentShader, useBlending=False):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
            self.useBlending = useBlending
        else:
            self.activeShader = None
            self.useBlending = False


    def Render(self):
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        self.camera.Update()

        # Asegurar que el depth test esté habilitado
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)

        # Renderizar modelos primero
        # Activar/desactivar blending según el shader activo
        if self.useBlending:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        else:
            glDisable(GL_BLEND)

        if self.activeShader is not None:
            glUseProgram(self.activeShader)

            glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "viewMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix) )

            glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "projectionMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix) )

            glUniform3fv( glGetUniformLocation(self.activeShader, "pointLight"), 1, glm.value_ptr(self.pointLight) )
            glUniform1f( glGetUniformLocation(self.activeShader, "ambientLight"), self.ambientLight )

            glUniform1f( glGetUniformLocation(self.activeShader, "value"), self.value )
            glUniform1f( glGetUniformLocation(self.activeShader, "time"), self.elapsedTime )


            glUniform1i( glGetUniformLocation(self.activeShader, "tex0"), 0)
            glUniform1i( glGetUniformLocation(self.activeShader, "tex1"), 1)



        for obj in self.scene:

            if self.activeShader is not None:
                glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "modelMatrix"),
                                1, GL_FALSE, glm.value_ptr( obj.GetModelMatrix() ) )

            obj.Render()

        # Asegurar que el blending esté desactivado antes del skybox
        glDisable(GL_BLEND)

        # Renderizar skybox primero para que no sobreescriba los pixeles de los modelos
        if self.skybox is not None:
            # Asegurar blending desactivado para skybox
            glDisable(GL_BLEND)
            self.skybox.Render()

        # Activar/desactivar blending según el shader activo para modelos
        if self.useBlending:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        else:
            glDisable(GL_BLEND)

        if self.activeShader is not None:
            glUseProgram(self.activeShader)

            glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "viewMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix) )

            glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "projectionMatrix"),
                                1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix) )

            glUniform3fv( glGetUniformLocation(self.activeShader, "pointLight"), 1, glm.value_ptr(self.pointLight) )
            glUniform1f( glGetUniformLocation(self.activeShader, "ambientLight"), self.ambientLight )

            glUniform1f( glGetUniformLocation(self.activeShader, "value"), self.value )
            glUniform1f( glGetUniformLocation(self.activeShader, "time"), self.elapsedTime )


            glUniform1i( glGetUniformLocation(self.activeShader, "tex0"), 0)
            glUniform1i( glGetUniformLocation(self.activeShader, "tex1"), 1)

        for obj in self.scene:

            if self.activeShader is not None:
                glUniformMatrix4fv( glGetUniformLocation(self.activeShader, "modelMatrix"),
                                1, GL_FALSE, glm.value_ptr( obj.GetModelMatrix() ) )

            obj.Render()

        # Draw debug points at each model world center to verify rendering
        if self.pointProgram is not None and len(self.scene) > 0:
            centers = []
            for obj in self.scene:
                wc = glm.vec3(
                    obj.position.x - (obj.originOffset.x * obj.scale.x),
                    obj.position.y - (obj.originOffset.y * obj.scale.y),
                    obj.position.z - (obj.originOffset.z * obj.scale.z)
                )
                centers.extend([wc.x, wc.y, wc.z])

            buf = Buffer(centers)
            glUseProgram(self.pointProgram)
            # set view/projection
            glUniformMatrix4fv( glGetUniformLocation(self.pointProgram, "viewMatrix"), 1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix) )
            glUniformMatrix4fv( glGetUniformLocation(self.pointProgram, "projectionMatrix"), 1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix) )
            glPointSize(8.0)
            buf.Use(0, 3)
            glDrawArrays(GL_POINTS, 0, int(len(centers)/3))
            glDisableVertexAttribArray(0)
            glUseProgram(0)

