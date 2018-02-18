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

def readFromFile(opCode, rsBits, rtBits, rdBits, saBits, funcBits, instructions):
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

def newReadFromFile(opCode, rsBits):
	inFile = open(sys.argv[1], 'rb')
	inFileLen = os.stat(sys.argv[1])[6]
	inFileWords = inFileLen / 4
	instructions = []
	address = []
	count = 0
	for i in range(inFileWords):
		instructions.append(struct.unpack('>I', inFile.read(4))[0])
		address.append(96 + (i * 4))
		I = instructions[len(instructions) - 1]
		IMM = ((I << 16) & 0xFFFFFFFF ) >> 16
		IMM = imm16BitUnsignedTo32BitSignedConverter(IMM)
		print bin(I)[2:].zfill(4)
		
	
def initializeOPCodes():
	instructions = [[100010, -1, 'J'], [100000, 001000, 'JR'], [100100, -1, 'BEQ'],
			[100001, -1, 'BLTZ'], [100000, 100000, 'ADD'], [101000, -1, 'ADDI'],
			[100000, 100010, 'SUB'], [101011, -1, 'SW'], [100011, -1, 'LW'],
			[100000, 000000, 'SLL'], [100000, 000010, 'SRL'], [100000, 011000, 'MUL'],
			[100000, 100100, 'AND'], [100000, 100101, 'OR'], [100000, 001010, 'MOVZ'],
			[100000, 001101, 'BREAK'], [100000, 000000, 'NOP']] #nop is sll 0,0,0
			#first six bits is normally opcode, however 1-5 will be used instead I guess...
			
	return instructions
	
def main():
	instructions = []
	opCode = []
	rsBits = []
	rtBits = []
	rdBits = []
	saBits = []
	funcBits = []
	#registers are initialized after the break.
	registers = []
	stdOPCodes = initializeOPCodes()
	address = readFromFile(opCode, rsBits, rtBits, rdBits, saBits, funcBits, instructions)
	print 'My Stuff: \n\n\n'
	for x in range(0, len(opCode)):
		print 'OP: ' + str(opCode[x])
		print 'RS: ' + str(rsBits[x])
		print 'Address: ' + str(address[x])
		print 'RT: ' + str(rtBits[x])
		print 'RD: ' + str(rdBits[x])
		print 'SA: ' + str(saBits[x])
		print 'FUNC: ' + str(funcBits[x])
		print '-------------------------------'

def checkOPCode():
	print "lol"
	for x in range(0, len(opCode)):
		if (#opcode starts with a 1):
			#invalid opcode
		else:
			#opcode valid
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

def addi():
	print 'Hello World!'

def sll(count):
	if (rs = 0 and rt = 0 and rd = 0):
		#handle NOP
	else:
		#handle SLL

if __name__ == "__main__":
	main()

