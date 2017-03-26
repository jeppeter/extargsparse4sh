#! /usr/bin/env python

import extargsparse
import threading
import sys
import subprocess
import random

class OutputCollect(_LoggerObject):
	def __init__(self,output):
		super(OutputCollect,self).__init__()
		self.__output = output
		self.__input = []
		self.__thread =threading.Thread(target=self.input_handle,args=())
		return


    def __trans_to_string(self,s):
        if sys.version[0] == '3':
            encodetype = ['UTF-8','latin-1']
            idx=0
            while idx < len(encodetype):
                try:
                    return s.decode(encoding=encodetype[idx])
                except:
                    idx += 1
            raise Exception('not valid bytes (%s)'%(repr(s)))
        return s

	def input_handle():
        for line in iter(self.__output.readline, b''):
            transline = self.__trans_to_string(line)
            queue.put(transline)
        return


    def get_lines():
    	if self.__thread is not None:
    		self.__thread.join()
    		self.__thread = None
    		self.__output = None
    	return self.__input





shell_env_string=''
shell_verbose_mode = 0
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

def format_tab_line(s,tabs=0):
	rets = ' ' * tabs
	rets += '%s\n'%(s)
	return rets


def shell_optparse(args,validx,keycls,params):
	global shell_env_string
	if keycls.attr is None or keycls.attr.shellfunc is None:
		# this is the 
		return 0
	devnullfd = None
	if shell_verbose_mode < 3:
		devnullfd = open(os.devnul,'w')

	format_out_lines = 'shopt -s extglob\n%s\n'%(shell_env_string)
	funcname = get_random_function_name(shell_env_string)
	function_code = ''
	function_code += format_tab_line('%s()'%(funcname))
	function_code += format_tab_line('{')
	function_code += format_tab_line('local _validx="$1"',1)
	function_code += format_tab_line('shift',1)
	function_code += format_tab_line('local -a _params=($@)',1)
	if keycls.type == 'list':
		function_code += format_tab_line('unset %s'%(keycls.varname),1)
		function_code += format_tab_line('declare -g -a %s'%(keycls.varname),1)
		if args.is_access(keycls.optdest):
			idx = 0
			for c in getattr(args,keycls.optdest,[]):
				function_code += format_tab_line('%s[%d]=%s'%(keycls.varname,idx,c),1)
				idx += 1
	else:
		function_code += format_tab_line('unset %s'%(keycls.varname),1)
		function_code += format_tab_line('declare -g %s'%(keycls.varname),1)
		if args.is_access(keycls.optdest):
			if keycls.type == 'bool':
				if getattr(args,keycls.optdest,False):
					function_code += format_tab_line('%s=1'%(keycls.varname),1)
				else:
					function_code += format_tab_line('%s=0'%(keycls.varname),1)
			elif keycls.type == ''
		else:
			if keycls.type == 'bool':
				if 
	p = subprocess.Popen('/bin/bash',stdin=subprocess.PIPE,stdout=subprocess,stderr=devnullfd,shell=False)
	outhdl = OutputCollect(p.stdout)
	# now to give the 



