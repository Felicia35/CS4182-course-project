from OpenGL.GL import *
import PIL.Image as Image
import utils

# Skybox class
class Skybox:
    textureIDs = []
    MAP_WIDTH = 16
    CELL_WIDTH = 16
    MAP = MAP_WIDTH * CELL_WIDTH / 2

    def __init__(self):
        pass

    def init(self):
        # back, front, bottom, top, left, right
        textureNames = ["sunset_negZ.bmp", "sunset_posZ.bmp", "sunset_negY.bmp", "sunset_posY.bmp", "sunset_negX.bmp", "sunset_posX.bmp"]
        for i in range(6):
            textureID = utils.loadTexture("../img/" + textureNames[i])
            self.textureIDs.append(textureID)

    def createSkybox(self, x, y, z, boxWidth, boxHeight, boxDepth):
        # Abtain lighting status
        lighing = glGetBooleanv(GL_LIGHTING)

        # Calculate width, height, depth of skybox
        width = self.MAP * boxWidth / 8
        height = self.MAP * boxHeight / 8
        depth = self.MAP * boxDepth / 8

        # Calculate skybox center
        x = x + self.MAP / 8 - width / 2
        y = y + self.MAP / 24 - height / 2
        z = z + self.MAP / 8 - depth / 2

        # Disable lighting
        glDisable(GL_LIGHTING)

        # glCullFace(GL_FRONT)

        glDepthMask(GL_FALSE)

        glPushMatrix()

        glLoadIdentity()

        glTranslatef(0, 0, 0)
        glEnable(GL_TEXTURE_2D)

        # Draw back
        glBindTexture(GL_TEXTURE_2D, self.textureIDs[0])
        
        glBegin(GL_QUADS)

        # Assign texture coordinates and vertex positions
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x + width, y, z)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x + width, y + height, z)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x, y + height, z)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x, y, z)

        glEnd()

        # Draw front
        glBindTexture(GL_TEXTURE_2D, self.textureIDs[1])
        
        glBegin(GL_QUADS)

        # Assign texture coordinates and vertex positions
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x, y, z + depth)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x, y + height, z + depth)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x + width, y + height, z + depth)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x + width, y, z + depth)

        glEnd()

        # Draw bottom
        glBindTexture(GL_TEXTURE_2D, self.textureIDs[2])

        glBegin(GL_QUADS)

        # Assign texture coordinates and vertex positions
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x, y, z)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x, y, z + depth)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x + width, y, z + depth)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x + width, y, z)

        glEnd()

        # Draw top
        glBindTexture(GL_TEXTURE_2D, self.textureIDs[3])

        glBegin(GL_QUADS)

        # Assign texture coordinates and vertex positions
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x + width, y + height, z)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x + width, y + height, z + depth)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x, y + height, z + depth)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x, y + height, z)

        glEnd()

        # Draw left
        glBindTexture(GL_TEXTURE_2D, self.textureIDs[4])

        glBegin(GL_QUADS)

        # Assign texture coordinates and vertex positions
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x, y + height, z)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x, y + height, z + depth)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x, y, z + depth)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x, y, z)

        glEnd()

        # Draw right
        glBindTexture(GL_TEXTURE_2D, self.textureIDs[5])

        glBegin(GL_QUADS)

        # Assign texture coordinates and vertex positions
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x + width, y, z)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x + width, y, z + depth)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x + width, y + height, z + depth)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x + width, y + height, z)

        glEnd()

        glPopMatrix()

        if lighing == GL_TRUE:
            glEnable(GL_LIGHTING)


        glDisable(GL_TEXTURE_2D)

        glDepthMask(GL_TRUE)
        # glCullFace(GL_BACK)

