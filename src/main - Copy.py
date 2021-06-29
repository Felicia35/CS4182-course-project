#!/usr/bin/env python
# -*- coding: utf-8 -*-‘
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random, csv, datetime
import ImportObject
import PIL.Image as Image
import jeep, cone, utils
from skybox import *
import math

windowWidth = 800
windowHeight = 600
lastWindowWidth = 0
lastWindowHeight = 0
isFullScreen = False
aspect = float(windowWidth) / windowHeight;
fov = 90.0
nearZ = 0.1
farZ = 100.0
helpWindow = False
helpWin = 0
mainWin = 0
centered = False

beginTime = 0
countTime = 0
score = 0
finalScore = 0
canStart = False
overReason = ""

moveSpeed = 20.0

#for wheel spinning
tickTime = 0.0
#Frame time(in second)
frameTime = 0.0

#creating objects
objectArray = []
jeep1Obj = jeep.jeep('p')
jeep2Obj = jeep.jeep('g')
jeep3Obj = jeep.jeep('r')

scene = None

star = None
starDL = None

# Physics
a = 2.0
s = 0.0
accumulatedTime = 0.0

allJeeps = [jeep1Obj, jeep2Obj, jeep3Obj]
jeepNum = 0
jeepObj = allJeeps[jeepNum]
#personObj = person.person(10.0,10.0)

#concerned with camera
eyeX = 0.0
eyeY = 3.0
eyeZ = -10.0
midDown = False
topView = False
behindView = True

#concerned with panning
nowX = 0.0
nowY = 0.0

angle = 0.0
radius = 10.0
phi = 0.0

#concerned with scene development
land = 20
gameEnlarge = 10

#concerned with obstacles (cones) & rewards (stars)
coneAmount = 15
starAmount = 5 #val = -10 pts
diamondAmount = 1 #val = deducts entire by 1/2
# diamondObj = diamond.diamond(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))
usedDiamond = False

allcones = []
allstars = []
obstacleCoord = []
rewardCoord = []
ckSense = 5.0

#concerned with lighting#########################!!!!!!!!!!!!!!!!##########
applyLighting = True
attenuation = 1.0

lightIndex = 0;

glLights = [GL_LIGHT0, GL_LIGHT1, GL_LIGHT2]

light0_Position = [-2.0, 2.0, -5.0, 1.0]
light0_Intensity = [0.75, 0.0, 0.0, 0.0]

light1_Position = [2.0, 2.0, 5.0, 1.0]
light1_Intensity = [0.5, 0.5, 0.0, 1.0]

light2_Position = [0.0, 2.0, 1.0, 1.0]
light2_Direction = [0.0, -1.0, 0.0, 0.0]
light2_Ambient = [1.0, 0.0, 1.0, 1.0]
light2_Diffuse = [1.0, 0.0, 1.0, 1.0]

matAmbient = [0.5, 0.5, 0.5, 0.5]
matDiffuse = [0.5, 0.5, 0.5, 1.0]
matSpecular = [0.5, 0.5, 0.5, 1.0]
matShininess  = 100.0

rotateAngle = 0.0
starRotateAngle = 0.0
starScale = 1.0
GKeyPressed = False

filter = 0
fogMode = [GL_EXP, GL_EXP2, GL_LINEAR]
fogFileter = 0
fogColor = [0.5, 0.5, 0.5, 1.0]

class Actor:
    def __init__(self):
        pass

#--------------------------------------developing scene---------------
class Scene:
    axisColor = (0.5, 0.5, 0.5, 0.5)
    axisXColor = (1.0, 0.0, 0.0, 1.0)
    axisYColor = (0.0, 1.0, 0.0, 1.0)
    axisZColor = (0.0, 0.0, 1.0, 1.0)
    axisLength = 50   # Extends to positive and negative on all axes
    landColor = (.47, .53, .6, 0.5) #Light Slate Grey
    landLength = land  # Extends to positive and negative on x and y axis
    landW = 1.0
    landH = 0.0
    cont = gameEnlarge
    skybox = Skybox()
    ufo = None
    ufoPositionX = -10.0
    ufoPosiitonY = 5.0
    ufoPositionZ = 0.0
    ufoDL = None
    star = None
    starPositionX = 0.0
    starPositionY = 8.0
    starPositionZ = 0.0
    starDL = None
    rotateAngle = 0.0

    def __init__(self):
        self.skybox.init()

        self.ufo = ImportObject.ImportedObject("../objects/ufo")

        self.ufo.loadOBJ("../img/")

        self.ufoDL = glGenLists(1)
        glNewList(self.ufoDL, GL_COMPILE)
        self.ufo.drawObject()
        glEndList()

    def update(self, frameTime):
        self.rotateAngle += 15.0 * frameTime
    
    def draw(self):
        # Draw skybox first
        self.drawSkybox()
        self.drawAxis()
        self.drawLand()
        self.drawUFO()
        # self.drawStar()

    def drawAxis(self):
        # Axis X
        glColor4f(self.axisXColor[0], self.axisXColor[1], self.axisXColor[2], self.axisXColor[3])
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(self.axisLength, 0, 0)
        glEnd()

        # Axis Y
        glColor4f(self.axisYColor[0], self.axisYColor[1], self.axisYColor[2], self.axisYColor[3])
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(0, self.axisLength, 0)
        glEnd()

        # Axis Z
        glColor4f(self.axisZColor[0], self.axisZColor[1], self.axisZColor[2], self.axisZColor[3])
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(0, 0, -self.axisLength)
        glEnd()

    def drawLand(self):
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, roadTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength, 0, self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(-self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)

    def drawSkybox(self):
        self.skybox.createSkybox(0.0, 0.0, 0.0, 10.0, 10.0, 8.0)

    def drawUFO(self, x = 0.0, y = 0.0, z = 0.0):
        glPushMatrix()
        self.ufoPositionX = self.ufoPositionZ * math.sin(math.radians(rotateAngle)) + self.ufoPositionX * math.cos(math.radians(rotateAngle))
        self.ufoPositionZ = self.ufoPositionZ * math.cos(math.radians(rotateAngle)) - self.ufoPositionX * math.sin(math.radians(rotateAngle))
        glTranslatef(self.ufoPositionX, 10.0, self.ufoPositionZ)
        glRotatef(self.rotateAngle, 0.0, 1.0, 0.0)
        glCallList(self.ufoDL)
        glPopMatrix()

    def drawStar(self, x = 0.0, y = 0.0, z = 0.0):
        glPushMatrix()
        glTranslatef(self.starPositionX, self.starPositionY, self.starPositionZ)
        glRotatef(self.rotateAngle, 0.0, 1.0, 0.0)
        glCallList(self.starDL)
        glPopMatrix()

#--------------------------------------populating scene----------------
def staticObjects():
    global objectArray, scene
    scene = Scene()
    objectArray.append(scene)
    print("scene appended")

def setupLight(index, position, direction, intensity):
    glPushMatrix()
    glLoadIdentity()
    gluLookAt(0.0, 3.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    glDisable(GL_LIGHTING)

    glColor3f(intensity[0], intensity[1], intensity[2])

    glTranslatef(position[0], position[1], position[2])

    glutSolidSphere(0.25, 36, 24)

    glTranslatef(-position[0], -position[1], -position[2])
    glEnable(GL_LIGHTING)

    glDisable(GL_LIGHTING)
    glLightfv(glLights[index], GL_POSITION, position)
    
    glLightfv(glLights[index], GL_DIFFUSE, intensity);

    if index == 2:
        glLightfv(glLights[index], GL_AMBIENT, intensity);
        glLightfv(glLights[index], GL_DIFFUSE, intensity);
        glLightf(glLights[index], GL_SPOT_CUTOFF, 90.0)
        glLightfv(glLights[index], GL_SPOT_DIRECTION, direction)
        glLightf(glLights[index], GL_SPOT_EXPONENT, 128.0)

    glEnable(GL_LIGHTING)
    glEnable(glLights[index])

    # glMaterialfv(GL_FRONT, GL_AMBIENT, matAmbient)
    # for x in range(1,4):
    #     for z in range(1,4):
    #          matDiffuse = [float(x) * 0.3, float(x) * 0.3, float(x) * 0.3, 1.0] 
    #          matSpecular = [float(z) * 0.3, float(z) * 0.3, float(z) * 0.3, 1.0]  
    #          matShininess = float(z * z) * 10.0
    #          ## Set the material diffuse values for the polygon front faces. 
    #          glMaterialfv(GL_FRONT, GL_DIFFUSE, matDiffuse)

    #          ## Set the material specular values for the polygon front faces. 
    #          glMaterialfv(GL_FRONT, GL_SPECULAR, matSpecular)

    #          ## Set the material shininess value for the polygon front faces. 
    #          glMaterialfv(GL_FRONT, GL_SHININESS, matShininess)

    #          ## Draw a glut solid sphere with inputs radius, slices, and stacks
    #          glutSolidSphere(0.25, 72, 64)
    #          glTranslatef(1.0, 0.0, 0.0)

    #     glTranslatef(-3.0, 0.0, 1.0)
    glPopMatrix()

def display():
    global jeepObj, canStart, score, beginTime, countTime
    glClearColor(0.4, 0.6, 0.9, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if (applyLighting == True):
        if lightIndex == 0:
            setupLight(lightIndex, light0_Position, light2_Direction, light0_Intensity)
        elif lightIndex == 1:
            setupLight(lightIndex, light1_Position, light2_Direction, light1_Intensity)
        elif lightIndex == 2:
            setupLight(lightIndex, light2_Position, light2_Direction, light2_Diffuse)
   
    beginTime = 6 - score
    countTime = score - 6
    if (score <= 5):
        canStart = False
        glColor3f(1.0,0.0,1.0)
        text3d("Begins in: " + str(beginTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    elif (score == 6):
        canStart = True
        glColor(1.0,0.0,1.0)
        text3d("GO!", jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    else:
        canStart = True
        glColor3f(0.0,1.0,1.0)
        text3d("Scoring: "+ str(countTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)

    for obj in objectArray:
        obj.draw()
    for cone in allcones:
        cone.draw()
    for star in allstars:
        star.draw()
    # if (usedDiamond == False):
    #     diamondObj.draw()
    drawStar(0.0, 8.0, 0.0)

    jeepObj.draw()
    jeepObj.drawW1()
    jeepObj.drawW2()
    #jeepObj.drawLight()

    #personObj.draw()
    glutSwapBuffers()

def idle():#--------------with more complex display items like turning wheel---
    global tickTime, prevTime, score, frameTime, accumulatedTime, rotateAngle, starRotateAngle
    jeepObj.rotateWheel(-0.1 * tickTime)    
    glutPostRedisplay()
    x = light0_Position[0]
    z = light0_Position[2]

    x = z * math.sin(math.radians(rotateAngle)) + x * math.cos(math.radians(rotateAngle))
    z = z * math.cos(math.radians(rotateAngle)) - x * math.sin(math.radians(rotateAngle))

    rotateAngle = frameTime * 15.0

    light0_Position[0] = x
    light0_Position[2] = z

    x = light1_Position[0]
    z = light1_Position[2]

    x = z * math.sin(math.radians(rotateAngle)) + x * math.cos(math.radians(rotateAngle))
    z = z * math.cos(math.radians(rotateAngle)) - x * math.sin(math.radians(rotateAngle))

    light1_Position[0] = x
    light1_Position[2] = z

    # light2_Position[2] += 0.01

    curTime = glutGet(GLUT_ELAPSED_TIME)
    tickTime =  curTime - prevTime
    frameTime = tickTime / 1000.0;
    accumulatedTime += frameTime
    prevTime = curTime
    score = curTime/1000
    scene.update(frameTime)

#---------------------------------setting camera----------------------------
def setView():
    global eyeX, eyeY, eyeZ
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, aspect, nearZ, farZ)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if (topView == True):
        gluLookAt(0, 10, land * gameEnlarge / 2, 0, jeepObj.posY, land * gameEnlarge / 2, 0, 1, 0)
    elif (behindView ==True):
        gluLookAt(jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ - 10.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1, 0) 
    else:
        gluLookAt(eyeX, eyeY, eyeZ, 0, 0, 0, 0, 1, 0)
    
    glutPostRedisplay()    

def setObjView():
    # things to do
    # realize a view following the jeep
    # refer to setview
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, aspect, nearZ, farZ)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if (topView == True):
        gluLookAt(0, 10, land * gameEnlarge / 2, 0, jeepObj.posY, land * gameEnlarge / 2, 0, 1, 0)
    elif (behindView ==True):
        gluLookAt(jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ - 10.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0, 1, 0) 
    
    glutPostRedisplay()   

#-------------------------------------------user inputs------------------
def mouseHandle(button, state, x, y):
    global midDown
    if (button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN):
        midDown = True
        print("getting pushed")
    else:
        midDown = False    
        
def motionHandle(x,y):
    global nowX, nowY, angle, eyeX, eyeY, eyeZ, phi
    if (midDown == True):
        pastX = nowX
        pastY = nowY 
        nowX = x
        nowY = y
        if (nowX - pastX > 0):
            angle -= 0.25
        elif (nowX - pastX < 0):
            angle += 0.25
        #elif (nowY - pastY > 0): look into looking over and under object...
            #phi += 1.0
        #elif (nowX - pastY <0):
            #phi -= 1.0
        eyeX = radius * math.sin(angle) 
        eyeZ = radius * math.cos(angle)
        #eyeY = radius * math.sin(phi)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()
    #print eyeX, eyeY, eyeZ, nowX, nowY, radius, angle
    #print "getting handled"

def mouseWheel(button, dir, x, y):
    global eyeX, eyeY, eyeZ, radius
    if (dir > 0): #zoom in
        radius -= 1
        #setView()
        print("zoom in!")
    elif (dir < 0): #zoom out
        radius += 1
        #setView()
        print("zoom out!")
    eyeX = radius * math.sin(angle)
    eyeZ = radius * math.cos(angle)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()


def specialKeys(keypress, mX, mY):
    # things to do
    # this is the function to move the car
    if keypress == GLUT_KEY_UP:
        jeepObj.posZ += moveSpeed * frameTime
    elif keypress == GLUT_KEY_DOWN:
        jeepObj.posZ -= moveSpeed * frameTime
    elif keypress == GLUT_KEY_LEFT:
        jeepObj.posX += moveSpeed * frameTime
    elif keypress == GLUT_KEY_RIGHT:
        jeepObj.posX -= moveSpeed * frameTime

    s = 1 / 2 * a * math.pow(accumulatedTime, 2)

    jeepObj.posZ += s

    setObjView()

def CreateMenu():
    menu = glutCreateMenu(processMenuEvents)  
    glutAddMenuEntry("One", 1)  
    glutAddMenuEntry("Two", 2)  
    glutAttachMenu(GLUT_RIGHT_BUTTON)
    # Add the following line to fix your code
    return 0

def processMenuEvents(option):
    print(option)

def changeWindowSize(width, height):
    global lastWindowWidth
    global lastWindowHeight
    global windowWidth
    global windowHeight
    lastWindowWidth = windowWidth
    lastWindowHeight = windowHeight
    windowWidth = width
    windowHeight = height
    glutReshapeWindow(windowWidth, windowHeight)

class Menu:
 def selectMenu(self, choice):
    # def _exit():
    #     import sys
    #     sys.exit(0)
    # {
    #     1: _exit
    # }[choice]()
    global applyLighting
    global lightIndex
    global windowWidth
    global windowHeight
    global isFullScreen
    if choice == 1:
        if applyLighting == True:
            applyLighting = bool(1 - applyLighting)
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
            glDisable(GL_LIGHT1)
        elif applyLighting == False:
            applyLighting = bool(1 - applyLighting)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_LIGHT1)
    elif choice == 2:
        lightIndex = 0
    elif choice == 3:
        lightIndex = 1
    elif choice == 4:
        lightIndex = 2
    elif choice == 5:
        changeWindowSize(800, 600)
    elif choice == 6:
        changeWindowSize(1280, 720)
    elif choice == 7:
        if isFullScreen == False:
            glutFullScreen()
            isFullScreen = bool(1 - isFullScreen)
        elif isFullScreen == True:
            windowWidth = lastWindowWidth
            windowHeight = lastWindowHeight
            glutReshapeWindow(windowWidth, windowHeight)
            isFullScreen = bool(1 - isFullScreen)
    return 0

 def createMenu(self):
    # --- Right-click Menu --------
    from ctypes import c_int
    import platform
    #platform specific imports:
    if (platform.system() == 'Windows'):
        #Windows
        from ctypes import WINFUNCTYPE
        CMPFUNCRAW = WINFUNCTYPE(c_int, c_int)
        # first is return type, then arg types.
    else:
        #Linux
        from ctypes import CFUNCTYPE
        CMPFUNCRAW = CFUNCTYPE(c_int, c_int)
        # first is return type, then arg types.

    myfunc = CMPFUNCRAW(self.selectMenu)

    selection_menu = glutCreateMenu( myfunc )
    glutAddMenuEntry("Toggle Lighting", 1);
    glutAddMenuEntry("Light0", 2)
    glutAddMenuEntry("Light1", 3) 
    glutAddMenuEntry("Light2", 4)
    glutAddMenuEntry("800x600", 5)
    glutAddMenuEntry("1280x720", 6)
    glutAddMenuEntry("Toggle FullScreen", 7)
    glutAttachMenu(GLUT_RIGHT_BUTTON);
    # -

def myKeyboard(key, mX, mY):
    global eyeX, eyeY, eyeZ, angle, radius, helpWindow, centered
    global helpWin, overReason, topView, behindView, GKeyPressed, starScale
    global windowWidth, windowHeight, fogFileter, fogMode, starRotateAngle
    if key == "h":
        print("h pushed ") + str(helpWindow)
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500,300)
            glutInitWindowPosition(600,0)
            helpWin = glutCreateWindow('Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(myKeyboard)
            glutMainLoop()
        elif helpWindow == True and winNum!=1:
            helpWindow = False
            print(glutGetWindow())
            glutHideWindow()
            glutMainLoop()

    if key == "r":
        print(eyeX, eyeY, eyeZ, angle, radius)
        eyeX = 0.0
        eyeY = 2.0
        eyeZ = 10.0
        angle = 0.0
        radius = 10.0
        if centered == False:
            setView()
        elif centered == True:
            setObjView()
    elif key == "h":
        print("h pushed ") + str(helpWindow)
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500,300)
            glutInitWindowPosition(600,0)
            helpWin = glutCreateWindow('Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(stdKey)
            glutMainLoop()
        elif helpWindow == True and winNum!=1:
            helpWindow = False
            print(glutGetWindow())
            glutHideWindow()
            #glutDestroyWindow(helpWin)
            glutMainLoop()
    elif key == "l":
        print("light triggered!")
        if jeepObj.lightOn == True:
            jeepObj.lightOn = False
        elif jeepObj.lightOn == False:
            jeepObj.lightOn = True
        glutPostRedisplay()
    elif key == "c":
        if centered == True:
            centered = False
            print("non-centered view")
        elif centered == False:
            centered = True
            print("centered view")
    elif key == "t":#top view, like a map ####################!!!!!!
        if (topView == True):
            topView = False
        elif (topView == False):
            topView = True
        if centered == False:
            setView()
        elif centered == True:
            setObjView()
    elif key == "b": #behind the wheel
        if (behindView == True):
            behindView = False
        elif (behindView == False):
            behindView = True
        setView()
    elif key == "q" and canStart == True:
        overReason = "You decided to quit!"
        gameOver()

    elif key == "x":
        windowWidth = 1280
        windowHeight = 720
        glutReshapeWindow(1280, 720)
        glutPostRedisplay()

    elif key == "f":
        fogFileter = (fogFileter + 1) % 3
        glFogi(GL_FOG_MODE, fogMode[fogFileter])

    if behindView == True:
        if key == "w":
            jeepObj.posZ += moveSpeed * frameTime
            setObjView()
        elif key == "s":
            jeepObj.posZ -= moveSpeed * frameTime
            setObjView()
        elif key == "a":
            jeepObj.posX += moveSpeed * frameTime
            setObjView()
        elif key == "d":
            jeepObj.posX -= moveSpeed * frameTime
            setObjView()

    if key == "1":
        starRotateAngle += frameTime * 100.0;
    elif key == "2":
        starRotateAngle -= frameTime * 100.0
    elif key == "3":
        starScale += 0.1
    elif key == "4":
        starScale -= 0.1

    s = 1 / 2 * a * math.pow(accumulatedTime, 2)

    jeepObj.posZ += s

#-------------------------------------------------tools----------------------       
def drawTextBitmap(string, x, y): #for writing text to display
    glRasterPos2f(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def text3d(string, x, y, z):
    glRasterPos3f(x,y,z)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def drawStar(x = 0.0, y = 0.0, z = 0.0):
    global starDL, starScale
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(starRotateAngle, 0.0, 1.0, 0.0)
    glScalef(starScale, starScale, starScale)
    glCallList(starDL)
    glPopMatrix()

def dist(pt1, pt2):
    a = pt1[0]
    b = pt1[1]
    x = pt2[0]
    y = pt2[1]
    return math.sqrt((a-x)**2 + (b-y)**2)

def noReshape(newX, newY): #used to ensure program works correctly when resized
    global windowWidth, windowHeight, aspect
    windowWidth = newX
    windowHeight = newY
    aspect = 1.0 * windowWidth / windowHeight;

    setView()
    
    # 设置视口大小为增个窗口大小
    glViewport(0, 0, windowWidth, windowHeight)

#--------------------------------------------making game more complex--------
def addCone(x,z):
    allcones.append(cone.cone(x,z))
    obstacleCoord.append((x,z))

def collisionCheck():
    global overReason, score, usedDiamond, countTime
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()
    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()
    for reward in rewardCoord:
        if dist((jeepObj.posX, jeepObj.posZ), reward) <= ckSense:
            print("Star bonus!")
            allstars.pop(rewardCoord.index(reward))
            rewardCoord.remove(reward)
            countTime -= 10
    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond ==False):
        print("Diamond bonus!")
        countTime /= 2
        usedDiamond = True
    if (jeepObj.posZ >= land*gameEnlarge):
        gameSuccess()
        
#----------------------------------multiplayer dev (using tracker)-----------
def recordGame():
    with open('results.csv', 'wt') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)
        spamwriter.writerow([st] + [finalScore])
    
#-------------------------------------developing additional windows/options----
def gameOver():
    global finalScore
    print("Game completed!")
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Game Over!")
    glutDisplayFunc(overScreen)
    glutMainLoop()
    
def gameSuccess():
    global finalScore
    print("Game success!")
    finalScore = score-6
    #recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200,200)
    glutInitWindowPosition(600,100)
    overWin = glutCreateWindow("Complete!")
    glutDisplayFunc(winScreen)
    glutMainLoop()

def winScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Completed Trial!" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score is: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()


def overScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,1.0)
    drawTextBitmap("Incomplete Trial" , -0.6, 0.85)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Because you..." , -1.0, 0.5)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(overReason, -1.0, 0.35)
    glColor3f(0.0,1.0,0.0)
    drawTextBitmap("Your score stopped at: ", -1.0, 0.0)
    glColor3f(1.0,1.0,1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()

def showHelp():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,0.0)
    drawTextBitmap("Help Guide" , -0.2, 0.85)
    glColor3f(0.0,0.0,1.0)
    drawTextBitmap("describe your control strategy." , -1.0, 0.7)
    glutSwapBuffers()

def loadSceneTextures():
    global roadTextureID
    roadTextureID = utils.loadTexture("../img/road2.png")
    # roadTextureID = utils.loadTexture("../img/sunset_posX.bmp")
    
#-----------------------------------------------lighting work--------------
def initializeLight():
    glEnable(GL_LIGHTING)                
    glEnable(GL_LIGHT0)                 
    glEnable(GL_DEPTH_TEST)              
    glClearDepth(1.0);
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_NORMALIZE)               

#~~~~~~~~~~~~~~~~~~~~~~~~~the finale!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def initFog():
    glFogi(GL_FOG_MODE, fogMode[fogFileter])
    glFogfv(GL_FOG_COLOR, fogColor)
    glFogf(GL_FOG_DENSITY, 0.35)
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogf(GL_FOG_START, 1.0)
    glFogf(GL_FOG_END, 5.0)
    glEnable(GL_FOG)

def main():
    glutInit()
    global prevTime, mainWin, displayList, star, starDL
    prevTime = glutGet(GLUT_ELAPSED_TIME)
    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    # things to do
    # change the window resolution in the game
    glutInitWindowSize(windowWidth, windowHeight)
    
    glutInitWindowPosition(0, 0)
    mainWin = glutCreateWindow('CS4182')
    glutDisplayFunc(display)
    glutIdleFunc(idle)#wheel turn

    glEnable(GL_DEPTH_TEST)   

    glutMouseFunc(mouseHandle)
    glutMotionFunc(motionHandle)
    glutMouseWheelFunc(mouseWheel)
    glutSpecialFunc(specialKeys)
    glutKeyboardFunc(myKeyboard)
    glutReshapeFunc(noReshape)
    # things to do
    # add a menu 

    loadSceneTextures()

    jeep1Obj.makeDisplayLists()
    jeep2Obj.makeDisplayLists()
    jeep3Obj.makeDisplayLists()

    #personObj.makeDisplayLists()

    # things to do
    # add a automatic object
    for i in range(coneAmount):#create cones randomly for obstacles, making sure to give a little lag time in beginning by adding 10.0 buffer
        addCone(random.randint(-land, land), random.randint(10.0, land*gameEnlarge))

    # things to do
    # add stars

    for cone in allcones:
        cone.makeDisplayLists()

    for star in allstars:
        star.makeDisplayLists()

    star = ImportObject.ImportedObject("../objects/starR")

    star.loadOBJ("../img/")

    starDL = glGenLists(1)
    glNewList(starDL, GL_COMPILE)
    star.drawObject()
    glEndList()

    # initFog()
    # CreateMenu()
    menu = Menu()
    menu.createMenu()

    # diamondObj.makeDisplayLists()
    
    staticObjects()
    if (applyLighting == True):
        initializeLight()
    glutMainLoop()

main()

