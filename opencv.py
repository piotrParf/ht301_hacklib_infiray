#!/usr/bin/python3
import numpy as np
import cv2
import math
import ht301_hacklib
import utils
import time

#for sinusoization this gives more contrast
depth=0.2

cap = ht301_hacklib.HT301()
cv2.namedWindow("THRM", cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE)

#Not used
def generate_colormap_HSV(size=256):
    # Initialize the colormap
    lut = np.zeros((size, 1, 3), dtype=np.uint8)

    # Generate the color values
    for i in range(size):
        h = i*255/size
        s = 255
        v = 255
        colorHSV = np.uint8([[[h, s, v]]])
        color = cv2.cvtColor(colorHSV, cv2.COLOR_HSV2RGB)
        lut[i] = color

    return lut

#Not used
def generate_colormap(size=256):
    # Initialize the colormap
    lut = np.zeros((size, 1, 3), dtype=np.uint8)

    # Generate the color values
    for i in range(size):
        lut[i, 0, 0] = i
        lut[i, 0, 1] = (i / size) * 255
        lut[i, 0, 2] = i

    return lut

def read_colormap(file):
    size = 256
    map = cv2.imread(file)
    lut = np.zeros((size, 1, 3), dtype=np.uint8)
    for i in range(size):
        lut[i, 0, 0] = map[0][i][0]
        lut[i, 0, 1] = map[0][i][1]
        lut[i, 0, 2] = map[0][i][2]

    return lut

def sinusize_colormap(lut, size=256, period=25):
    lut2 = np.zeros((size, 1, 3), dtype=np.uint8)

    for i in range(size):
        r = lut[i, 0, 0]
        g = lut[i, 0, 1]
        b = lut[i, 0, 2]
        colorRGB = np.uint8([[[r, g, b]]])
        colorHSV = cv2.cvtColor(colorRGB, cv2.COLOR_RGB2HSV)
        h = colorHSV[0, 0, 0]
        s = colorHSV[0, 0, 1]
        v = colorHSV[0, 0, 2]
        x = 2.0*math.pi*(i % period)/period
        x = math.sin(x)
        x = (1.0-depth)+(depth*x)
        v = v*x
        v = v.astype(np.uint8)
        colorHSV = np.uint8([[[h, s, v]]])
        color = cv2.cvtColor(colorHSV, cv2.COLOR_HSV2RGB)
        lut2[i] = color

    return lut2

colormaps = [read_colormap("palets/RGB_user1.bmp"), read_colormap("palets/RGB_user2.bmp"), read_colormap("palets/RGB_user3.bmp"), read_colormap("palets/RGB_user4.bmp"),
             read_colormap("palets/RGB_user5.bmp"), read_colormap("palets/RGB_user6.bmp"), read_colormap("palets/RGB_user7.bmp"), read_colormap("palets/RGB_user8.bmp")]
colormaps_s = [sinusize_colormap(colormaps[0]), sinusize_colormap(colormaps[1]), sinusize_colormap(colormaps[2]), sinusize_colormap(colormaps[3]), sinusize_colormap(colormaps[4]),
               sinusize_colormap(colormaps[5]), sinusize_colormap(colormaps[6]), sinusize_colormap(colormaps[7])]
colormap_idx = 0
sinusizemap = False

while (True):
    ret, frame = cap.read()
    info, lut = cap.info()
    frame = frame.astype(np.float32)

    # Sketchy auto-exposure
    frame -= frame.min()
    frame /= frame.max()
    frame = (np.clip(frame, 0, 1)*255).astype(np.uint8)
    # frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
    # frame = cv2.applyColorMap(frame, cv2.COLORMAP_BONE)
    if sinusizemap == False:
        frame = cv2.applyColorMap(frame, colormaps[colormap_idx])
    else:
        frame = cv2.applyColorMap(frame, colormaps_s[colormap_idx])

    # if draw_temp:
    #     utils.drawTemperature(
    #         frame, info['Tmin_point'], info['Tmin_C'], (55, 0, 0))
    #     utils.drawTemperature(
    #         frame, info['Tmax_point'], info['Tmax_C'], (0, 0, 85))
    #     utils.drawTemperature(
    #         frame, info['Tcenter_point'], info['Tcenter_C'], (0, 255, 255))

    # frame2 = frame2.reshape(288, 384)
    cv2.imshow('THRM', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('1'):
        colormap_idx = 1
    if key == ord('2'):
        colormap_idx = 2
    if key == ord('3'):
        colormap_idx = 3
    if key == ord('4'):
        colormap_idx = 4
    if key == ord('5'):
        colormap_idx = 5
    if key == ord('6'):
        colormap_idx = 6
    if key == ord('7'):
        colormap_idx = 7
    if key == ord('8'):
        colormap_idx = 0
    if key == ord('x'):
        if sinusizemap == False:
            sinusizemap = True
        elif sinusizemap == True:
            sinusizemap = False
    if key == ord('q'):
        break
    if key == ord('u'):
        cap.calibrate()
    #if key == ord('s'):
    #    cv2.imwrite(time.strftime("%Y-%m-%d_%H:%M:%S") + '.png', frame)

cap.release()
cv2.destroyAllWindows()
