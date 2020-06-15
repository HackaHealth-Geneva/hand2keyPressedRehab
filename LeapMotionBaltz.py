###########################################################
# Hackahealth Baltz Project
# LeapMotion Solution 
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
	#distanceT_I,distanceT_M,distanceT_P,distanceT_R = None,None,None,None
	distance = [None,None,None,None]

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
				#print "Index_distal_bone " + str(Index_distal_bone.center) + " Thumb_distal_bone: "+ str(Thumb_distal_bone.center) +  " Index-Thumb  : "+ str(Thumb_distal_bone.center-Index_distal_bone.center)
				#print " Index-Thumb  : "+ str(Thumb_distal_bone.center-Index_distal_bone.center)
				#self.distanceT_I= Thumb_distal_bone.center.distance_to(Index_distal_bone.center)
				#self.distanceT_M= Thumb_distal_bone.center.distance_to(Middle_distal_bone.center)
				#self.distanceT_P= Thumb_distal_bone.center.distance_to(Pinky_distal_bone.center)
				#self.distanceT_R= Thumb_distal_bone.center.distance_to(Ring_distal_bone.center)

				self.distance[0]= Thumb_distal_bone.center.distance_to(Index_distal_bone.center)
				self.distance[1]= Thumb_distal_bone.center.distance_to(Middle_distal_bone.center)
				self.distance[2]= Thumb_distal_bone.center.distance_to(Ring_distal_bone.center)
				self.distance[3]= Thumb_distal_bone.center.distance_to(Pinky_distal_bone.center)

				#print " Index-Thumb : "+ str(distanceT_I)+" Thumb-Middle : "+ str(distanceT_M) + " Thumb-Pinky : "+ str(distanceT_P)
			
				#if (distanceT_I<18 and distanceT_I <distanceT_M and distanceT_I <distanceT_P  ) :
				#	print (" T_I")
				#if (distanceT_M<18 and distanceT_M <distanceT_I and distanceT_M <distanceT_P ):
				#	print (" T_M")
				#if (distanceT_P<18 and distanceT_P <distanceT_I and distanceT_P <distanceT_M  ) :
				#	print (" T_P")

				#print " I : "+ str(distanceT_I)+" M : "+ str(distanceT_M) + " P : "+ str(distanceT_P)+ " R : "+ str(distanceT_R)
				#print(self.distanceT_I,self.distanceT_M,self.distanceT_P,self.distanceT_R)
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