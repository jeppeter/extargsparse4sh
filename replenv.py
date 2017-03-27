#! /usr/bin/env python

import sys
import random
import os

RANDOM_LOWER_CHARS = 'abcdefghijklmnopqrstuvwxyz'
RANDOM_UPPER_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
RANDOM_NUMBER_CHARS = '0123456789'
RANDOM_ALPHBET_CHARS = RANDOM_LOWER_CHARS + RANDOM_UPPER_CHARS
RANDOM_FUNC_CHARS = RANDOM_ALPHBET_CHARS + RANDOM_NUMBER_CHARS

def get_random_function_name(ins,number=10):
	while True:
		s = ''
		for i in range(number):
			if i > 0:
				s += random.choice(RANDOM_FUNC_CHARS)
			else:
				s += random.choice(RANDOM_ALPHBET_CHARS)
		chgs = ins.replace(s,'',0)
		if chgs == ins:
			return s
	return None


def get_replace_string(l):
	i = 0
	newname = get_random_function_name(l)
	return '%%%s%%'%(newname) +  l.replace('\n','%%%s%%'%(newname))

def write_file(s,outfile=None):
	fout = sys.stdout
	if outfile is not None:
		fout = open(outfile,'wb')
	bmode = False
	if 'b' in fout.mode:
		bmode = True
	if sys.version[0] == '2' or not bmode:
		fout.write('s')
	else:
		fout.write(s.encode(encoding='UTF-8'))
	if fout != sys.stdout:
		fout.close()
	fout = None
	return

def read_file(infile=None):
	s = ''
	fin = sys.stdin
	if infile is not None:
		fin = open(infile,'rb')
	bmode = False
	if 'b' in fin.mode:
		bmode = True
	for l in fin:
		if sys.version[0] == '2' or not bmode:
			s += l
		else:
			s += l.decode(encoding='UTF-8')
	if fin != sys.stdin:
		fin.close()
	fin = None
	return s

def main():
	outfile = None
	infile = None
	if len(sys.argv[1:]) > 0:
		outfile = sys.argv[1]

	if len(sys.argv[1:]) > 1:
		infile = sys.argv[2]
	random.seed(os.getpid())
	s = read_file(infile)
	s = get_replace_string(s)
	write_file(s,outfile)
	return

if __name__ == '__main__':
	main()