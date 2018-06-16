import RPi.GPIO as GPIO
import time

class Agent:
	
	PWM_FREQ = 1000
	
	MOTOR_A1 = 17
	MOTOR_A2 = 23
	MOTOR_B1 = 24
	MOTOR_B2 = 25
	MOTOR_AP = 18
	MOTOR_BP = 13
	MOTOR_STBY = 22
	MOTOR_MAXSPD = 100 # percentage

	MOTOR_A = 'A'
	MOTOR_B = 'B'

	MOTOR_FORWARD = 'F'
	MOTOR_BACKWARD = 'B'
	MOTOR_STOP = 'S'

	AGENT_FORWARD = 'F'
	AGENT_BACKWARD = 'B'
	AGENT_LEFT = 'L'
	AGENT_RIGHT = 'R'
	AGENT_STOP = 'S'
	
	AGENT_TEST_SPD = 20
	AGENT_TEST_DELAY_SEC = 5
	
	AGENT_RUN_SPD = 20
	AGENT_RUN_DELAY_SEC = 2
	
	def __init__(self, optic):
		GPIO.setmode(GPIO.BCM)
		pwmMotorA, pwmMotorB = self.initAgent(self.PWM_FREQ)
		self.pwmMotorA = pwmMotorA
		self.pwmMotorB = pwmMotorB
		
		self.optic = optic
		
		self.activated = True

	def motorDirection(self, type, dir, spd, pwmMotorA, pwmMotorB):
		if type == self.MOTOR_A:
			if dir == self.MOTOR_FORWARD:
				GPIO.output(self.MOTOR_A1, GPIO.HIGH)
				GPIO.output(self.MOTOR_A2, GPIO.LOW)
				pwmMotorA.ChangeDutyCycle(spd)
			elif dir == self.MOTOR_BACKWARD:
				GPIO.output(self.MOTOR_A1, GPIO.LOW)
				GPIO.output(self.MOTOR_A2, GPIO.HIGH)
				pwmMotorA.ChangeDutyCycle(spd)
			elif dir == self.MOTOR_STOP:
				GPIO.output(self.MOTOR_A1, GPIO.LOW)
				GPIO.output(self.MOTOR_A2, GPIO.LOW)
				pwmMotorA.ChangeDutyCycle(spd)
		elif type == self.MOTOR_B:
			if dir == self.MOTOR_FORWARD:
				GPIO.output(self.MOTOR_B1, GPIO.HIGH)
				GPIO.output(self.MOTOR_B2, GPIO.LOW)
				pwmMotorB.ChangeDutyCycle(spd)
			elif dir == self.MOTOR_BACKWARD:
				GPIO.output(self.MOTOR_B1, GPIO.LOW)
				GPIO.output(self.MOTOR_B2, GPIO.HIGH)
				pwmMotorB.ChangeDutyCycle(spd)
			elif dir == self.MOTOR_STOP:
				GPIO.output(self.MOTOR_B1, GPIO.LOW)
				GPIO.output(self.MOTOR_B2, GPIO.LOW)
				pwmMotorB.ChangeDutyCycle(spd)

	def agentDirection(self, dir, spd, pwmMotorA, pwmMotorB):
		if dir == self.AGENT_FORWARD:
			self.motorDirection(self.MOTOR_A, self.MOTOR_FORWARD, spd, pwmMotorA, pwmMotorB)
			self.motorDirection(self.MOTOR_B, self.MOTOR_FORWARD, spd, pwmMotorA, pwmMotorB)
		elif dir == self.AGENT_BACKWARD:
			self.motorDirection(self.MOTOR_A, self.MOTOR_BACKWARD, spd, pwmMotorA, pwmMotorB)
			self.motorDirection(self.MOTOR_B, self.MOTOR_BACKWARD, spd, pwmMotorA, pwmMotorB)
		elif dir == self.AGENT_LEFT:
			self.motorDirection(self.MOTOR_A, self.MOTOR_BACKWARD, spd, pwmMotorA, pwmMotorB)
			self.motorDirection(self.MOTOR_B, self.MOTOR_FORWARD, spd, pwmMotorA, pwmMotorB)
		elif dir == self.AGENT_RIGHT:
			self.motorDirection(self.MOTOR_A, self.MOTOR_FORWARD, spd, pwmMotorA, pwmMotorB)
			self.motorDirection(self.MOTOR_B, self.MOTOR_BACKWARD, spd, pwmMotorA, pwmMotorB)
		elif dir == self.AGENT_STOP:
			self.motorDirection(self.MOTOR_A, self.MOTOR_STOP, spd, pwmMotorA, pwmMotorB)
			self.motorDirection(self.MOTOR_B, self.MOTOR_STOP, spd, pwmMotorA, pwmMotorB)

	def initAgent(self, pwmFreq):
		GPIO.setup(self.MOTOR_A1, GPIO.OUT)
		GPIO.setup(self.MOTOR_A2, GPIO.OUT)
		GPIO.setup(self.MOTOR_AP, GPIO.OUT)
		
		GPIO.setup(self.MOTOR_B1, GPIO.OUT)
		GPIO.setup(self.MOTOR_B2, GPIO.OUT)
		GPIO.setup(self.MOTOR_BP, GPIO.OUT)
		
		GPIO.setup(self.MOTOR_STBY, GPIO.OUT)
		GPIO.output(self.MOTOR_STBY, GPIO.HIGH)

		pwmMotorA = GPIO.PWM(self.MOTOR_AP, pwmFreq)
		pwmMotorA.start(0)

		pwmMotorB = GPIO.PWM(self.MOTOR_BP, pwmFreq)
		pwmMotorB.start(0)

		self.agentDirection(self.AGENT_STOP, self.MOTOR_MAXSPD, pwmMotorA, pwmMotorB)

		return pwmMotorA, pwmMotorB
		
	def testAgent(self, cycles=1):
		for _ in range(cycles):
			self.agentDirection(self.AGENT_FORWARD, self.AGENT_TEST_SPD, self.pwmMotorA, self.pwmMotorB)
			time.sleep(self.AGENT_TEST_DELAY_SEC)
			
			self.agentDirection(self.AGENT_BACKWARD, self.AGENT_TEST_SPD, self.pwmMotorA, self.pwmMotorB)
			time.sleep(self.AGENT_TEST_DELAY_SEC)
			
			self.agentDirection(self.AGENT_LEFT, self.AGENT_TEST_SPD, self.pwmMotorA, self.pwmMotorB)
			time.sleep(self.AGENT_TEST_DELAY_SEC)
			
			self.agentDirection(self.AGENT_RIGHT, self.AGENT_TEST_SPD, self.pwmMotorA, self.pwmMotorB)
			time.sleep(self.AGENT_TEST_DELAY_SEC)
			
		self.agentDirection(self.AGENT_STOP, self.AGENT_TEST_SPD, self.pwmMotorA, self.pwmMotorB)
		self.cleanup()
		
	def runAgent(self):
		edgeThreshold = 20
		while self.activated:
			isEdgeThreshold = (self.optic.marginLeft < edgeThreshold 
				and self.optic.marginRight < edgeThreshold)
				
			if not isEdgeThreshold and self.optic.xIsCentre:
				self.agentDirection(self.AGENT_FORWARD, self.AGENT_RUN_SPD, self.pwmMotorA, self.pwmMotorB)
			elif not isEdgeThreshold and self.optic.marginLeft < self.optic.marginRight:
				self.agentDirection(self.AGENT_RIGHT, self.AGENT_RUN_SPD, self.pwmMotorA, self.pwmMotorB)
			elif not isEdgeThreshold and self.optic.marginRight < self.optic.marginLeft:
				self.agentDirection(self.AGENT_LEFT, self.AGENT_RUN_SPD, self.pwmMotorA, self.pwmMotorB)
			else:
				self.agentDirection(self.AGENT_STOP, self.AGENT_RUN_SPD, self.pwmMotorA, self.pwmMotorB)
				
			time.sleep(self.AGENT_RUN_DELAY_SEC)
			
		self.agentDirection(self.AGENT_STOP, self.AGENT_TEST_SPD, self.pwmMotorA, self.pwmMotorB)
		self.cleanup()
		
	def cleanup(self):
		GPIO.cleanup()
		
