#!/usr/bin/env python
# -*- coding: utf-8 -*-‘
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, csv, datetime
# import ImportObject
import PIL.Image as Image
# import jeep, cone, utils
# from skybox import *
# ImportObject.py

import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import OpenGL.GLU as GLU
## Avoid conflict with Python open
from PIL.Image import open as imageOpen

import random

from win32ui import IDD_SET_TABSTOPS
from win32ui import IDC_EDIT_TABS
from win32ui import IDC_PROMPT_TABS
from win32con import IDOK
from win32con import IDCANCEL

import win32ui
import win32con

from pywin.mfc import dialog

import six
import appdirs
import packaging

windowWidth = 800
windowHeight = 600
lastWindowWidth = 0
lastWindowHeight = 0
isFullScreen = False
aspect = float(windowWidth) / windowHeight;

class SettingDialog(dialog. Dialog): # 通过继承dialog Dialog生成对话框类
    def __init__(self):
        style = (win32con.DS_MODALFRAME | #定义对话框样式
        win32con.WS_POPUP |
        win32con.WS_VISIBLE |
        win32con.WS_CAPTION |
        win32con.WS_SYSMENU |
        win32con.DS_SETFONT)

        childstyle =(win32con. WS_CHILD | #定义控件样式
        win32con.WS_VISIBLE)

        buttonstyle = win32con.WS_TABSTOP | childstyle

        di = ['Python', (0, 0, 200, 90), style, None,(8, "MS Sans Serif")]

        ButoK =(['Button', #设置OK按钮属性
        "OK",
        win32con.IDOK,
        (50, 50, 50, 14),
        buttonstyle | win32con.BS_PUSHBUTTON])

        ButCancel =(['Button', #设置Cancel按钮属性
        "Cancel",
        win32con.IDCANCEL,
        (110, 50, 50, 14),
        buttonstyle | win32con.BS_PUSHBUTTON])

        Stadic =(['Static', #设置标签属性
        'Resolution:',
        12,
        (10, 30, 60, 14), childstyle])

        Width =(['Edit', #设置文本框属性
        '1280',
        13,
        (50, 30, 50, 14),
        childstyle | win32con.ES_LEFT |
        win32con.WS_BORDER | win32con.WS_TABSTOP])

        Height =(['Edit', #设置文本框属性
        '720',
        14,
        (110, 30, 50, 14),
        childstyle | win32con.ES_LEFT |
        win32con.WS_BORDER | win32con.WS_TABSTOP])

        FullScreen =(['Button', #设置Cancel按钮属性
        "Full Screen",
        15,
        (50, 70, 50, 14),
        buttonstyle | win32con.BS_AUTOCHECKBOX])

        init = [] #初始化信息列表
        init.append(di)
        init.append(ButoK)
        init.append(ButCancel)
        init.append(Stadic)
        init.append(Width)
        init.append(Height)
        init.append(FullScreen)
        dialog.Dialog.__init__(self, init)

    def OnInitDialog(self):  #重载对话框初始化方法
        dialog.Dialog.OnInitDialog(self) #调用父类的对话框初始化方法
        self.width = self.GetDlgItem(13)
        self.height = self.GetDlgItem(14)
        self.checkBox = self.GetDlgItem(15)

    def OnOK(self):  #重载OnOK方法
        global windowWidth, windowHeight, isFullScreen
        windowWidth = int(self.width.GetWindowText())
        windowHeight = int(self.height.GetWindowText())
        isFullScreen = self.checkBox.GetCheck()
        self.EndDialog(1)

    def OnCancel(self):#重载OnCancel方法
        win32ui. MessageBox('Press Cancel', 'Python'. win32con.MB_OK)
        windowWidth = 800
        windowHeight = 600;
        self.EndDialog()

## This class is used to create an object from geometry and materials
##  saved to a file in WaveFront object format.  The object exported
##  from Blender must have the normals included.
class ImportedObject:
    ## Constructor that includes storage for geometry and materials
    ##  for an object.
    def __init__(self, fileName, setAmbient = 0.9, verbose = False):
        self.faces = []
        self.verts = []
        self.norms = []
        self.texCoords = []
        self.materials = []
        self.fileName = fileName
        self.setAmbient = False
        self.hasTex = False
        ## Set this value to False before loading if the model is flat
        self.isSmooth = True
        self.verbose = verbose

    ## Load the material properties from the file
    def loadMat(self):
        ## Open the material file
        with open((self.fileName + ".mtl"), "r") as matFile:
            ## Load the material properties into tempMat
            tempMat = []
            for line in matFile:
                ## Break the line into its components
                vals = line.split()
                ## Make sure there's something in the line (not blank)
                if len(vals) > 0 :
                    ## Record that a new material is being applied
                    if vals[0] == "newmtl":
                        n = vals[1]
                        tempMat.append(n)
                    ## Load the specular exponent
                    elif vals[0] == "Ns":
                        n = vals[1]
                        tempMat.append(float(n))
                    ## Load the diffuse values
                    elif vals[0] == "Kd":
                        n = map(float, vals[1:4])
                        tempMat.append(n)
                        ## if self.setAmbient is False, ignore ambient values
                        ## and load diffuse values twice to set the ambient
                        ## equal to diffuse
                        if self.setAmbient:
                            tempMat.append(n)
                    ## load the ambient values (if not overridden)
                    elif vals[0] == "Ka" and not self.setAmbient:
                        n = map(float, vals[1:4])
                        tempMat.append(n)
                    ## load the specular values
                    elif vals[0] == "Ks":
                        n = map(float, vals[1:4])
                        tempMat.append(n)
                        tempMat.append(None)
                        ## specular is the last line loaded for the material
                        self.materials.append(tempMat)
                        tempMat = []
                    ## load texture file info
                    elif vals[0] == "map_Kd":
                        ## record the texture file name
                        fileName = vals[1]
                        self.materials[-1][5]=(self.loadTexture(fileName))
                        self.hasTex = True

        if self.verbose:
            print("Loaded " + self.fileName + \
                  ".mtl with " + str(len(self.materials)) + " materials")

    ## Load the object geometry.
    def loadOBJ(self):
        ## parse the materials file first so we know when to apply materials
        ## and textures
        self.loadMat()
        numFaces = 0
        with open((self.fileName + ".obj"), "r") as objFile:
            for line in objFile:
                ## Break the line into its components
                vals = line.split()
                if len(vals) > 0:
                    ## Load vertices
                    if vals[0] == "v":
                        v = map(float, vals[1:4])
                        self.verts.append(v)
                    ## Load normals
                    elif vals[0] == "vn":
                        n = map(float, vals[1:4])
                        self.norms.append(n)
                    ## Load texture coordinates
                    elif vals[0] == "vt":
                        t = map(float, vals[1:3])
                        self.texCoords.append(t)
                    ## Load materials. Set index to -1!
                    elif vals[0] == "usemtl":
                        m = vals[1]
                        self.faces.append([-1, m, numFaces])
                    ## Load the faces
                    elif vals[0] == "f":
                        tempFace = []
                        for f in vals[1:]:
                            ## face entries have vertex/tex coord/normal
                            w = f.split("/")
                            ## Vertex required, but should work if texture or
                            ## normal is missing
                            if w[1] != '' and w[2] != '':
                                tempFace.append([int(w[0])-1,
                                                 int(w[1])-1,
                                                 int(w[2])-1])
                            elif w[1] != '':
                                tempFace.append([int(w[0])-1,
                                                 int(w[1])-1], -1)
                            elif w[2] != '':
                                tempFace.append([int(w[0])-1, -1,
                                                 int(w[2])-1])
                            else :
                                tempFace.append([int(w[0])-1,-1, -1])

                        self.faces.append(tempFace)

        if self.verbose:
            print("Loaded " + self.fileName + ".obj with " + \
                  str(len(self.verts)) + " vertices, " + \
                  str(len(self.norms)) + " normals, and " + \
                  str(len(self.faces)) + " faces")


    ## Draws the object
    def drawObject(self):
        if self.hasTex:
            GL.glEnable(GL.GL_TEXTURE_2D)
            ## Use GL.GL_MODULATE instead of GL.GL_DECAL to retain lighting
            GL.glTexEnvf(GL.GL_TEXTURE_ENV,
                         GL.GL_TEXTURE_ENV_MODE,
                         GL.GL_MODULATE)

        ## *****************************************************************
        ## Change GL.GL_FRONT to GL.GL_FRONT_AND_BACK if faces are missing
        ## (or fix the normals in the model so they point in the correct
        ## direction)
        ## *****************************************************************
        GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
        for face in self.faces:
            ## Check if a material
            if face[0] == -1:
                self.setModelColor(face[1])
            else:

                GL.glBegin(GL.GL_POLYGON)
                ## drawing normal, then texture, then vertice coords.
                for f in face:
                    if f[2] != -1:
                        GL.glNormal3f(self.norms[f[2]][0],
                                      self.norms[f[2]][1],
                                      self.norms[f[2]][2])
                    if f[1] != -1:
                        GL.glTexCoord2f(self.texCoords[f[1]][0],
                                        self.texCoords[f[1]][1])
                    GL.glVertex3f(self.verts[f[0]][0],
                                  self.verts[f[0]][1],
                                  self.verts[f[0]][2])
                GL.glEnd()
        ## Turn off texturing (global state variable again)
        GL.glDisable(GL.GL_TEXTURE_2D)

    ## Finds the matching material properties and sets them.
    def setModelColor(self, material):
        mat = []
        for tempMat in self.materials:
            if tempMat[0] == material:
                mat = tempMat
                ## found it, break out.
                break

        ## Set the color for the case when lighting is turned off.  Using
        ##  the diffuse color, since the diffuse component best describes
        ##  the object color.
        GL.glColor3f(mat[3][0], mat[3][1],mat[3][2])
        ## Set the model to smooth or flat depending on the attribute setting
        if self.isSmooth:
            GL.glShadeModel(GL.GL_SMOOTH)
        else:
            GL.glShadeModel(GL.GL_FLAT)
        ## The RGBA values for the specular light intesity.  The alpha value
        ## (1.0) is ignored unless blending is enabled.
        mat_specular = [mat[4][0], mat[4][1], mat[4][2], 1.0]
        ## The RGBA values for the diffuse light intesity.  The alpha value
        ## (1.0) is ignored unless blending is enabled.
        mat_diffuse = [mat[3][0], mat[3][1],mat[3][2], 1.0]
        ## The value for the specular exponent.  The higher the value, the
        ## "tighter" the specular highlight.  Valid values are [0.0, 128.0]
        mat_ambient = [mat[2][0], mat[2][1], mat[2][2],1.0]
        ## The value for the specular exponent.  The higher the value, the
        ## "tighter" the specular highlight.  Valid values are [0.0, 128.0]
        mat_shininess = 0.128 * mat[1]
        ## Set the material specular values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, mat_specular)
        ## Set the material shininess values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, mat_shininess)
        ## Set the material diffuse values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, mat_diffuse)
        ## Set the material ambient values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT, mat_ambient)
        ## See if there is a texture and bind it if it's there
        if mat[5] != None:
            GL.glBindTexture(GL.GL_TEXTURE_2D, mat[5])


    ## Load a texture from the provided image file name
    def loadTexture(self, texFile):
        if self.verbose:
            print("Loading " + texFile)
        ## Open the image file
        texImage = imageOpen(texFile)
        try:
            ix, iy, image = texImage.size[0], \
                            texImage.size[1], \
                            texImage.tobytes("raw", "RGBA", 0, -1)
        except SystemError:
            ix, iy, image = texImage.size[0], \
                            texImage.size[1], \
                            texImage.tobytes("raw", "RGBX", 0, -1)
        ## GL.glGenTextures() and GL.glBindTexture() name and create a texture
        ## object for a texture image
        tempID = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tempID)
        ## The four calls to GL.glTexParameter*() specify how the texture is to
        ## be wrapped and how the colors are to be filtered if there isn't an
        ## exact match between pixels in the texture and pixels on the screen
        ## Values for GL.GL_TEXTURE_WRAP_S and GL.GL_TEXTURE_WRAP_T are
        ## GL.GL_REPEAT and GL.GL_CLAMP
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_WRAP_S,
                           GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_WRAP_T,
                           GL.GL_REPEAT)
        ## The MAG_FILTER has values of GL.GL_NEAREST and GL.GL_LINEAR.  There
        ## are many choices for values for the MIN_FILTER.  GL.GL_NEAREST has
        ## more pixelation, but is the fastest
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_MAG_FILTER,
                           GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_MIN_FILTER,
                           GL.GL_NEAREST)
        ## Store the pixel data
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 3, ix, iy, 0,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image)
        return tempID

## This class is used to create an object from geometry and materials
##  saved to a file in WaveFront object format.  The object exported
##  from Blender must have the normals included.
class ImportedObject:
    ## Constructor that includes storage for geometry and materials
    ##  for an object.
    def __init__(self, fileName, setAmbient = 0.9, verbose = False):
        self.faces = []
        self.verts = []
        self.norms = []
        self.texCoords = []
        self.materials = []
        self.fileName = fileName
        self.setAmbient = False
        self.hasTex = False
        ## Set this value to False before loading if the model is flat
        self.isSmooth = True
        self.verbose = verbose

    ## Load the material properties from the file
    def loadMat(self, texturePath = ""):
        ## Open the material file
        with open((self.fileName + ".mtl"), "r") as matFile:
            ## Load the material properties into tempMat
            tempMat = []
            for line in matFile:
                ## Break the line into its components
                vals = line.split()
                ## Make sure there's something in the line (not blank)
                if len(vals) > 0 :
                    ## Record that a new material is being applied
                    if vals[0] == "newmtl":
                        n = vals[1]
                        tempMat.append(n)
                    ## Load the specular exponent
                    elif vals[0] == "Ns":
                        n = vals[1]
                        tempMat.append(float(n))
                    ## Load the diffuse values
                    elif vals[0] == "Kd":
                        n = map(float, vals[1:4])
                        tempMat.append(n)
                        ## if self.setAmbient is False, ignore ambient values
                        ## and load diffuse values twice to set the ambient
                        ## equal to diffuse
                        if self.setAmbient:
                            tempMat.append(n)
                    ## load the ambient values (if not overridden)
                    elif vals[0] == "Ka" and not self.setAmbient:
                        n = map(float, vals[1:4])
                        tempMat.append(n)
                    ## load the specular values
                    elif vals[0] == "Ks":
                        n = map(float, vals[1:4])
                        tempMat.append(n)
                        tempMat.append(None)
                        ## specular is the last line loaded for the material
                        self.materials.append(tempMat)
                        tempMat = []
                    ## load texture file info
                    elif vals[0] == "map_Kd":
                        ## record the texture file name
                        fileName = vals[1]
                        self.materials[-1][5]=(self.loadTexture(texturePath +fileName))
                        self.hasTex = True

        if self.verbose:
            print("Loaded " + self.fileName + \
                  ".mtl with " + str(len(self.materials)) + " materials")

    ## Load the object geometry.
    def loadOBJ(self, texturePath = ""):
        ## parse the materials file first so we know when to apply materials
        ## and textures
        self.loadMat(texturePath)
        numFaces = 0
        with open((self.fileName + ".obj"), "r") as objFile:
            for line in objFile:
                ## Break the line into its components
                vals = line.split()
                if len(vals) > 0:
                    ## Load vertices
                    if vals[0] == "v":
                        v = map(float, vals[1:4])
                        self.verts.append(v)
                    ## Load normals
                    elif vals[0] == "vn":
                        n = map(float, vals[1:4])
                        self.norms.append(n)
                    ## Load texture coordinates
                    elif vals[0] == "vt":
                        t = map(float, vals[1:3])
                        self.texCoords.append(t)
                    ## Load materials. Set index to -1!
                    elif vals[0] == "usemtl":
                        m = vals[1]
                        self.faces.append([-1, m, numFaces])
                    ## Load the faces
                    elif vals[0] == "f":
                        tempFace = []
                        for f in vals[1:]:
                            ## face entries have vertex/tex coord/normal
                            w = f.split("/")
                            ## Vertex required, but should work if texture or
                            ## normal is missing
                            if w[1] != '' and w[2] != '':
                                tempFace.append([int(w[0])-1,
                                                 int(w[1])-1,
                                                 int(w[2])-1])
                            elif w[1] != '':
                                tempFace.append([int(w[0])-1,
                                                 int(w[1])-1], -1)
                            elif w[2] != '':
                                tempFace.append([int(w[0])-1, -1,
                                                 int(w[2])-1])
                            else :
                                tempFace.append([int(w[0])-1,-1, -1])

                        self.faces.append(tempFace)

        if self.verbose:
            print("Loaded " + self.fileName + ".obj with " + \
                  str(len(self.verts)) + " vertices, " + \
                  str(len(self.norms)) + " normals, and " + \
                  str(len(self.faces)) + " faces")


    ## Draws the object
    def drawObject(self):
        if self.hasTex:
            GL.glEnable(GL.GL_TEXTURE_2D)
            ## Use GL.GL_MODULATE instead of GL.GL_DECAL to retain lighting
            GL.glTexEnvf(GL.GL_TEXTURE_ENV,
                         GL.GL_TEXTURE_ENV_MODE,
                         GL.GL_MODULATE)

        ## *****************************************************************
        ## Change GL.GL_FRONT to GL.GL_FRONT_AND_BACK if faces are missing
        ## (or fix the normals in the model so they point in the correct
        ## direction)
        ## *****************************************************************
        GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)

        normsKeyValues = {}
        texCoordsKeyValues = {}
        vertsKeyValues = {}

        for face in self.faces:

            ## Check if a material
            if face[0] == -1:
                self.setModelColor(face[1])
            else:

                GL.glBegin(GL.GL_POLYGON)
                ## drawing normal, then texture, then vertice coords.
                for f in face:
                    #    print("f:" + str(f))
                    #    print("self.norms[f[2]]:" + str(self.norms[f[2]]))
                    #    print("f[2]:" + str(f[2]))
                    fList = list(map(int, f))
                    if f[2] != -1:

                        normsf2List = None

                        if len(normsKeyValues) > 0:
                            if f[2] in normsKeyValues:
                                normsf2List = normsKeyValues[f[2]]

                        if normsf2List == None:
                            normsKeyValues[f[2]] = list(map(float, self.norms[f[2]]))
                            normsf2List = normsKeyValues[f[2]]

                        GL.glNormal3f(normsf2List[0],
                                      normsf2List[1],
                                      normsf2List[2])
                    if f[1] != -1:
                        texCoordsf1List = None

                        if len(texCoordsKeyValues) > 0:
                            if f[1] in texCoordsKeyValues:
                                texCoordsf1List = texCoordsKeyValues[f[1]]

                        if texCoordsf1List == None:
                            texCoordsKeyValues[f[1]] = list(map(float, self.texCoords[f[1]]))
                            texCoordsf1List = texCoordsKeyValues[f[1]]

                        GL.glTexCoord2f(texCoordsf1List[0],
                                        texCoordsf1List[1])
                    vertsf0List = None

                    if len(vertsKeyValues) > 0:
                        if f[0] in vertsKeyValues:
                            vertsf0List = vertsKeyValues[f[0]]

                    if vertsf0List == None:
                        vertsf0List = list(map(float, self.verts[f[0]]))
                        vertsKeyValues[f[0]] = vertsf0List

                    GL.glVertex3f(vertsf0List[0],
                                  vertsf0List[1],
                                  vertsf0List[2])
                GL.glEnd()
        ## Turn off texturing (global state variable again)
        GL.glDisable(GL.GL_TEXTURE_2D)

    ## Finds the matching material properties and sets them.
    def setModelColor(self, material):
        mat = []
        for tempMat in self.materials:
            if tempMat[0] == material:
                mat = tempMat
                ## found it, break out.
                break
        # print(mat[3])
        mat3List = list(map(float, mat[3]))
        # print(mat3List)
        ## Set the color for the case when lighting is turned off.  Using
        ##  the diffuse color, since the diffuse component best describes
        ##  the object color.
        GL.glColor3f(mat3List[0], mat3List[1], mat3List[2])
        ## Set the model to smooth or flat depending on the attribute setting
        if self.isSmooth:
            GL.glShadeModel(GL.GL_SMOOTH)
        else:
            GL.glShadeModel(GL.GL_FLAT)

        mat2List = list(map(float, mat[2]))
        mat4List = list(map(float, mat[4]))
        ## The RGBA values for the specular light intesity.  The alpha value
        ## (1.0) is ignored unless blending is enabled.
        mat_specular = [mat4List[0], mat4List[1], mat4List[2], 1.0]
        ## The RGBA values for the diffuse light intesity.  The alpha value
        ## (1.0) is ignored unless blending is enabled.
        mat_diffuse = [mat3List[0], mat3List[1],mat3List[2], 1.0]
        ## The value for the specular exponent.  The higher the value, the
        ## "tighter" the specular highlight.  Valid values are [0.0, 128.0]
        mat_ambient = [mat2List[0], mat2List[1], mat2List[2],1.0]
        ## The value for the specular exponent.  The higher the value, the
        ## "tighter" the specular highlight.  Valid values are [0.0, 128.0]
        mat_shininess = 0.128 * mat[1]
        ## Set the material specular values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, mat_specular)
        ## Set the material shininess values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, mat_shininess)
        ## Set the material diffuse values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_DIFFUSE, mat_diffuse)
        ## Set the material ambient values for the polygon front faces.
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT, mat_ambient)
        ## See if there is a texture and bind it if it's there
        if mat[5] != None:
            GL.glBindTexture(GL.GL_TEXTURE_2D, mat[5])


    ## Load a texture from the provided image file name
    def loadTexture(self, texFile):
        if self.verbose:
            print("Loading " + texFile)
        ## Open the image file
        texImage = imageOpen(texFile)
        try:
            ix, iy, image = texImage.size[0], \
                            texImage.size[1], \
                            texImage.tobytes("raw", "RGBX", 0, -1)
        except SystemError:
            ix, iy, image = texImage.size[0], \
                            texImage.size[1], \
                            texImage.tobytes("raw", "RGBA", 0, -1)
        ## GL.glGenTextures() and GL.glBindTexture() name and create a texture
        ## object for a texture image
        tempID = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tempID)
        ## The four calls to GL.glTexParameter*() specify how the texture is to
        ## be wrapped and how the colors are to be filtered if there isn't an
        ## exact match between pixels in the texture and pixels on the screen
        ## Values for GL.GL_TEXTURE_WRAP_S and GL.GL_TEXTURE_WRAP_T are
        ## GL.GL_REPEAT and GL.GL_CLAMP
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_WRAP_S,
                           GL.GL_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_WRAP_T,
                           GL.GL_REPEAT)
        ## The MAG_FILTER has values of GL.GL_NEAREST and GL.GL_LINEAR.  There
        ## are many choices for values for the MIN_FILTER.  GL.GL_NEAREST has
        ## more pixelation, but is the fastest
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_MAG_FILTER,
                           GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D,
                           GL.GL_TEXTURE_MIN_FILTER,
                           GL.GL_NEAREST)
        ## Store the pixel data
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 3, ix, iy, 0,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image)
        return tempID

# utils.py
#----------------------------------------------texture development-----------
def loadTexture(imageName):
    texturedImage = Image.open(imageName)
    try:
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGBX",0,-1)#tostring("raw", "RGBX", 0, -1)
    except Exception as e:
        print("Error:", e)
        print("Switching to RGBA mode.")
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw","RGB",0,-1)#tostring("raw", "RGBA", 0, -1)

    textureID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
    return textureID

# Skybox.py
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
            textureID = loadTexture("../img/" + textureNames[i])
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

# jeep.py

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time
import ImportObject


class jeep:
    obj = 0
    displayList = 0
    wheel1DL = 0
    wheel2DL = 0
    dimDL = 0
    litDL = 0

    dimL = 0
    litL = 0
    lightOn = False

    wheel1 = 0
    wheel2 = 0

    wheelTurn = 0.0
    revWheelTurn = 360.0
    #allWheels=[wheel1,wheel2]

    wheelDir = 'stop'

    posX = 0.0
    posY = 1.75
    posZ = 0.0

    ##    wheel1LocX =0
    ##    wheel1LocZ = 0
    ##    wheel2LocX = 0
    ##    wheel2LocZ = 0

    sizeX = 1.0
    sizeY = 1.0
    sizeZ = 1.0

    rotation = 0.0

    def __init__(self, color):
        if (color == 'p'):
            self.obj = ImportedObject("../objects/jeepbare")
        elif (color == 'g'):
            self.obj = ImportedObject("../objects/jeepbare2")
        elif (color == 'r'):
            self.obj = ImportedObject("../objects/jeepbare3")
        self.wheel1 = ImportedObject("../objects/frontwheel")
        self.wheel2 = ImportedObject("../objects/backwheel")
        self.dimL = ImportedObject("../objects/dimlight")
        self.litL = ImportedObject("../objects/litlight")

    def makeDisplayLists(self):
        self.obj.loadOBJ()
        self.wheel1.loadOBJ()
        self.wheel2.loadOBJ()
        self.dimL.loadOBJ()
        self.litL.loadOBJ()

        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        self.obj.drawObject()
        glEndList()

        self.wheel1DL = glGenLists(1)
        glNewList(self.wheel1DL, GL_COMPILE)
        self.wheel1.drawObject()
        glEndList()

        self.wheel2DL = glGenLists(1)
        glNewList(self.wheel2DL, GL_COMPILE)
        self.wheel2.drawObject()
        glEndList()

        self.dimDL = glGenLists(1)
        glNewList(self.dimDL, GL_COMPILE)
        self.dimL.drawObject()
        glEndList()

        self.litDL = glGenLists(1)
        glNewList(self.litDL, GL_COMPILE)
        self.litL.drawObject()
        glEndList()


    def draw(self):
        glPushMatrix()

        glTranslatef(self.posX,self.posY,self.posZ)
        glRotatef(self.rotation,0.0,1.0,0.0)
        glScalef(self.sizeX,self.sizeY,self.sizeZ)

        glCallList(self.displayList)
        glPopMatrix()

    def drawW1(self):
        glPushMatrix()

        glTranslatef(self.posX, self.posY-1.3146, self.posZ)
        glRotatef(self.rotation,0.0,1.0,0.0)
        glTranslatef(0.0, self.posY-1.3146, 2.9845)
        glScalef(self.sizeX, self.sizeY, self.sizeZ)

        if self.wheelDir == 'fwd':
            glRotatef(self.revWheelTurn,1.0,0.0,0.0)
        elif self.wheelDir == 'back':
            glRotatef(self.wheelTurn,1.0,0.0,0.0)

        glTranslatef(0.0,1.3146,-2.9845)

        glCallList(self.wheel1DL)
        glPopMatrix()

    def drawW2(self):
        glPushMatrix()

        glTranslatef(self.posX, self.posY-1.3146, self.posZ)
        glRotatef(self.rotation,0.0,1.0,0.0)
        glTranslatef(0.0, self.posY-1.3146, -2.9845)
        glScalef(self.sizeX, self.sizeY, self.sizeZ)

        if self.wheelDir == 'fwd':
            glRotatef(self.revWheelTurn,1.0,0.0,0.0)
        elif self.wheelDir == 'back':
            glRotatef(self.wheelTurn,1.0,0.0,0.0)

        glTranslatef(0.0,1.3146,3.3)

        glCallList(self.wheel2DL)
        glPopMatrix()

    def rotateWheel(self, newTheta):
        global wheelTurn
        self.wheelTurn = self.wheelTurn + newTheta
        self.wheelTurn = self.wheelTurn % 360
        self.revWheelTurn = 360 - self.wheelTurn

    def drawLight(self):
        glPushMatrix()

        glTranslatef(self.posX, self.posY, self.posZ)
        glRotatef(self.rotation,0.0,1.0,0.0)
        glScalef(self.sizeX, self.sizeY, self.sizeZ)

        if self.lightOn == True:
            glCallList(self.litDL)
        elif self.lightOn == False:
            glCallList(self.dimDL)

        glPopMatrix()

    def move(self, rot, val):
        if rot == False:
            self.posZ += val * math.cos(math.radians(self.rotation)) #must make more sophisticated to go in direction
            self.posX += val * math.sin(math.radians(self.rotation))
##            self.wheel1LocZ += val * math.cos(math.radians(self.rotation))
##            self.wheel1LocX += val * math.sin(math.radians(self.rotation))
##            self.wheel2LocZ += val * math.cos(math.radians(self.rotation))
##            self.wheel2LocX += val * math.sin(math.radians(self.rotation))
        elif rot == True:
            self.rotation+= val

# cone.py

class cone:
    obj = 0
    displayList = 0

    posX = 0.0
    posY = 0.0
    posZ = 0.0

    sizeX = 1.0
    sizeY = 1.0
    sizeZ = 1.0

    rotation = 0.0

    def __init__(self, x, z):
        self.obj = ImportObject.ImportedObject("../objects/cone")
        self.posX = x
        self.posZ = z

    def makeDisplayLists(self):
        self.obj.loadOBJ()

        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        self.obj.drawObject()
        glEndList()

    def draw(self):
        glPushMatrix()

        glTranslatef(self.posX,self.posY,self.posZ)
        #glRotatef(self.rotation,0.0,1.0,0.0)
        glScalef(self.sizeX,self.sizeY,self.sizeZ)

        glCallList(self.displayList)
        glPopMatrix()

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
jeep1Obj = jeep('p')
jeep2Obj = jeep('g')
jeep3Obj = jeep('r')

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

glLights = [GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3]

light0_Ambient = [1.0, 0.0, 0.0, 1.0]
light0_Diffuse = [0.75, 0.0, 0.0, 0.0]
light0_Position = [-2.0, 2.0, -5.0, 1.0]
light0_Intensity = [0.75, 0.0, 0.0, 0.0]

ambientColors = [[random.random(), random.random(), random.random(), 1.0],
                 [random.random(), random.random(), random.random(), 1.0],
                 [random.random(), random.random(), random.random(), 1.0]]

ambientColors = [[ambientColors[0][j] / 10 for j in range(3)],
                 [ambientColors[1][j] / 10 for j in range(3)],
                 [ambientColors[2][j] / 10 for j in range(3)]]

diffuseColors = [[random.random(), random.random(), random.random(), 1.0],
                 [random.random(), random.random(), random.random(), 1.0],
                 [random.random(), random.random(), random.random(), 1.0]]

lightPositions = [[-2.0, 2.0, -5.0, 1.0], [2.0, 2.0, 5.0, 1.0], [0.0, 2.0, 1.0, 1.0]]

ambientColorIndex = 0
diffuseColorIndex = 0
lightPositionIndex = 0

light1_Ambient = [0.0, 1.0, 0.0, 1.0]
light1_Position = [2.0, 2.0, 5.0, 1.0]
light1_Diffuse = [0.5, 0.5, 0.0, 1.0]

light2_Position = [0.0, 2.0, 1.0, 1.0]
light2_Direction = [0.0, -1.0, 0.0, 0.0]
light2_Ambient = [1.0, 0.0, 1.0, 1.0]
light2_Diffuse = [1.0, 0.0, 1.0, 1.0]

light3_Ambient = [0.0, 1.0, 1.0, 1.0]
light3_Diffuse = [0.0, 1.0, 1.0, 1.0]

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

def setupLight(index, position, direction, ambient, diffuse):
    glPushMatrix()
    glLoadIdentity()
    gluLookAt(0.0, 3.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    glDisable(GL_LIGHTING)

    glColor3f(ambient[0] * 10.0, ambient[1] * 10.0, ambient[2] * 10.0)

    if position != None:
        glTranslatef(position[0], position[1], position[2])

    glutSolidSphere(0.25, 36, 24)

    if position != None:
        glTranslatef(-position[0], -position[1], -position[2])
    glEnable(GL_LIGHTING)

    if position != None:
        glLightfv(glLights[index], GL_POSITION, position)

    glLightfv(glLights[index], GL_AMBIENT, ambient);
    glLightfv(glLights[index], GL_DIFFUSE, diffuse);

    if direction != None:
        glLightf(glLights[index], GL_SPOT_CUTOFF, 90.0)
        glLightfv(glLights[index], GL_SPOT_DIRECTION, direction)
        glLightf(glLights[index], GL_SPOT_EXPONENT, 128.0)

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
            setupLight(lightIndex, lightPositions[lightPositionIndex], None, ambientColors[ambientColorIndex], diffuseColors[diffuseColorIndex])
        elif lightIndex == 1:
            setupLight(lightIndex, lightPositions[lightPositionIndex], None, ambientColors[ambientColorIndex], diffuseColors[diffuseColorIndex])
        elif lightIndex == 2:
            setupLight(lightIndex, lightPositions[lightPositionIndex], light2_Direction, ambientColors[ambientColorIndex], diffuseColors[diffuseColorIndex])
        elif lightIndex == 3:
            setupLight(lightIndex, None, None, ambientColors[ambientColorIndex], diffuseColors[diffuseColorIndex])

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
    jeepObj.drawLight()

    #personObj.draw()
    glutSwapBuffers()

def idle():#--------------with more complex display items like turning wheel---
    global tickTime, prevTime, score, frameTime, accumulatedTime, rotateAngle, starRotateAngle
    global lightPositionIndex, lightPositions
    jeepObj.rotateWheel(-0.1 * tickTime)
    glutPostRedisplay()
    x = lightPositions[lightPositionIndex][0]
    z = lightPositions[lightPositionIndex][2]

    x = z * math.sin(math.radians(rotateAngle)) + x * math.cos(math.radians(rotateAngle))
    z = z * math.cos(math.radians(rotateAngle)) - x * math.sin(math.radians(rotateAngle))

    rotateAngle = frameTime * 15.0

    lightPositions[lightPositionIndex][0] = x
    lightPositions[lightPositionIndex][2] = z

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
                glDisable(GL_LIGHT2)
                glDisable(GL_LIGHT3)
            elif applyLighting == False:
                applyLighting = bool(1 - applyLighting)
                glEnable(GL_LIGHTING)
                glEnable(GL_LIGHT0)
                glEnable(GL_LIGHT1)
                glEnable(GL_LIGHT2)
                glEnable(GL_LIGHT3)
        elif choice == 2:
            lightIndex = 0
        elif choice == 3:
            lightIndex = 1
        elif choice == 4:
            lightIndex = 2
        elif choice == 5:
            lightIndex = 3
        elif choice == 6:
            changeWindowSize(800, 600)
        elif choice == 7:
            changeWindowSize(1280, 720)
        elif choice == 8:
            if isFullScreen == False:
                glutFullScreen()
                isFullScreen = bool(1 - isFullScreen)
            elif isFullScreen == True:
                windowWidth = lastWindowWidth
                windowHeight = lastWindowHeight
                glutReshapeWindow(windowWidth, windowHeight)
                isFullScreen = bool(1 - isFullScreen)
        return 0

    def test(self):
        pass

    def ambientColorMenu(self, choice):
        global ambientColorIndex
        ambientColorIndex = choice
        return 0

    def diffuseColorMenu(self, choice):
        global diffuseColorIndex
        diffuseColorIndex = choice
        return 0

    def lightPositionMenu(self, choice):
        global lightPositionIndex
        lightPositionIndex = choice
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

        callback = CMPFUNCRAW(self.selectMenu)
        testCallback = CMPFUNCRAW(self.test)

        ambientColorMenuCallback = CMPFUNCRAW(self.ambientColorMenu)
        diffuseColorMenuCallback = CMPFUNCRAW(self.diffuseColorMenu)
        lightPositionMenuCallback = CMPFUNCRAW(self.lightPositionMenu)

        ambientColorSubMenu = glutCreateMenu(ambientColorMenuCallback)
        glutAddMenuEntry("Ambient Color 1", 0)
        glutAddMenuEntry("Ambient Color 2", 1)
        glutAddMenuEntry("Ambient Color 3", 2)

        diffuseColorSubMenu = glutCreateMenu(diffuseColorMenuCallback)
        glutAddMenuEntry("Diffuse Color 1", 0)
        glutAddMenuEntry("Diffuse Color 2", 1)
        glutAddMenuEntry("Diffuse Color 3", 2)

        lightColorSubMenu = glutCreateMenu(lightPositionMenuCallback)
        glutAddMenuEntry("Light Position 1", 0)
        glutAddMenuEntry("Light Position 2", 1)
        glutAddMenuEntry("Light Position 3", 2)

        ambientColorMenu = glutCreateMenu(testCallback)
        glutAddSubMenu("Ambient Color", ambientColorSubMenu)
        glutAddSubMenu("Diffuse Color", diffuseColorSubMenu)
        glutAddSubMenu("Light Positions", lightColorSubMenu)

        lightingMenu = glutCreateMenu( callback )
        glutAddMenuEntry("Toggle Lighting", 1);
        # glutAddMenuEntry("Light0", 2)
        glutAddMenuEntry("Point Light", 3)
        glutAddMenuEntry("Spot Light", 4)
        glutAddMenuEntry("Directional Light", 5)
        glutAddSubMenu("Light Properties", ambientColorMenu)

        # glutAddMenuEntry("800x600", 6)
        # glutAddMenuEntry("1280x720", 7)
        # glutAddMenuEntry("Toggle FullScreen", 8)
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
        createSettingDialog()

        if isFullScreen == True:
            glutFullScreen();
        glutReshapeWindow(windowWidth, windowHeight)
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
    allcones.append(cone(x,z))
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
    drawTextBitmap(" 1.Use W/S/A/D to move the car, the camera will follow." , -1.0, 0.7)
    drawTextBitmap(" 2.Press 'B' will switch to orbit camera mode." , -1.0, 0.5)
    drawTextBitmap(" 3.Press the middle mouse button and move can fly around the car.", -1.0, 0.3)
    drawTextBitmap("    (1).Mouse wheel used to change fov(zoom in / out)." , -1.0, 0.1)
    drawTextBitmap("    (2).Number keys 1, 2 used to rotate the star." , -1.0, -0.1)
    drawTextBitmap(" 4.Number keys 3, 4 used to scale the star." , -1.0, -0.3)
    drawTextBitmap(" 5.Right click in the viewport to fire up light setting memnu." , -1.0, -0.5)
    drawTextBitmap(" 6.Press \"X\" fire up resolution setting window." , -1.0, -0.7)
    glutSwapBuffers()

def loadSceneTextures():
    global roadTextureID
    roadTextureID = loadTexture("../img/road2.png")
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

def createSettingDialog():
    settingDialog = SettingDialog() #生成对话框实例对象
    settingDialog. DoModal()    #创建对话框

def main():
    glutInit()
    global prevTime, mainWin, displayList, star, starDL
    global lastWindowWidth, lastWindowHeight
    prevTime = glutGet(GLUT_ELAPSED_TIME)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)

    createSettingDialog()

    # things to do
    # change the window resolution in the game
    glutInitWindowSize(windowWidth, windowHeight)
    lastWindowWidth = windowWidth
    lastWindowHeight = windowHeight;
    screenWidth = glutGet(GLUT_SCREEN_WIDTH)
    screenHeight = glutGet(GLUT_SCREEN_HEIGHT)
    glutInitWindowPosition((screenWidth - windowWidth) / 2, (screenHeight - windowHeight) / 2)
    mainWin = glutCreateWindow('CS4182')
    if isFullScreen == True:
        glutFullScreen()
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
