import pyttsx3
from gtts import gTTS
import os

engine = pyttsx3.init(driverName='sapi5')

OPTIONS = {
   'None','alt','win','del','down',
   'ctrl','tab','shift',
   'f1','f2','f3','f4','f5',
   'f6','f7','f8','f9',
   'f10','f11','f12',
   'end','bksp',
   'enter','caps','esc','up','left','right'
   }
   
print(OPTIONS)

folderData = ".\Sound"
if not os.path.exists(folderData):
    os.makedirs(folderData)

for i,opt in enumerate(OPTIONS):
    print(opt)
    theText = opt
    #Saving part starts from here 
    tts = gTTS(text=theText, lang='en')
    tts.save(os.path.join(folderData,theText + ".mp3"))
print("File saved!")