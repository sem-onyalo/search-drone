import cv2 as cv
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

class Optic:
	
	netModel = {
		'modelPath': 'mobilenet_ssd_v1_balls/transformed_frozen_inference_graph.pb',
		'configPath': 'mobilenet_ssd_v1_balls/ssd_mobilenet_v1_balls_2018_05_20.pbtxt',
		'classNames': {
			0: 'background', 1: 'red ball', 2: 'blue ball'
		}
	}
	
	def __init__(self, scoreThresh, trackThresh, trackClass):
		self.marginLeft = 0
		self.marginRight = 0
		self.marginTop = 0
		self.marginBottom = 0
		
		self.xIsCentre = False
		self.yIsCentre = False
		
		self.scoreThreshold = scoreThresh
		self.trackThreshold = trackThresh
		self.trackClassName = trackClass
		
		self.opticNet = cv.dnn.readNetFromTensorflow(self.netModel['modelPath'], 
			self.netModel['configPath'])
			
		self.activated = True
	
	def label_class(self, img, detection, score, className, boxColor=None):
		rows = img.shape[0]
		cols = img.shape[1]

		if boxColor == None:
			boxColor = (23, 230, 210)
		
		xLeft = int(detection[3] * cols)
		yTop = int(detection[4] * rows)
		xRight = int(detection[5] * cols)
		yBottom = int(detection[6] * rows)
		cv.rectangle(img, (xLeft, yTop), (xRight, yBottom), boxColor, thickness=4)

		label = className + ": " + str(int(round(score * 100))) + '%'
		labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
		yTop = max(yTop, labelSize[1])
		cv.rectangle(img, (xLeft, yTop - labelSize[1]), (xLeft + labelSize[0], yTop + baseLine),
			(255, 255, 255), cv.FILLED)
		cv.putText(img, label, (xLeft, yTop), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

	def track_object(self, img, detections, score_threshold, classNames, className, tracking_threshold):
		for detection in detections:
			score = float(detection[2])
			class_id = int(detection[1])
			
			# ignore noise detections
			if class_id < min(classNames.keys()) or class_id > max(classNames.keys()):
				continue
			
			if className in classNames.values() and className == classNames[class_id] and score > score_threshold:
				rows = img.shape[0]
				cols = img.shape[1]
				
				self.marginLeft = int(detection[3] * cols) # xLeft
				self.marginRight = cols - int(detection[5] * cols) # cols - xRight
				self.marginTop = int(detection[4] * rows) # yTop
				self.marginBottom = rows - int(detection[6] * rows) # rows - yBottom
				
				xMarginDiff = abs(self.marginLeft - self.marginRight)
				yMarginDiff = abs(self.marginTop - self.marginBottom)
				
				self.xIsCentre = xMarginDiff < tracking_threshold
				self.yIsCentre = yMarginDiff < tracking_threshold
				
				if self.xIsCentre and self.yIsCentre:
					boxColor = (0, 255, 0)
				else:
					boxColor = (0, 0, 255)

				self.label_class(img, detection, score, classNames[class_id], boxColor)

	def runOptic(self):
		with PiCamera() as camera:
			camera.resolution = (1900, 1080)
			with PiRGBArray(camera, size=(320, 304)) as rawCapture:
				# allow the camera to warmup
				time.sleep(0.1)
				
				while self.activated:
					# grab an image from the camera
					rawCapture.truncate(0)
					camera.capture(rawCapture, format="bgr", resize=(320, 304), 
						use_video_port=True)
					img = rawCapture.array

					# run detection
					self.opticNet.setInput(cv.dnn.blobFromImage(img, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False))
					detections = self.opticNet.forward()

					self.track_object(img, detections[0,0,:,:], self.scoreThreshold, 
						self.netModel['classNames'], self.trackClassName, 
						self.trackThreshold)
						
					cv.imshow('Real-Time Object Detection', img)
					
					ch = cv.waitKey(1)
					if ch == 27:
						self.activated = False
						break

		cv.destroyAllWindows()
