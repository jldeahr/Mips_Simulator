# -*- coding: cp1252 -*-
import sys
import os
import struct

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
		print bin(I)
		# get the opcode bits
		OP = I>>26
		opCode.append(OP)
		print OP
		# get the RS bits
		RS = ((I<<6) & 0xFFFFFFFF) >> 27
		print RS
		rsBits.append(RS)
		print '----'
	inFile.close()
	return address
	
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
	
def determineInstruction(instruction, opCode, funcBits, stdOPCodes, validity, endPT, data, registers, addresses):
	#Here comes the long list of instruction options:
	for x in range(0, endPT):
		#take care of validity first
		if (!validity[x]):
			invalid(instruction[x])
		#handle ones dealing with func next
		else if (opCode[x] == int('100000', 2)):
			if (funcBits[x] == stdOPCodes[1][1]):
				x = JR(instruction[x], registers, addresses)
			else if (funcBits[x] == stdOPCodes[4][1]):
				ADD(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[6][1]):
				SUB(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[9][1]):
				SLL(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[10][1]):
				SRL(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[11][1]):
				MUL(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[12][1]):
				AND(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[13][1]):
				OR(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[14][1]):
				MOVZ(instruction[x], registers)
			else if (funcBits[x] == stdOPCodes[15][1]):
				BREAK()
			else if (funcBits[x] == stdOPCodes[16][1]):
				x = SLL(instruction[x], registers, addresses)
			#handle all other cases next
		else:
			if (opCode[x] == stdOPCodes[0][1]):
				x = J(instruction[x], registers, addresses)
			else if (opCode[x] == stdOPCodes[2][1]):
				BEQ()
			else if (opCode[x] == stdOPCodes[3][1]):
				BLTZ()
			else if (opCode[x] == stdOPCodes[5][1]):
				ADDI(instruction[x], registers)
			else if (opCode[x] == stdOPCodes[7][1]):
				SW(instruction[x], registers, data)
			else if (opCode[x] == stdOPCodes[8][1]):
				LW(instruction[x], registers, data)
				
def output():
	print ''
	
def ADD(ins, registers):
	#ins is the full instruction.
	#rs is at 25-21, rt is at 20-16, rd is at 15-11
	rs = ins[6:11]
	rt = ins[11:16]
	rd = ins[16:21]
	op = 'ADD'
	
	registers[rd] = registers[rs] + registers[rt]
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def ADDI(ins, registers):
	rs = ins[6:11]
	rt = ins[11:16]
	imm = ins[16:]
	op = 'ADDI'
	
	registers[rt] = registers[rs] + imm
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def SUB(ins, registers):
	rd = ins[16:21]
	rs = ins[6:11]
	rt = ins[11:16]
	op = 'SUB'
	
	registers[rd] = registers[rs] - registers[rt]
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def MUL(ins, registers):
	rd = ins[16:21]
	rs = ins[6:11]
	rt = ins[11:16]
	op = 'MUL'
	
	registers[rd] = registers[rs] * registers[rt]
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def MOVZ(ins, registers):
	rd = ins[16:21]
	rs = ins[6:11]
	rt = ins[11:16]
	op = 'MOVZ'
	
	if (int(rt) == 0):
		registers[rd] = registers[rs]
		
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def J(ins, registers, addresses):
	addr = ins[6:]
	op = 'J'
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
	for x in range(0, len(addresses)):
		if (int(addr) == addresses[x]):
			return x

def JR(ins, registers, addresses):
	rs = ins[6:11]
	addr = registers[rs]
	op = 'JR'
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
	for x in range(0, len(addresses)):
		if (int(addr) == addresses[x]):
			return x
		
def BEQ(ins, registers):
	rs = ins[6:11]
	rt = ins[11:16]
	op = 'BEQ'
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
	if (rs == rt):
		#come back to later when I understand better
	
	
def SW(ins, registers, data):
	base = ins[6:11]
	rt = ins[11:16]
	offset = ins[16:]
	op = 'SW'
	
	data[int(base) + int(offset)] = rt

	printDisData(ins, registers, data, op)
	printSimData(ins, registers, data, op)
	
def LW(ins, registers, data):
	base = ins[6:11]
	rt = ins[11:16]
	offset = ins[16:]
	op = 'LW'
	
	registers[rt] = data[base + offset]
	
	printDisData(ins, registers, data, op)
	printSimData(ins, registers, data, op)
	
def SLL(ins, registers):
	rs = ins[6:11]
	rd = ins[16:21]
	rt = ins[11:16]
	shamt = ins[21:26]
	
	if (int(rs) == 0 and int(rd) == 0 and int(rt) == 0):
		#NOP handling...
		op = 'NOP'
		printDis(ins, registers, op)
		printSim(ins, registers, op)
		
	else:
		op = 'SLL'
		registers[rd] = (registers[rt] << int(shamt))
	
		printDis(ins, registers, op)
		printSim(ins, registers, op)
	
def SRL(ins, registers):
	rd = ins[16:21]
	rt = ins[11:16]
	shamt = ins[21:26]
	op = 'SRL'
	
	registers[rd] = (registers[rt] >> int(shamt))
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def AND(ins, registers):
	rs = ins[6:11]
	rd = ins[16:21]
	rt = ins[11:16]
	op = 'AND'
	
	registers[rd] = (registers[rs] & registers[rt])
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def OR(ins, registers):
	rs = ins[6:11]
	rd = ins[16:21]
	rt = ins[11:16]
	op = 'OR'
	
	registers[rd] = (registers[rs] | registers[rt])
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
def BREAK(ins, registers, addresses):
	op = 'BREAK'
	
	printDis(ins, registers, op)
	printSim(ins, registers, op)
	
	return len(addresses)
	
#this function is not used, and is just storing some notes.	
def addi():
	print 'Hello World!'
	RT = ((I<<17) & 0xFFFFFFFF) >> 27
	rtBits.append(RT)
	print RT
	RD = ((I<<12) & 0xFFFFFFFF) >> 27
	rdBits.append(RD)
	print RD
	SA = ((I<<7) & 0xFFFFFFFF) >> 27
	saBits.append(SA)
	print SA
	FUNC = ((I<<1) & 0xFFFFFFFF) >> 27
	funcBits.append(FUNC)
	print FUNC

def sll(count):
	if (rs == 0 and rt == 0 and rd == 0):
		print 'NOP'
		#handle NOP
	else:
		print 'SLL'
		#handle SLL
		
def printDis():
	print ''
	
def printSim():
	print ''
	
def initializeRegisters():
	registers = []
	x = 0
	while (x < 32):
		registers.append(0)
		x = x + 1
	return registers
		
def main():
	instructions = []
	opCode = []
	rsBits = []
	funcBits = []
	#data is initialized after the break.
	data = []
	registers = initializeRegisters()
	stdOPCodes = initializeOPCodes()
	addresses = readFromFile(opCode, rsBits, instructions)
	print 'My Stuff: \n\n\n'
	for x in range(0, len(opCode)):
		print 'OP: ' + str(opCode[x])
		print 'RS: ' + str(rsBits[x])
		print 'Address: ' + str(address[x])
	validity = checkOPCode(opCode, stdOPCodes) #false if invalid, true if valid, makes for printing and reading easier later.
	instructionEnd = getData(data, validity, instructions)
	#for x in range(0, len(data)):
		#print '------------------'
		#print 'Valid' + str(validity[x])
		#print 'Data: ' + str(data[x])
	#need to initialize funcBits!!! (only for the instructions with func, else it should be null)

if __name__ == "__main__":
	main()

