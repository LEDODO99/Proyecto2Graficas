import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy
import pyrr
from PIL import Image
from objloader import *
import math
from time import sleep

def window_resize(window, width, height):
    glViewport(0, 0, width, height)
def get_camera_x_z(angle,dist):
    if ((angle % 360)==0):
        angle=0
    elif (((angle+90) % 360)==0):
        angle=270
    elif (((angle+180) % 360)==0):
        angle=180
    elif (((angle+270) % 360)==0):
        angle=90
        
    if (angle==0):
        z=dist
        x=0
    elif(angle==90):
        z=0
        x=dist
    elif (angle==180):
        z=-dist
        x=0
    elif(angle==270):
        z=0
        x=-dist
    else:
        z=math.cos((angle/180)*math.pi)*dist
        x=math.sin((angle/180)*math.pi)*dist
    return [z,x]
print(get_camera_x_z(0,5))
print(get_camera_x_z(10,5))
print(get_camera_x_z(20,5))
print(get_camera_x_z(30,5))
print(get_camera_x_z(40,5))
print(get_camera_x_z(50,5))
print(get_camera_x_z(60,5))
print(get_camera_x_z(70,5))
print(get_camera_x_z(80,5))
print(get_camera_x_z(90,5))
def main():

    # initialize glfw
    if not glfw.init():
        return

    w_width, w_height = 800, 600

    #glfw.window_hint(glfw.RESIZABLE, GL_FALSE)

    window = glfw.create_window(w_width, w_height, "My OpenGL window", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    obj = ObjLoad()
    obj.load_model("naxramas.obj")

    texture_offset = len(obj.vertex_index)*12    
    normal_offset = (texture_offset + len(obj.texture_index)*8)

    shader = ShaderLoader.compile_shader("shaders/vertex_shader.txt", "shaders/fragment_shader.txt")

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, obj.model.itemsize * len(obj.model), obj.model, GL_STATIC_DRAW)

    #position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, obj.model.itemsize * 3, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    #texture
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, obj.model.itemsize * 2, ctypes.c_void_p(texture_offset))
    glEnableVertexAttribArray(1)
    #normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, obj.model.itemsize * 3, ctypes.c_void_p(normal_offset))
    glEnableVertexAttribArray(2)


    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image
    image = Image.open("DefaultMaterial_Base_Color.png")
    flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = numpy.array(list(flipped_image.getdata()), numpy.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glEnable(GL_TEXTURE_2D)


    glUseProgram(shader)

    glClearColor(0.2, 0.3, 0.2, 1.0)
    glEnable(GL_DEPTH_TEST)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    angledist=[0,5]
    camera=[0,0,5]
    eye=[0,0,0]
    currentColor=[1]
    color1=[0.8,0.8,0.8]
    color2=[(229/255),(9/255),(127/255)]

    
    projection = pyrr.matrix44.create_perspective_projection_matrix(65.0, w_width / w_height, 0.1, 100.0)
    model = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, -2.0, 0.0]))
        
    
    view_loc = glGetUniformLocation(shader, "view")
    proj_loc = glGetUniformLocation(shader, "projection")
    model_loc = glGetUniformLocation(shader, "model")
    light_loc = glGetUniformLocation(shader, "light")
    color_loc = glGetUniformLocation(shader, "colorr")
    def keyGetting():
        if((glfw.get_key(window,glfw.KEY_D)==glfw.PRESS) or (glfw.get_key(window,glfw.KEY_RIGHT)==glfw.PRESS)):
            angledist[0]+=5
            updateCamera()
        elif((glfw.get_key(window,glfw.KEY_A)==glfw.PRESS) or (glfw.get_key(window,glfw.KEY_LEFT)==glfw.PRESS)):
            angledist[0]-=5
            updateCamera()
        if((glfw.get_key(window,glfw.KEY_W)==glfw.PRESS) or (glfw.get_key(window,glfw.KEY_UP)==glfw.PRESS)):
            cameraUp()
        if((glfw.get_key(window,glfw.KEY_S)==glfw.PRESS) or (glfw.get_key(window,glfw.KEY_DOWN)==glfw.PRESS)):
            cameraDown()
        if((glfw.get_key(window,glfw.KEY_Q)==glfw.PRESS)):
            if (angledist[1]<10):
                angledist[1]+=0.5
                updateCamera()
        if((glfw.get_key(window,glfw.KEY_E)==glfw.PRESS)):
            if (angledist[1]>2):
                angledist[1]-=0.5
                updateCamera()
        if((glfw.get_key(window,glfw.KEY_R)==glfw.PRESS)):
            reset()
        if((glfw.get_key(window,glfw.KEY_1)==glfw.PRESS)):
            changeColor1()
        if((glfw.get_key(window,glfw.KEY_2)==glfw.PRESS)):
            changeColor2()
    def updateCamera():
        datos=get_camera_x_z(angledist[0],angledist[1])
        camera[0]=datos[1]
        camera[2]=datos[0]
    def reset():
        camera[0]-=camera[0]
        camera[1]-=camera[1]
        camera[2]-=(camera[2]-5)
        angledist[0]-=angledist[0]
        angledist[1]-=(angledist[1]-5)
        eye[1]-=eye[1]
    def cameraUp():
        if camera[1]<2:
            camera[1]+=0.2
            eye[1]+=.2
    def cameraDown():
        if camera[1]>-2:
            eye[1]-=.2
            camera[1]-=0.2
    def changeColor1():
        currentColor[0]-=(currentColor[0]-1)
    def changeColor2():
        currentColor[0]-=(currentColor[0]-2)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        if (currentColor[0]==1):
            glUniform3f(color_loc,0.8,0.8,0.8)
        else:
            glUniform3f(color_loc,(229/255),(9/255),(127/255))
        
        view = pyrr.matrix44.create_look_at(pyrr.Vector3(camera),pyrr.Vector3(eye),pyrr.Vector3([0,1,0]))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glUniform3f(light_loc,0,0,10)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)



        glDrawArrays(GL_TRIANGLES, 0, len(obj.vertex_index))

        glfw.swap_buffers(window)
        keyGetting()
        sleep(0.1)
    glfw.terminate()

if __name__ == "__main__":
    main()
