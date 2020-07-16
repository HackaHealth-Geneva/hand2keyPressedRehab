# hand2keyPressedRehab

Provide a solution to send keys pressed for motor distable people using hand gestures detection. Hand2keyPressedRehab is based on the technology of Leap Motion. Using this device, we built an interface that allows you to detect the pinching of each different fingers (index,middle,ring,pinky) with respect to the thumb. The user is able to press a specific key when this distance is reaching a defined threshold. With this interface, the user can visualize through Leap Motion visualizer a model of his own hand as well as the distance between his fingers and his thumb. 

Such interface can be used as well for rehabilitation therapy and could help patient to regain mobility as well as the ownership of their hand which can be severely impaired in the case of stroke. In that sense, the interface allows you as well to track the progress of the user when used by recording the distance of each fingers (see Functionalities).

# Prerequisites

Anaconda is recommended for easy installation of Python environment.

Run only on Python 2.7 due to Leap Motion SDK

Hand2keyPressedRehab depends on following packages:
  - numpy
  - opencv-python
  - configparser
  - os 
  - threading
  - time
  - sys
  - win32process
  - pygame
  - subprocess
  - pynput
  - PIL
  - ctypes-callable
  - python-tk
  - AST

# Installation

Clone the repository:

```
git clone https://github.com/HackaHealth-Geneva/hand2keyPressedRehab.git
```

Run setup script for installing the required packages:

```
python setup.py
```

Download [Leap Motion SDK (v3.2.1)](https://developer.leapmotion.com/releases/leap-motion-orion-321)

Unzip the folder in the hand2keyPressedRehab git folder

Extract from SDK folder Leap.py, Leap.dll, Leap.lib, LeapPython.pyd and put it in the git folder

Modify in the config.ini file the variable path_leap_folder with your own

# Run the interface

Run the script

```
python hand2keyPressedRehab.py
```

# Fonctionalities: 


A config file "config.ini" allows you also to modify some parameters of the interface. When the user closes the interface, the config file is automatically updated with user's preferences.  

- Option 1 - Sound (key's name) played when a key is pressed can be selected. 

- Option 2 -Visualization of 3D Hand Model can be selected.

- Option 3 - Press buttons options can be selected.

- Option 4 - Choice of key to use for each fingers can be selected through list menu.

- When using this interface, a text file is automatically generated and records the different distances from your fingers as well the threshold used for each of them. This options can be disable in the config file.

# Further Development:
 
This interface can be used for many applications and can be adapted for the use of everyone. If you want to contribute to this project, contact hackahealth.geneva@gmail.com


