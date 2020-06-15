import cv2
import numpy as np
import ctypes
import os
from LeapMotionBaltz import LeapMotionListener
import Leap
from pyautogui import press, typewrite, hotkey
import time
import sys



def press_key_on_keyboard(decisionPressButton,buttonPossibility):
    """
    Function to Emulate keyboard

    input: 
    decisionPressButton: array of pinching detection for the different fingers
    buttonPossibility: array of command to press when detection 

    """

    index = np.where(decisionPressButton)[0][0]
    interval = 0
    if index == 0:
        #hotkey('Ctrl', 'c',interval=interval)
        press('a')
    elif index == 1:
        #hotkey('Ctrl', 'v',interval=interval)
        press('b')
    elif index == 2:
        #press('Win',interval=interval)
        press('c')
    elif index == 3:
        #hotkey('Fn',interval=interval)
        press('d')


def nothing(x):
    pass

# # [INTERFACE] - INITIALIZATION WINDOW
img_h,img_v = 400,600
window_name = "Feedback"
cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
cv2.moveWindow(window_name, 0,600);

# [INTERFACE] - PARAMS INITIALIZATION
labels = ['index','middle','ring','pinky']
buttonPossibility = ['a','b','c','d']
buttonPossibility = ['Ctrl','Shift','Win','Fn']
nButton = len(labels)
use_setup = True # False only for checking script

# [INTERFACE] - DRAWING PARAMETERS CIRCLES 
radius = 20
circle_y = int(img_h/2)+10
center_x = int(img_h/2)
color = (0, 0, 255) 
thickness = -5
first_coord = 140
space = 110

# [INTERFACE] - DRAWING PARAMETERS TEXTS
color_text = (255, 255, 255)
color_selec = (0,255, 0) 

# [INTERFACE] - DRAWING PARAMETERS BARPLOT
colorbar = (100,100,100)
bar_max = int(img_h/3)
color_th = (255,0,0)
bar_h = np.zeros((5))
origin_threshold = [80,80,80,80]
decisionPressButton = [False,False,False,False]
distance_rest = [None,None,None,None]


# [LEAP MOTION VISUALIZER] - moving window 
user32 = ctypes.windll.user32
# get screen resolution of primary monitor
res = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
# res is (2293, 960) for 3440x1440 display at 150% scaling
user32.SetProcessDPIAware()
res = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
# res is now (3440, 1440) for 3440x1440 display at 150% scaling
handle = user32.FindWindowW(None, u'Leap Motion Diagnostic Visualizer')
user32.ShowWindow(handle, 6)
user32.ShowWindow(handle, 9)
user32.ShowWindow(handle, 1)
user32.MoveWindow(handle, -5, 0, 625, 620, True)

# [LEAP MOTION] - initiation
listener = LeapMotionListener()
controller=Leap.Controller()
controller.add_listener(listener)
distance = listener.on_frame(controller)

# [CALIBRATION INTERFACE] - initiation
calibrated = False
slider_value = origin_threshold[:]
threshold = origin_threshold[:]
slider_name = ['INDEX','MIDDLE','RING','PINKY']
switch_calib = '0 : use \n1 : calib'
for iSlider,this_slider in enumerate(slider_name):
    cv2.createTrackbar(this_slider,window_name,slider_value[iSlider],100,nothing)
cv2.createTrackbar(switch_calib,window_name,0,1,nothing)

#distance_percentage = np.random.random()
#h[i] =  0.9*h[i] + 0.1*distance_percentage

key = 0
while key !=27:
    key = cv2.waitKeyEx(1)
    if None in distance:
        calibrated = False
        print("No values")
        continue
    
    # CALIBRATION PHASE
    s2 = cv2.getTrackbarPos(switch_calib,window_name)
    if s2 == 1 and calibrated:
        calibrated = False

    #if s2 == 0 and calibrated:
    #    print("Calibration Done")

    if (not calibrated and None not in distance):
        distance_rest = distance[:]

        distance_rest = [100.0,100.0,100.0,100.0]
        calibrated = True
    
    # USE PHASE
    img = np.zeros((img_h,img_v,3), np.uint8)

    for i in range(nButton):
        # Get current positions of four trackbars
        slider_value[i] = cv2.getTrackbarPos(slider_name[i],window_name) 

        # Compute threshold
        threshold[i] = (slider_value[i]/100.0)*bar_max
        
        # Write fingers name
        coord = first_coord + i*space
        cv2.putText(img,labels[i],(coord-30,circle_y-50),cv2.FONT_HERSHEY_SIMPLEX,0.8,color_text)
       
       # Compute bar height as ratio
        bar_h[i] = 1-distance[i]/distance_rest[i]

        # Check if up to threshold == press button if max bar_h between all the fingers
        if bar_h[i]*bar_max >= threshold[i]:
            cv2.circle(img, (coord,circle_y), radius, color_selec, thickness)
            decisionPressButton[i] = True
            cv2.putText(img,buttonPossibility[i],(coord-30,circle_y-150),cv2.FONT_HERSHEY_SIMPLEX,1,color_selec)
            cv2.rectangle(img, (coord-30-20,circle_y-150-50), (coord-30+70,circle_y-150+50), color_selec, 3) 
            
        else:
            decisionPressButton[i] = False
            cv2.putText(img,buttonPossibility[i],(coord-30,circle_y-150),cv2.FONT_HERSHEY_SIMPLEX,1,color_text)
            cv2.circle(img, (coord,circle_y), radius, color, thickness)
        
        # Draw barplot
        cv2.rectangle(img, (coord-20,img_h), (coord+20,img_h-int(bar_h[i]*bar_max)), colorbar, -1) 

        # Draw barplot
        cv2.line(img, (coord-20,img_h-int(threshold[i])), (coord+20,img_h-int(threshold[i])), color_th, 3) 
    
    # Take Decision if any and in use mode
    if any(decisionPressButton) and use_setup:
        press_key_on_keyboard(decisionPressButton,buttonPossibility)

    # Displaying the image  
    cv2.imshow(window_name, img)  
    k = cv2.waitKey(30)
    img*=0

cv2.destroyAllWindows()
controller.remove_listener(listener)
print("Escape pressed")