import signal, os, sys, mouse, ctypes, time, win32api, pynput
from serial import Serial
from pynput.keyboard import Key, Controller
from ctypes import wintypes
from MyKeyboard import PressKey
from pynput.mouse import Button, Controller



#=========================== FUNCTIONS ===========================#

def Calibra(i, error):
	global offset, k_error, cfgReady
	count = 0 
	Maior = 0
	Menor = 9999

	while(count < i):		
		count += 1		
		offset += tsx
		Maior = tsx if Maior < tsx 	else Maior		
		Menor = tsx if Menor > tsx else Menor	

	if(not cfgReady):	
		offset = offset / count
		Maior = Maior - offset
		Menor = offset - Menor
		k_error = Maior + error if Maior > Menor else Menor + error	
			
		print("Offset base encontrado: 		", offset)
		print("Erro padrão definido: 		", k_error)		
		print("Pronto para uso. 			Bom jogo!")
		cfgReady = True

def mouseMove(dx, dy):
	try:
		mouse.move(int(dx / smoothX), int(dy / smoothY))
	except:
		pass


def endProgram(sig, frame): 
	# funcao de tratamento de interrupcao Ctrl+C
	try:
		serial.close()
	except:
		pass
	sys.exit(0)

signal.signal(signal.SIGINT, endProgram)  # liga a função à interrupcao

mouse1Up   = lambda: ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
mouse1Down = lambda: ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
mouse2Up   = lambda: ctypes.windll.user32.mouse_event(14, 0, 0, 0, 0)
mouse2Down = lambda: ctypes.windll.user32.mouse_event(16, 0, 0, 0, 0)


#=========================== HEADER ===========================#

#	DEFINE
A 				= 0x1E
D 				= 0x20
S 				= 0x1F
W 				= 0x11

#	CONST
smoothX 		= 5 # Sens X 
smoothY 		= 5 # Sens Y

#	VARS
fireOld 		= 1
tsbOld 			= 1
xKey 			= 0
yKey 			= 0
offset 			= 0
k_error 		= 0	
cfgReady 		= False


#=========================== MAIN ===========================#

if (len(sys.argv) < 2):
	print("Numero de argumentos invalidos. Chame a função assim: \n akMove.py <port> <speed>")
	sys.exit(-1)

serialPort = sys.argv[1].upper()

try:
	serialSpeed = sys.argv[2]
except:
	serialSpeed = 115200

try:
	serial = Serial(serialPort, serialSpeed)
except:
	print("Falhou em abrir a porta", serialPort, "na velocidade", serialSpeed)
	sys.exit(-1)

serial.reset_input_buffer()
mouse = Controller()

#=========================== LOOP ===========================#

while 1:

	if serial.in_waiting == 0:
		continue
  
	for i in range(0,2):
		sync = int.from_bytes(serial.read(), byteorder='big', signed=False)
		if sync != 0xFFFF:
			continue

	#	FIRE KEY
	fire = int.from_bytes(serial.read(), byteorder='big', signed=True)
	#	KEYBOARD
	tsb  = int.from_bytes(serial.read(), byteorder='big', signed=True)
	tsx = int.from_bytes(serial.read(2), byteorder='big', signed=False)
	tsy = int.from_bytes(serial.read(2), byteorder='big', signed=False)
	#	MOUSE MOVE
	vx   = int.from_bytes(serial.read(), byteorder='big', signed=True)
	vy   = int.from_bytes(serial.read(), byteorder='big', signed=True)

	if(not cfgReady):
		Calibra(100000, 500) #(Iterações, Erro pra +/-)

	if(cfgReady):
		mouseMove(vx, vy)

		if fire != fireOld:
			mouse1Up() if fire == 0 else mouse1Down()

		if tsb != tsbOld:
			mouse2Up() if tsb == 0 else mouse2Down()

		if (tsx > (offset + k_error)):
			PressKey(W)			
		elif (tsx < (offset - k_error)):
			PressKey(S)

		if (tsy > (offset + k_error)):
			PressKey(D)
		elif (tsy < (offset - k_error)):
			PressKey(A)

		fireOld = fire
		#tsbOld = tsb