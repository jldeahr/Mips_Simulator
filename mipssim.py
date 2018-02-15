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

def readFromFile(opCode, rsBits, rtBits, rdBits, saBits, funcBits):
	# how to read binary file and get ints
	inFile = open( sys.argv[1], 'rb' )
	# get the file length
	inFileLen = os.stat( sys.argv[1] )[6]
	inFileWords = inFileLen / 4
	instructions = []
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
	instructions = [[2, -1, 'J'], [0, 8, 'JR'], [4, -1, 'BEQ'],
			[1, -1, 'BLTZ'], [0, 20, 'ADD'], [8, -1, 'ADDI'],
			[0, 22, 'SUB'], [43, -1, 'SW'], [23, -1, 'LW'],
			[0, 0, 'SLL'], [0, 2, 'SRL'], [0, 18, 'MUL'],
			[0, 24, 'AND'], [0, 25, 'OR'], [0, 10, 'MOVZ'],
			[13, -1, 'BREAK'], [0, 0, 'NOP']] #nop is sll 0,0,0
			#need a 40, 35, 33, 32, 43, 34, 43, 63, 0
			#first five bits is normally opcode, however 2-5 will be used instead I guess...
			
	return instructions
	
def main():
	opCode = []
	rsBits = []
	rtBits = []
	rdBits = []
	saBits = []
	funcBits = []
	stdOPCodes = initializeOPCodes()
	address = readFromFile(opCode, rsBits, rtBits, rdBits, saBits, funcBits)
	print 'My Shit: \n\n\n'
	for x in range(0, len(opCode)):
		print 'OP: ' + str(opCode[x])
		print 'RS: ' + str(rsBits[x])
		print 'Address: ' + str(address[x])
		print 'RT: ' + str(rtBits[x])
		print 'RD: ' + str(rdBits[x])
		print 'SA: ' + str(saBits[x])
		print 'FUNC: ' + str(funcBits[x])
		print '-------------------------------'

if __name__ == "__main__":
	main()

