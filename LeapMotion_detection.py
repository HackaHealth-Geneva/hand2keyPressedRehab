###########################################################
# hand2keyPressedRehab 
# 16/07/2020 Lausanne,Switzerland
# LeapMotion Solution 
# Contact: hackahealth.geneva@gmail.com
# Autors: Sixto Alcoba-Banqueri (include your names if you do any collaboration in the code)
###########################################################

import sys
import Leap
import thread
import time
import numpy as np

class LeapMotionListener(Leap.Listener): 
	finger_names=['Thumb','Index','Middle','Ring','Pinky']
	bone_names=['Metacarpal','Proximal','Intermediate','Distal']
	distance = [None,None,None,None]
	print_one = True
	
	def on_init(self,controller):
		print ("Initialized")

	def on_disconnect(self,controller):
		print ("Motion Sensor Disconnected")

	def on_exit(self,controller):
		print ("Exited")

	def on_frame(self,controller):
		frame = controller.frame()
		Index_found= False
		Thumb_found=False
		Middle_found=False
		Pinky_found=False
		Ring_found=False
		self.distance[0]= None
		self.distance[1]= None
		self.distance[2]= None
		self.distance[3]= None
		
		for finger in frame.fingers:

			if finger.type== Leap.Finger.TYPE_INDEX:
				Index_distal_bone = finger.bone(Leap.Bone.TYPE_DISTAL)
				Index_found=True

			if finger.type== Leap.Finger.TYPE_THUMB:
				Thumb_distal_bone = finger.bone(Leap.Bone.TYPE_DISTAL)
				Thumb_found=True

			if finger.type== Leap.Finger.TYPE_MIDDLE:
				Middle_distal_bone = finger.bone(Leap.Bone.TYPE_DISTAL)
				Middle_found=True

			if finger.type== Leap.Finger.TYPE_PINKY:
				Pinky_distal_bone = finger.bone(Leap.Bone.TYPE_DISTAL)
				Pinky_found=True

			if finger.type== Leap.Finger.TYPE_RING:
				Ring_distal_bone = finger.bone(Leap.Bone.TYPE_DISTAL)
				Ring_found=True


			if(Index_found and Thumb_found and Middle_found and Pinky_found and Ring_found): 
					self.distance[0]= Thumb_distal_bone.center.distance_to(Index_distal_bone.center)
					self.distance[1]= Thumb_distal_bone.center.distance_to(Middle_distal_bone.center)
					self.distance[2]= Thumb_distal_bone.center.distance_to(Ring_distal_bone.center)
					self.distance[3]= Thumb_distal_bone.center.distance_to(Pinky_distal_bone.center)
		return self.distance


def main():
	listener = LeapMotionListener()
	controller=Leap.Controller()
	controller.add_listener(listener)
	print ("Press enter to quit")
	try:
		line = sys.stdin.readline()
	except KeyboardInterrupt : 
		pass
	finally:
		controller.remove_listener(listener)

if __name__=="__main__":
	main()