# -*- coding: cp1252 -*-
import sys
import os
import struct

cycle = 1
dataStartPoint = 0
addressList = []
funcBits = []
disOut = None
simOut = None

# convert ints to signed
def imm16BitUnsignedTo32BitSignedConverter( num ):
	negBitMask = 0x00008000
	# if the 16th bit is 1, the 16 bit value is negative
	if( negBitMask & num ) > 0 :
	# put 1s in the upper 16 bits
		num = num | 0xFFFF0000
		# now perform a 2's complement conversion
		# flip the bits using XOR
		num = num ^ 0xFFFFFFFF
		# add 1
		num = num + 1
		# num is now the positive version of the number
		# multiply by -1 to get a signed integer with the negative number
		num = num * -1
	return num

def readFromFile(opCode, rsBits, instructions):
	# how to read binary file and get ints
	inFile = open( sys.argv[1], 'rb' )
	# get the file length
	inFileLen = os.stat( sys.argv[1] )[6]
	inFileWords = inFileLen / 4
	address = []
	# read the words from the file
	for i in range( inFileWords ) :
		# print 'Original: ' + str(struct.unpack('>I', inFile.read(4))[0])
		instructions.append( struct.unpack('>I', inFile.read(4))[0] )
		address.append( 96 + (i*4) )
		# use I to hold the current instruction
		I = instructions[ len(instructions)-1 ]
		# get IMMEDIATE bits
		IMM = ((I << 16) & 0xFFFFFFFF ) >> 16
		IMM = imm16BitUnsignedTo32BitSignedConverter( IMM )
		#print bin(I)
		# get the opcode bits
		OP = I>>26
		opCode.append(OP)
		#print OP
		# get the RS bits
		RS = ((I<<6) & 0xFFFFFFFF) >> 27
		#print RS
		rsBits.append(RS)
		#print '----'
	inFile.close()
	return address

def initializeFuncCodes(instructions):
	funcBits = []
	for x in range(0, len(instructions)):
		funcCode = int(bin(instructions[x])[-6:], 2)
		funcBits.append(funcCode)
	return funcBits
	
def initializeOPCodes():
	instructions = [[int('100010', 2), None, 'J'], [int('100000', 2), int('001000', 2), 'JR'], [int('100100', 2), None, 'BEQ'],
					[int('100001', 2), None, 'BLTZ'], [int('100000', 2), int('100000', 2), 'ADD'], [int('101000', 2), None, 'ADDI'],
					[int('100010', 2), int('100000', 2), 'SUB'], [int('101011', 2), None, 'SW'], [int('100011', 2), None, 'LW'],
					[int('100000', 2), int('000000', 2), 'SLL'], [int('100000', 2), int('000010', 2), 'SRL'], [int('100000', 2), int('011000', 2), 'MUL'],
					[int('100000', 2), int('100100', 2), 'AND'], [int('100000', 2), int('100101', 2), 'OR'], [int('100000', 2), int('001010', 2), 'MOVZ'],
					[int('100000', 2), int('001101', 2), 'BREAK'], [int('100000', 2), int('000000', 2), 'NOP']] #nop is sll 0,0,0
					#first six bits is normally opcode, however 1-5 will be used instead
			
	return instructions

def checkOPCode(opCode, stdOPCodes):
	validity = []
	valid = False
	for x in range(0, len(opCode)):
		valid = False
		for y in range(0, len(stdOPCodes)):
			if (opCode[x] == stdOPCodes[y][0]):
				valid = True
				y = len(stdOPCodes)
		validity.append(valid)			   
	return validity
def getData(data, validity, instructions):
	location = 0
	startPt = len(validity) - 1
	while (startPt >= 0):
		if (validity[startPt]):
			#print 'Location1: ' + str(location)
			location = startPt + 1
			#print 'Location2: ' + str(location)
			startPt = -1
		startPt = startPt - 1
	returnPT = location
	#now that we have the starting location for the data, we can decide the data values
	while (location < len(validity)):
		data.append(int(instructions[location]))
		location = location + 1
	return returnPT
	
def determineInstruction(instruction, opCode, funcBits, stdOPCodes, validity, endPT, data, registers, addresses, out1, out2):
	cycle = 1
	dataStartPoint = endPT + 1
	global addressList
	addressList = addresses
	#Here comes the long list of instruction options:
	for x in range(0, endPT):
		#take care of validity first
		if (validity[x] != True):
			printInvalid(instruction[x])
		#handle ones dealing with func next
		elif (opCode[x] == int('100000', 2)):
			if (funcBits[x] == stdOPCodes[1][1]):
				x = JR(instruction[x], registers, addresses, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[4][1]):
				ADD(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[6][1]):
				SUB(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[9][1]):
				SLL(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[10][1]):
				SRL(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[11][1]):
				MUL(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[12][1]):
				AND(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[13][1]):
				OR(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[14][1]):
				MOVZ(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[15][1]):
				BREAK(instruction[x], registers, addresses[x], data, out1, out2, endPT)
			elif (funcBits[x] == stdOPCodes[16][1]):
				x = SLL(instruction[x], registers, addresses, data)
			#handle all other cases next
		else:
			if (opCode[x] == stdOPCodes[0][0]):
				x = J(instruction[x], registers, addresses, data, addresses[x],out1,out2,endPT)
			elif (opCode[x] == stdOPCodes[2][0]):
				x = BEQ(instruction[x], registers, addresses, address[x], data, out1, out2, endPT)
			elif (opCode[x] == stdOPCodes[3][0]):
				x = BLTZ(instruction[x], registers, addresses, address[x], data, out1, out2, endPT)
			elif (opCode[x] == stdOPCodes[5][0]):
				ADDI(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (opCode[x] == stdOPCodes[7][0]):
				SW(instruction[x], registers, data, addresses[x], out1, out2, endPT)
			elif (opCode[x] == stdOPCodes[8][0]):
				LW(instruction[x], registers, data, addresses[x], out1, out2, endPT)
	cycle = cycle + 1
				
	
def ADD(ins, registers, data, address, out1, out2, endPt):
	#ins is the full instruction.
	#rs is at 25-21, rt is at 20-16, rd is at 15-11
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	op = 'ADD'
	
	registers[rd] = registers[rs] + registers[rt]
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def ADDI(ins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[8:13],2)
	rt = int(str(bin(ins))[13:18],2)
	imm = int(str(bin(ins))[18:],2)
	op = 'ADDI'
	
	registers[rt] = registers[rs] + imm
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
#need to go through and add 1 to all the shit...
def SUB(ins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	op = 'SUB'
	
	registers[rd] = registers[rs] - registers[rt]
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def MUL(iins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	op = 'MUL'
	
	registers[rd] = registers[rs] * registers[rt]
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def MOVZ(ins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	op = 'MOVZ'
	
	if (int(rt) == 0):
		registers[rd] = registers[rs]
		
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def J(ins, registers, addresses, data, address, out1, out2, endPt):
	#jumps to location 4*bin
	addr = bin(ins)[7:]
	addr = int(addr, 2)
	addr = addr * 4
	op = 'J'
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
	for x in range(0, len(addresses)):
		if (int(addr) == addresses[x]):
			return x
def JR(ins, registers, addresses, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	addr = registers[rs]
	op = 'JR'
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
	for x in range(0, len(addresses)):
		if (int(addr) == addresses[x]):
			return x
		
def BEQ(ins, registers, addresses, address, data, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	imm = int(str(bin(str(bin(ins))[17:])<< 2),2)
	op = 'BEQ'
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
	if (rs == rt):
		return (imm + 4 + address)
	
def BLTZ(ins, registers, addresses, address, data, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	imm = int(str(bin(str(bin(ins))[17:])<< 2),2)
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
	if (int(rs) < 0):
		return (imm + 4 + address)
	
def SW(ins, registers, data, address, out1, out2, endPt):
	base = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	offset = int(str(bin(ins))[17:],2)
	op = 'SW'
	
	data[int(base) + int(offset)] = rt

	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def LW(ins, registers, data, address, out1, out2, endPt):
	base = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	offset = int(str(bin(ins))[17:],2)
	op = 'LW'
	
	registers[rt] = data[base + offset]
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def SLL(ins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	shamt = int(str(bin(ins))[22:27],2)
	
	if (int(rs) == 0 and int(rd) == 0 and int(rt) == 0):
		#NOP handling...
		op = 'NOP'
		
	else:
		op = 'SLL'
		registers[rd] = (int(registers[rt]) * (2^shamt))
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def SRL(ins, registers, data, address, out1, out2, endPt):
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	shamt = int(str(bin(ins))[22:27],2)
	op = 'SRL'
	
	registers[rd] = (registers[rt] >> int(shamt))
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def AND(ins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	op = 'AND'
	
	registers[rd] = int(str((bin(registers[rs]) & bin(registers[rt]))),2)
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def OR(ins, registers, data, address, out1, out2, endPt):
	rs = int(str(bin(ins))[7:12],2)
	rt = int(str(bin(ins))[12:17],2)
	rd = int(str(bin(ins))[17:22],2)
	op = 'OR'
	
	registers[rd] = int(str((bin(registers[rs]) | bin(registers[rt]))),2)
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
	
def BREAK(ins, registers, address, data, out1, out2, endPt):
	op = 'BREAK'
	
	printDis(ins, registers, op, data, address, out1, endPt)
	printSim(ins, registers, op, data, address, out2, endPt)
		
	
def initializeRegisters(registers):
	x = 0
	while (x < 32):
		registers.append(0)
		x = x + 1
		
def printDis(ins, registers, op, data, address, disOut, endPt):
	#print dis stuff that modifies registers from here
	print ''
	
def printSim(ins, registers, op, data, address, simOut, endPt):
	#print sim stuff that modifies registers from here
	simOut.write('====================\n')
	
	if (op == 'J'):
		simOut.write('cycle:' + str(cycle) + ' ' + str(address) + '\t' + str(op) + '\t#' + str((int(bin(ins)[7:],2)) * 4) + '\n\n')
	if (op == 'ADDI'):
		simOut.write('cycle:' + str(cycle) + ' ' + str(address) + '\t' + str(op) + '\t' + 'R' + str(int(str(bin(ins))[13:18],2)) + ', R' + str(int(str(bin(ins))[8:13],2)) + ', #' + str(int(str(bin(ins))[18:],2)) + '\n\n')
	
	#outside if block:
	simOut.write('registers:\nr00:\t' + str(registers[0]) + '\t' + str(registers[1]) + '\t' + str(registers[2]) + '\t' + str(registers[3]) + '\t' + str(registers[4]) + '\t' + str(registers[5]) + '\t' + str(registers[6]) + '\t' + str(registers[7]))
	simOut.write('\nr08:\t' + str(registers[8]) + '\t' + str(registers[9]) + '\t' + str(registers[10]) + '\t' + str(registers[11]) + '\t' + str(registers[12]) + '\t' + str(registers[13]) + '\t' + str(registers[14]) + '\t' + str(registers[15]))
	simOut.write('\nr16:\t' + str(registers[16]) + '\t' + str(registers[17]) + '\t' + str(registers[18]) + '\t' + str(registers[19]) + '\t' + str(registers[20]) + '\t' + str(registers[21]) + '\t' + str(registers[22]) + '\t' + str(registers[23]))
	simOut.write('\nr24:\t' + str(registers[24]) + '\t' + str(registers[25]) + '\t' + str(registers[26]) + '\t' + str(registers[27]) + '\t' + str(registers[28]) + '\t' + str(registers[29]) + '\t' + str(registers[30]) + '\t' + str(registers[31]))
	simOut.write('\n\ndata:\n')
	
	dataSize = len(data) #used for how many data points are to be printed
	listLength = int(dataSize/8) #used for how many lines needed to be printed
	if (listLength == 0):
		listLength = 1
	global addressList
	dataLocation = None
	dataLocation = endPt #used for looking up address - endpt
	infoLocation = 0 #used to track where in the data list the program is
	i = 0
	
	while (i < listLength):
		simOut.write(str(addressList[dataLocation]) + ':\t')
		j = 0
		i = i + 1
		while (j < 8):
			if (j == (dataSize - 1)):
				j = 8
			simOut.write(str(data[infoLocation]) + '\t')
			infoLocation = infoLocation + 1
			j = j + 1
		simOut.write('\n')

#needs to be written
def printInvalid(address):
	print ''

def main():
	#file io stuff:
	disOut = open(sys.argv[2] + '_dis.txt', 'w')
	simOut = open(sys.argv[2] + '_sim.txt', 'w')
	
	instructions = []
	opCode = []
	rsBits = []
	funcBits = []
	#data is initialized after the break.
	data = []
	registers = []
	initializeRegisters(registers)
	stdOPCodes = initializeOPCodes()
	addresses = readFromFile(opCode, rsBits, instructions)
	funcBits = initializeFuncCodes(instructions)
	validity = checkOPCode(opCode, stdOPCodes) #false if invalid, true if valid, makes for printing and reading easier later.
	instructionEnd = getData(data, validity, instructions)
	#checkWhatsUp(instructions, opCode, rsBits, funcBits, data, registers, addresses, validity, stdOPCodes)
	determineInstruction(instructions, opCode, funcBits, stdOPCodes, validity, instructionEnd, data, registers, addresses, disOut, simOut)
	
def checkWhatsUp(instructions, opCode, rsBits, funcBits, data, registers, addresses, validity, stdOPCodes):
	for x in range(0, len(instructions)):
		print "ins: " + str(bin(instructions[x]))
		print "op: " + str(opCode[x])
		print "rs: " + str(rsBits[x])
		print "func: " + str(funcBits[x])
		print "addresses: " + str(addresses[x])
		print "valid: " + str(validity[x]) + '\n'
	
	for x in range(0, len(data)):
		print "data: " + str(data[x])
		
	for x in range(0, len(registers)):
		print "reg: " + str(registers[x])
	
	for x in range(0, len(stdOPCodes)):
		print "sops: " + str(stdOPCodes[x])

if __name__ == "__main__":
	main()

