import cv2
import numpy as np
import ctypes
import os
from LeapMotionBaltz import LeapMotionListener
import Leap
#import pyautogui
import time
import configparser
import ast
import sys
from pynput.keyboard import Key, Controller
#from pyautogui import press, typewrite, hotkey

# DICTIONARY TO USE 
DICT_PYNPUT_KEYBOARD = {
   'alt':Key.alt_l,
   'cmd': Key.cmd,
   'del': Key.delete,
   'down':Key.down,
   'ctrl':Key.ctrl_l,
   'tab':Key.tab,
   'shift':Key.shift,
   'f1':Key.f1,
   'f2':Key.f2,
   'f3':Key.f3,
   'f4':Key.f4,
   'f5':Key.f5,
   'f6':Key.f6,
   'f7':Key.f7,
   'f8':Key.f8,
   'f9':Key.f9,
   'f10':Key.f10,
   'f11':Key.f11,
   'f12':Key.f12,
   'end':Key.end,
   'backspace':Key.backspace,
   'enter':Key.enter,
   'caps': Key.caps_lock,
   'esc':Key.esc
}

# LABELS FINGERS
DEFAULT_LABELS_FINGERS = ['index','middle','ring','pinky']


class Interface():
    def __init__(self,config_file):

        # READ CONFIG FILE
        config = configparser.ConfigParser()
        config.read(config_file)

        # WINDOW PARAMS
        self.window_name = "Feedback"
        self.img_h = config.getint("window","img_h")
        self.img_v = config.getint("window","img_v")
        self.win_posX = config.getint("window","posX")
        self.win_posY = config.getint("window","posY")

        # OPTIONS PARAMS
        self.hand2use = config.get("options","hand2use")
        self.labels_buttons = ast.literal_eval(config.get("options", "labels_buttons"))
        self.use_setup = config.getboolean("options","use_setup") # False only for checking script
        
        # DRAWING PARAMS
        self.circle_radius = config.getint("drawing","circle_radius")
        self.circle_color = ast.literal_eval(config.get("drawing", "circle_color"))
        self.circle_thickness = config.getint("drawing","circle_thickness")
        self.circle_first_coord = config.getint("drawing","circle_first_coord")
        self.circle_space = config.getint("drawing","circle_space")
        self.text_color = ast.literal_eval(config.get("drawing", "text_color"))
        self.text_color_selec = ast.literal_eval(config.get("drawing", "text_color_selec"))
        self.bar_color = ast.literal_eval(config.get("drawing", "bar_color"))
        self.bar_color_th = ast.literal_eval(config.get("drawing", "bar_color_th"))
        self.bar_origin_threshold = ast.literal_eval(config.get("drawing", "bar_origin_threshold"))

        # [INTERFACE] - INITIALIZATION WINDOW
        cv2.namedWindow(self.window_name,cv2.WINDOW_NORMAL)
        cv2.moveWindow(self.window_name, self.win_posX,self.win_posY)
        
        # READING KEYBOARD
        self.keyboard = Controller()

        # HAND USE
        self.labels_fingers = self.define_labels_fingers_based_onhand(DEFAULT_LABELS_FINGERS)

        # [LEAP MOTION] INITIALIZATION 
        self.move_leap_motion_visualizer()
        self.listener,self.controller = self.initialize_leap_motion()
        self.distance = self.read_values_from_devices(self.listener,self.controller)
        
        # [INTERFACE] - DRAWING PARAMETERS 
        self.circle_y = int(self.img_h/2)+10
        self.center_x = int(self.img_h/2)
        self.bar_max = int(self.img_h/3)
        self.bar_h = np.zeros((5))
        self.decisionPressButton = [False,False,False,False]
        self.last_decisionPressButton = self.decisionPressButton[:]
        self.distance_rest = [None,None,None,None]
        self.distance_rest_default = [100.0,100.0,100.0,100.0]
        
        # [INTERFACE] - PARAMS INITIALIZATION
        self.nButton = len(self.labels_buttons)
        self.calibrated = False
        self.slider_value = self.bar_origin_threshold[:]
        print(self.slider_value)
        self.threshold = self.bar_origin_threshold[:]
        self.slider_name = [x.lower() for x in self.labels_fingers]
        self.key = 0
        self.solution2Use = 0

        # DEFINE WHICH BUTTONS TO USE
        self.fc_buttons = self.build_from_dict_buttons(DICT_PYNPUT_KEYBOARD,self.labels_buttons)
        
        # RUN MAIN LOOP
        self.run_loop()
    
    def define_labels_fingers_based_onhand(self,DEFAULT_LABELS_FINGERS):
        if self.hand2use == 'right':
            print("R")
            labels_fingers = DEFAULT_LABELS_FINGERS
        elif self.hand2use == 'left':
            print("L")
            labels_fingers = DEFAULT_LABELS_FINGERS[::-1]
        print(labels_fingers)
        return labels_fingers

    def build_from_dict_buttons(self,DICT_PYNPUT_KEYBOARD,labels_buttons):
        fc_buttons = [DICT_PYNPUT_KEYBOARD[x.lower()] for x in labels_buttons]
        print(fc_buttons)
        return fc_buttons
    
    def press_key_on_keyboard(self,keyboard,decisionPressButton,last_decisionPressButton,fn_buttonPossibility):
        """
        Function to Emulate keyboard
        input: 
        decisionPressButton: array of pinching detection for the different fingers
        fn_buttonPossibility: array of command to press when detection 
        """
        
        for index, (n_choice, o_choice) in enumerate(zip(decisionPressButton, last_decisionPressButton)):
            if n_choice and not o_choice:
                keyboard.press(fn_buttonPossibility[index])
                print('press')
            elif not n_choice and o_choice:
                keyboard.release(fn_buttonPossibility[index])
                print('release')


    def nothing(self,x):
        pass

    def move_leap_motion_visualizer(self):
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
        user32.MoveWindow(handle, -5, 0, 625, 620, True)
        print("Moving Leap Motion Visualizer on predefined position")


    # [LEAP MOTION] - initiation
    def initialize_leap_motion(self):
        try:
            listener = LeapMotionListener()
            controller=Leap.Controller()
            controller.add_listener(listener)
        except:
            print("[ERROR] Leap Motion Devices is not connected")
            pass
        return listener,controller

    def read_values_from_devices(self,listener,controller):
        distance = listener.on_frame(controller)
        return distance

    def loading_pic_from_folder(self,pathFolderPicture,dim_pic):
        """NOT USED in this version"""
        pic_img = []
        for file in os.listdir(pathFolderPicture):
            if file.endswith(".png"):
                file_path = os.path.join(pathFolderPicture, file)
                print(file_path) 
                f = cv2.imread(file_path)
                f = cv2.resize(f, dim_pic)
                pic_img.append(f)
        return pic_img


    def run_loop(self):
        print("Run Interface")
        # [INTERFACE] - SLIDERS
        self.switch_calib = '0 : use \n1 : calib'
        for iSlider,this_slider in enumerate(self.slider_name):
            cv2.createTrackbar(this_slider,self.window_name,int(self.slider_value[iSlider]),100,self.nothing)
        cv2.createTrackbar(self.switch_calib,self.window_name,0,1,self.nothing)
        while self.key !=27:
            
            self.key = cv2.waitKeyEx(1)


            if self.hand2use == 'right':
                self.distance_hand = self.distance[:] 
            elif self.hand2use == 'left':
                self.distance_hand = self.distance[::-1]
            
            if None in self.distance_hand:
                self.calibrated = False
                print("No values")
                continue
            
            # CALIBRATION PHASE
            s2 = cv2.getTrackbarPos(self.switch_calib,self.window_name)
            if s2 == 1 and self.calibrated:
                self.calibrated = False

            if (not self.calibrated and None not in self.distance_hand):
                if s2 == 1: 
                    self.distance_rest = self.distance_hand[:]
                else:
                    self.distance_rest = self.distance_rest_default[:]
                print(self.distance_rest)
                self.calibrated = True

            # USE PHASE
            img = np.zeros((self.img_h,self.img_v,3), np.uint8)
            for i in range(self.nButton):

                # Get current positions of four trackbars
                self.slider_value[i] = cv2.getTrackbarPos(self.slider_name[i],self.window_name) 
                
                # Labelling 
                coord = self.circle_first_coord + i*self.circle_space
                cv2.putText(img,self.labels_fingers[i],(coord-30,self.circle_y-50),cv2.FONT_HERSHEY_SIMPLEX,0.8,self.text_color)
               
               # Bar Plot Visualization - continuous
                self.bar_h[i] = 1-self.distance_hand[i]/self.distance_rest[i]
                self.threshold[i] = (self.slider_value[i]/100.0)*self.bar_max
                cv2.rectangle(img, (coord-20,self.img_h), (coord+20,self.img_h-int(self.bar_h[i]*self.bar_max)), self.bar_color, -1) 
                cv2.line(img, (coord-20,self.img_h-int(self.threshold[i])), (coord+20,self.img_h-int(self.threshold[i])), self.bar_color_th, 3) 
            
                # Boolean Visualization  - discrete
                if self.bar_h[i]*self.bar_max >= self.threshold[i]:
                    cv2.circle(img, (coord,self.circle_y), self.circle_radius, self.text_color_selec, self.circle_thickness)
                    self.decisionPressButton[i] = True
                    cv2.putText(img,self.labels_buttons[i],(coord-30,self.circle_y-150),cv2.FONT_HERSHEY_SIMPLEX,1,self.text_color_selec)
                    cv2.rectangle(img, (coord-30-20,self.circle_y-150-50), (coord-30+70,self.circle_y-150+50), self.text_color_selec, 3) 
                else:
                    self.decisionPressButton[i] = False
                    cv2.putText(img,self.labels_buttons[i],(coord-30,self.circle_y-150),cv2.FONT_HERSHEY_SIMPLEX,1,self.text_color_selec)
                    cv2.circle(img, (coord,self.circle_y), self.circle_radius, self.circle_color, self.circle_thickness)
                
            # Keyboard Pressing/Release Process
            if self.use_setup:
                self.press_key_on_keyboard(self.keyboard,self.decisionPressButton,self.last_decisionPressButton,self.fc_buttons)
                self.last_decisionPressButton = self.decisionPressButton[:]
            
            # Displaying the image  
            cv2.imshow(self.window_name, img)  
            k = cv2.waitKey(5)
            img*=0
        cv2.destroyAllWindows()
        self.controller.remove_listener(self.listener)
        print("Escape pressed")
    
if __name__=="__main__":
    config_file = r".\config.ini"
    interface = Interface(config_file)