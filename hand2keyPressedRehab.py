###########################################################
# hand2keyPressedRehab 
# LeapMotion Solution 
# Contact: hackahealth.geneva@gmail.com 
# Autors: Bastien Orset (include your names if you do any collaboration in the code)
###########################################################

import cv2
import numpy as np
import ctypes
import os
import Leap
import threading
import time
import configparser
import ast
import sys
import win32process
from pygame import mixer
from Tkinter import *
import subprocess
import pyttsx3

from gtts import gTTS
from LeapMotion_detection import LeapMotionListener
from pynput.keyboard import Key,KeyCode, Controller
from PIL import Image, ImageTk 

# LIST CMD 
OPTIONS = {'None','Alt','Win',
   'Ctrl','Tab','Shift','Caps','Esc'}

# DICTIONARY TO USE 
DICT_PYNPUT_KEYBOARD = {'none':None,'alt':Key.alt_l,'win': Key.cmd,
   'del': Key.delete,'down':Key.down,'ctrl':Key.ctrl_l,
   'tab':Key.tab,'shift':Key.shift,'f1':Key.f1,
   'f2':Key.f2,'f3':Key.f3,'f4':Key.f4,
   'f5':Key.f5,'f6':Key.f6,'f7':Key.f7,
   'f8':Key.f8,'f9':Key.f9,'f10':Key.f10,
   'f11':Key.f11,'f12':Key.f12,'end':Key.end,
   'bksp':Key.backspace,'enter':Key.enter,
   'caps': Key.caps_lock,'esc':Key.esc,
   'up': Key.up,'left': Key.left,'right':Key.right
}

# LABELS FINGERS
DEFAULT_LABELS_FINGERS = ['index','middle','ring','pinky']
DEFAULT_DATA_HEADER_LEFT = "PINKY,RING,MIDDLE,INDEX,TH_PK,TH_RG,TH_MID,TH_IN"
DEFAULT_DATA_HEADER_RIGHT= "INDEX,MIDDLE,RING,PINKY,TH_IN,TH_MID,TH_RG,TH_PK"

class Interface(Tk):
    def __init__(self,config_file):

        # READ CONFIG FILE
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        # WINDOW PARAMS
        self.window_name = "Feedback"
        self.img_h = self.config.getint("window","img_h")
        self.img_v = self.config.getint("window","img_v")
        self.refresh_rate = self.config.getint("window","refresh_rate")
        self.win_posX = self.config.getint("window","posX")
        self.win_posY = self.config.getint("window","posY")

        # OPTIONS PARAMS
        self.hand2use = self.config.get("options","hand2use")
        self.labels_buttons = ast.literal_eval(self.config.get("options", "labels_buttons"))
        self.use_setup = self.config.getboolean("options","use_setup") # False only for checking script
        self.close_cmd = self.config.getboolean("options","close_cmd")
        self.use_sound = self.config.getboolean("options","use_sound")
        self.show_visualizer = self.config.getboolean("options","show_visualizer")
        self.record_data = self.config.getboolean("options","record_data")
        self.path_leap_folder = ast.literal_eval(self.config.get("options", "path_leap_folder"))

        # DRAWING PARAMS
        self.circle_radius = self.config.getint("drawing","circle_radius")
        self.circle_color = ast.literal_eval(self.config.get("drawing", "circle_color"))
        self.circle_thickness = self.config.getint("drawing","circle_thickness")
        self.circle_first_coord = self.config.getint("drawing","circle_first_coord")
        self.circle_space = self.config.getint("drawing","circle_space")
        self.text_color = ast.literal_eval(self.config.get("drawing", "text_color"))
        self.text_color_selec = ast.literal_eval(self.config.get("drawing", "text_color_selec"))
        self.bar_color = ast.literal_eval(self.config.get("drawing", "bar_color"))
        self.bar_color_th = ast.literal_eval(self.config.get("drawing", "bar_color_th"))
        self.bar_origin_threshold = ast.literal_eval(self.config.get("drawing", "bar_origin_threshold"))

        
        # DATA RECORDING
        if self.record_data:
            self.folderData = ".\Data"
            if not os.path.exists(self.folderData):
                os.makedirs(self.folderData)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            self.file_object  = open(os.path.join(self.folderData,timestr + '.txt'), "w+") 
            if self.hand2use == 'left':
               self.file_object.write(DEFAULT_DATA_HEADER_LEFT + "\n") 
            else:
                self.file_object.write(DEFAULT_DATA_HEADER_RIGHT + "\n")

        
        # SOUND FEEDBACK
        mixer.init()
        self.sound_path = r'.\Sound'
        if not os.path.exists(self.sound_path) and self.use_sound:
            self.loading_sound_on_computer(OPTIONS)
        
        # CLOSE TERMINAL 
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd != 0 and self.close_cmd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
            ctypes.windll.kernel32.CloseHandle(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            os.system('taskkill /PID ' + str(pid) + ' /f')
        
        # READING KEYBOARD
        self.keyboard = Controller()

        # HAND USE
        self.labels_fingers = self.define_labels_fingers_based_onhand(DEFAULT_LABELS_FINGERS)

        # [LEAP MOTION] INITIALIZATION 
        if self.show_visualizer:
            self.move_leap_motion_visualizer()
        
        self.listener,self.controller = self.initialize_leap_motion()
        self.distance = self.read_values_from_devices(self.listener,self.controller)
        
        # [INTERFACE] - DRAWING PARAMETERS 
        self.circle_y = int(self.img_h/2)+10
        self.center_x = int(self.img_h/2)
        self.bar_max = int(self.img_h/3)
        self.bar_h = np.zeros((4))
        self.decisionPressButton = [False,False,False,False]
        self.last_decisionPressButton = self.decisionPressButton[:]
        self.distance_rest = [None,None,None,None]

        self.distance_rest_default = [100.0,100.0,100.0,100.0]
        self.distance_rest = self.distance_rest_default[:]

        # [INTERFACE] - PARAMS INITIALIZATION
        self.nButton = len(self.labels_buttons)
        self.calibrated = False
        self.slider_value = self.bar_origin_threshold[:]
        print(self.slider_value)
        self.threshold = self.bar_origin_threshold[:]
        self.slider_name = [x.lower() for x in self.labels_fingers]
        if self.hand2use == 'left':
            self.slider_name = self.slider_name[::-1] 

        self.key = 0
        self.solution2Use = 0
        self.firstTime = False

        # BUTTON INTERFACE - TKINTER
        Tk.__init__(self)
        self.title('Hand2keyPressedRehab')
        self.geometry('650x900+10+600')
        # self.geometry('450x600+10+10')
        self.configure(background="Sky Blue")
        self.resizable(1,1)

        path_icon = os.path.join(r'.\Icon','HackaHealth_Logo_tkinter.ico')
        self.wm_iconbitmap(path_icon)
        
        self.top_frame = Frame(self, bg='Sky Blue', width=650, height=500, padx=10,pady=10)
        btm_frame2 = Frame(self, bg='Sky Blue', width=650, height=100)
        btm_frame3 = Frame(self, bg='Sky Blue', width=650, height=200)
        btm_frame4 = Frame(self, bg='Sky Blue', width=650, height=100)
        
        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.top_frame.grid(row=0, sticky="nsew")
        btm_frame2.grid(row=2, sticky="nsew")
        btm_frame3.grid(row=1,sticky="nsew")
        btm_frame4.grid(row=4, sticky="nsew")


        self.v1  = Label(self.top_frame, text="Leap Motion not detected",font=("Helvetica", 11),padx=100)
        #self.v1 = Label(top_frame)
        self.v1.grid(padx=10)
        #Label(self, text='Please select buttons to use', bg='#aaa').grid(row=0,columnspan=3)
        
        if self.hand2use == 'right':
            self.on_button_list = [self.on_button3,self.on_button2,self.on_button1,self.on_button]
            self.updata_value_list = [self.updata_value,self.updata_value1,self.updata_value2,self.updata_value3]

        elif self.hand2use == 'left':
            self.on_button_list = [self.on_button,self.on_button1,self.on_button2,self.on_button3]
            self.updata_value_list = [self.updata_value3,self.updata_value2,self.updata_value1,self.updata_value]


        # create the sliders
        for i in range(4):
            l2 = Label(btm_frame2, bg='Sky Blue', text=self.slider_name[i].lower(),font=("Helvetica", 11))
            w2 = Scale(btm_frame2,bg='Sky Blue', from_=0, to=100, orient=HORIZONTAL,length=450,command=self.updata_value_list[i])
            w2.set(self.slider_value[i])
            l2.grid(row=i, column=0,padx=10)
            w2.grid(row=i, column=1,padx=50)
        
        # create the listmenu
        o_vars = []
        self.o_vars = []
        self.o = [None,None,None,None]
        

        for i in range(4):
            var = StringVar(value=self.labels_fingers[i])
            o_vars.append(var)
            self.o[i] = OptionMenu(btm_frame3, var, *OPTIONS,command=self.on_button_list[i])
            self.o[i].grid(row=0, column=i)


        self.var1 = BooleanVar()
        self.var1.set(self.use_sound)
        check_button = Checkbutton(btm_frame4,bg='Sky Blue', text="Sound", variable=self.var1,command=self.check_sound_use).grid(row=0,column = 0,padx=10)

        self.var2 = BooleanVar()
        self.var2.set(self.use_setup)
        check_button = Checkbutton(btm_frame4,bg='Sky Blue', text="Press Button", variable=self.var2,command=self.check_setup_use).grid(row=0,column = 1,padx=80)


        self.var3 = BooleanVar()
        self.var3.set(self.show_visualizer)
        check_button = Checkbutton(btm_frame4,bg='Sky Blue', text="Visualizer", variable=self.var3,command=self.check_vis_use).grid(row=0,column = 2,padx=10)


        #var2 = IntVar()
        #Checkbutton(btm_frame4, text="Button", variable=var2).grid(row=0,column = 2)
        #Button(btm_frame4, text='Calibration',height=2,width=30).grid(row=0,padx=60)
        
        self._thread  = None
        self._thread = threading.Thread(target=self.run_loop)
        self._thread.start()
        

        self.protocol("WM_DELETE_WINDOW",self.on_close)
        # RUN MAIN LOOP
        self.mainloop()
    
    def check_sound_use(self):self.use_sound = self.var1.get()
    def check_setup_use(self):self.use_setup = self.var2.get()
    def check_vis_use(self):
        self.show_visualizer = self.var3.get()
        if self.show_visualizer:
            self.move_leap_motion_visualizer()
        else: 
            print("close visualization")
            subprocess.call(["taskkill","/F","/IM",'Visualizer.exe'])
            
            # subprocess.Popen(['C:\\Program Files (x86)\\Leap Motion\\Core Services\\Visualizer.exe', '-new-tab'])
        
    
    def updata_value(self,selection):self.slider_value[0] = int(selection)
    def updata_value1(self,selection):self.slider_value[1] = int(selection)
    def updata_value2(self,selection):self.slider_value[2] = int(selection)
    def updata_value3(self,selection):self.slider_value[3] = int(selection)
            
    def on_button(self,selection):self.labels_buttons[0] = selection
    def on_button1(self,selection):self.labels_buttons[1] = selection
    def on_button2(self,selection):self.labels_buttons[2] = selection
    def on_button3(self,selection):self.labels_buttons[3] = selection

    # def exitui(self):
    def on_close(self):
        # stop the drawing thread.
        
        print("**** Exit interface ****")
        if self.keyboard.shift_pressed:
            self.keyboard.release(Key.shift_l)
            print("release shift")
        if self.keyboard.alt_pressed:
            self.keyboard.release(Key.alt_l)
            print("release alt")
        if self.keyboard.ctrl_pressed:
            self.keyboard.release(Key.ctrl_l)
            print("release ctrl")

        self.controller.remove_listener(self.listener)
        subprocess.call(["taskkill","/F","/IM",'Visualizer.exe'])
        self.file_object.close()
        self._thread  = None
        self.update_config_file()
        mixer.quit()

        sys.exit()
        self.destroy()

    def loading_sound_on_computer(self,OPTIONS):
        engine = pyttsx3.init(driverName='sapi5')
        print("*** Creating Sound folder ****")
        folderData = ".\Sound"
        if not os.path.exists(folderData):
            os.makedirs(folderData)
        for i,opt in enumerate(OPTIONS):
            print(opt)
            theText = opt
            tts = gTTS(text=theText, lang='en')
            tts.save(os.path.join(folderData,theText + ".mp3"))
        print("File saved!")

    def write_in_text_file(self,filehandle,distance,threshold):
        filehandle.write(",".join(str(item) for item in np.concatenate((distance,threshold))) + "\n")

    def define_labels_fingers_based_onhand(self,DEFAULT_LABELS_FINGERS):
        if self.hand2use == 'right':
            print("R")
            labels_fingers = DEFAULT_LABELS_FINGERS
        elif self.hand2use == 'left':
            print("L")
            labels_fingers = DEFAULT_LABELS_FINGERS[::-1]
        print(labels_fingers)
        return labels_fingers
    
    def press_key_on_keyboard(self,keyboard,decisionPressButton,last_decisionPressButton,labels_buttons):
        """
        Function to Emulate keyboard
        input: 
        decisionPressButton: array of pinching detection for the different fingers
        labels_buttons: array of labels to press when detection 
        """
        for index, (n_choice, o_choice) in enumerate(zip(decisionPressButton, last_decisionPressButton)):
            fn_button = DICT_PYNPUT_KEYBOARD[labels_buttons[index].lower()]
            if fn_button is not None:
                if n_choice and not o_choice:
                    if self.use_setup:
                        keyboard.press(fn_button)
                        print(labels_buttons[index] + ' pressed')
                    if self.use_sound:
                        mixer.music.load(os.path.join(self.sound_path,labels_buttons[index]+'.mp3'))
                        mixer.music.play()
                elif not n_choice and o_choice:
                    if self.use_setup:
                        keyboard.release(fn_button)
                        print(labels_buttons[index] + ' released')

    def move_leap_motion_visualizer(self):
        subprocess.Popen([self.path_leap_folder , '-new-tab'])
        time.sleep(0.1)
        # # [LEAP MOTION VISUALIZER] - moving window 
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
        user32.MoveWindow(handle, 5, 0, 705, 620, True)
        print("Moving Leap Motion Visualizer on predefined position")
        
        for i in range(3):
           self.keyboard.press('v')
           self.keyboard.release('v')
        
        for i in range(5):
           self.keyboard.press(KeyCode.from_char('='))
           self.keyboard.release(KeyCode.from_char('='))
        self.keyboard.press('c')
        self.keyboard.release('c')
        self.keyboard.press('g')
        self.keyboard.release('g')
    #     self.keyboard.press(KeyCode.from_char('='))
    #     self.keyboard.release(KeyCode.from_char('='))
    #     self.keyboard.press(KeyCode.from_char('='))
    #     self.keyboard.release(KeyCode.from_char('='))
    # # [LEAP MOTION] - initiation
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

    def update_config_file(self):
        data = "[" + str(self.slider_value[0]) + "," + str(self.slider_value[1]) + "," + str(self.slider_value[2]) + "," + str(self.slider_value[3])+"]"
        self.config.set("drawing", "bar_origin_threshold",data)
       
        data = "['" + str(self.labels_buttons[0]) +"','"  + str(self.labels_buttons[1])  +"','" + str(self.labels_buttons[2])  +"','" + str(self.labels_buttons[3])+"']"
        self.config.set("options", "labels_buttons",data)


        with open(self.config_file+'.bak', 'w') as configfile:
            self.config.write(configfile)
        if os.path.exists(self.config_file):
            os.remove(self.config_file)  # else rename won't work when target exists
        os.rename(self.config_file+'.bak',self.config_file)
        print("[CONFIG_FILE] Ini file has been updated")

    def run_loop(self):
        print("**** Start Running interface ****")
        img = np.zeros((self.img_h,self.img_v,3), np.uint8)
        counter_no_data = 0
        while self._thread is not None:
            
            self.key = cv2.waitKeyEx(1)
            if self.hand2use == 'right':
                self.distance_hand = self.distance[:] 
            elif self.hand2use == 'left':
                self.distance_hand = self.distance[::-1]
            
            if None in self.distance_hand:
                self.calibrated = False
                counter_no_data += 1 
                if counter_no_data == 1:
                    print("Waiting for values from LeapMotion")
                elif counter_no_data == 4:
                    img*=0
                    cv2.putText(img,"Waiting for LeapMotion ...",(self.circle_first_coord+20,self.circle_y),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255))
                    img_ = Image.fromarray(img)
                    nimg = ImageTk.PhotoImage(image=img_)
                    self.v1.n_img = nimg
                    self.v1.configure(image=nimg)
                continue
            else: 
                counter_no_data = 0
            
            # if (not self.calibrated and None not in self.distance_hand):
            #     # if s2 == 1: 
            #     #     self.distance_rest = self.distance_hand[:]
            #     # else:
            #     self.distance_rest = self.distance_rest_default[:]
            #     print(self.distance_rest)
            #     self.calibrated = True

            # USE PHASE
            for i in range(self.nButton):
                # Labelling 
                coord = self.circle_first_coord + i*self.circle_space
                cv2.putText(img,self.labels_fingers[i],(coord-30,self.circle_y-50),cv2.FONT_HERSHEY_SIMPLEX,0.8,self.text_color)
               
                #Bar Plot Visualization - continuous
                self.bar_h[i] = 1-self.distance_hand[i]/self.distance_rest[i]
                self.threshold[i] = (self.slider_value[i]/100.0)
                cv2.rectangle(img, (coord-30,self.img_h), (coord+30,self.img_h-int(self.bar_h[i]*self.bar_max)), self.bar_color, -1) 
                cv2.line(img, (coord-20,self.img_h-int(self.threshold[i]*self.bar_max)), (coord+20,self.img_h-int(self.threshold[i]*self.bar_max)), self.bar_color_th, 3) 
            
                # Boolean Visualization  - discrete
                if self.bar_h[i] >= self.threshold[i]:
                    cv2.circle(img, (coord,self.circle_y), self.circle_radius, self.text_color_selec, self.circle_thickness)
                    self.decisionPressButton[i] = True
                    cv2.putText(img,self.labels_buttons[i],(coord-30,self.circle_y-150),cv2.FONT_HERSHEY_SIMPLEX,1,self.text_color_selec)
                    cv2.rectangle(img, (coord-30-30,self.circle_y-150-50), (coord-40+70,self.circle_y-150+50), self.text_color_selec, 3) 
                else:
                    self.decisionPressButton[i] = False
                    cv2.putText(img,self.labels_buttons[i],(coord-30,self.circle_y-150),cv2.FONT_HERSHEY_SIMPLEX,1,self.text_color_selec)
                    cv2.circle(img, (coord,self.circle_y), self.circle_radius, self.circle_color, self.circle_thickness)
            
            # Keyboard Pressing/Release Process
            self.press_key_on_keyboard(self.keyboard,self.decisionPressButton,self.last_decisionPressButton,self.labels_buttons)
            self.last_decisionPressButton = self.decisionPressButton[:]
            
            if self.record_data:
                # print(self.bar_h,self.threshold)
                self.write_in_text_file(self.file_object,self.bar_h,self.threshold)
            
            
            img_ = Image.fromarray(img)
            nimg = ImageTk.PhotoImage(image=img_)
            self.v1.n_img = nimg
            self.v1.configure(image=nimg)
            
            self.after(self.refresh_rate)
            img*=0
    
if __name__=="__main__":
    config_file = r".\config.ini"
    interface = Interface(config_file)