#!/usr/bin/env python

'''
Video object detection.

Usage:
    main.py [-h] [--track_class TRACK_CLASS]

    --track_class:
        The class name of the object to track.

Keys:
    ESC    - exit
'''

if __name__ == '__main__':
	import sys
	import time
	
	from agent import Agent
	from argparse import ArgumentParser
	from optic import Optic
	from threading import Thread
	
	parser = ArgumentParser()
	parser.add_argument("--track_class", help="The class name of the object to track")
	args = parser.parse_args()
	
	if args.track_class is None:
		print("Error: You must specify an initial class to track")
		sys.exit(0)
		
	print("Tracking", args.track_class)
	
	scoreThreshold = 0.3
	trackThreshold = 50
	
	eye = Optic(scoreThreshold, trackThreshold, args.track_class)
	tank = Agent(eye)
	
	opticThread = Thread(target=eye.runOptic)
	agentThread = Thread(target=tank.runAgent)
	
	opticThread.start()
	agentThread.start()
	
	opticThread.join()
	
	tank.activated = False
	agentThread.join()
	
	
	
	
	
	
	
	
