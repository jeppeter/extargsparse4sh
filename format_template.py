#! /usr/bin/env python

import sys
import os
import importlib
import inspect
import logging
import re
import extargsparse
import disttools



def check_method_callback(key,val,ctx):
	for k in ctx.checkmethod:
		sarr = re.split('\.',k)
		if key == sarr[0] and len(sarr) > 1:
			# now check whether it is a method
			if sarr[1] not in dir(val):
				raise Exception('%s not method in'%(k))
	return


def set_log_level(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    elif args.verbose >= 1 :
        loglvl = logging.WARN
    # we delete old handlers ,and set new handler
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return

def get_ver_tuple(ver):
	sarr = re.split('\.',ver)
	i = 0
	while i < len(sarr):
		sarr[i] = int(sarr[i])
		i += 1
	return sarr

def check_version(verleast):
	try:
		vernum = extargsparse.__version__
		vertuple = get_ver_tuple(vernum)
		leasttuple = get_ver_tuple(verleast)
		ok = True
		if vertuple[0] < leasttuple[0]:
			ok = False
		elif vertuple[0] == leasttuple[0]:
			if vertuple[1] < leasttuple[1]:
				ok = False
			elif vertuple[1] == leasttuple[1]:
				if vertuple[2] < leasttuple[2]:
					ok = False				
		if not ok :
			raise Exception('version %s < %s'%(vernum,verleast))
	except:
		raise Exception('must at lease %s version of extargsparse'%(verleast))
	return

def output_handler(args):
	# now to get the file string
	s = ''
	check_version('0.9.0')
	excludes = args.excludes
	macros = []
	for m in args.macro:
		marr = eval(m)
		if len(marr) != 2:
			raise Exception('not valid macros')
		macros.append(marr)
	repls = dict()
	for r in args.replace:
		sarr = re.split('=',r,2)
		if len(sarr) > 1:
			repls[sarr[0]] = sarr[1]
		else:
			repls[sarr[0]] = ''
	cmdchgs = args.cmdchg
	totals = ''
	for modname in args.args:
		mod = importlib.import_module(modname)
		totals += '%s'%(disttools.release_get_output(mod,excludes,macros,cmdchgs,repls,check_method_callback,args,True))
		#logging.info('totals (%s)'%(totals))

	fin = sys.stdin
	fout = sys.stdout

	if args.input is not None:
		fin = open(args.input,'r+')
	if args.output is not None:
		fout = open(args.output,'w+')

	for l in fin:
		l = l.rstrip('\r\n')
		if args.pattern is not None :
			if l == args.pattern:
				l = totals
		fout.write('%s\n'%(l))

	if fin != sys.stdin:
		fin.close()
	fin = None
	if fout != sys.stdout:
		fout.close()
	fout = None
	return

def main():
	commandline='''
	{
		"verbose|v" : "+",
		"excludes|E" : [],
		"input|i" : null,
		"pattern|P" : null,
		"output|o" : null,
		"checkmethod|c" : [],
		"macro|m" : [],
		"cmdchg|C" : [],
		"replace|r" : [],
		"$" : "*"
	}
	'''
	parser = extargsparse.ExtArgsParse()
	parser.load_command_line_string(commandline)
	args = parser.parse_command_line()
	set_log_level(args)
	output_handler(args)
	return

if __name__ == '__main__':
	main()



