#! /usr/bin/env python

import extargsparse
import threading
import sys
import subprocess
import random
import re
import os
import logging


class _LoggerObject(object):
    def __init__(self,cmdname='extargsparse'):
        self.__logger = logging.getLogger(cmdname)
        if len(self.__logger.handlers) == 0:
            loglvl = logging.WARN
            lvlname = '%s_LOGLEVEL'%(cmdname)
            lvlname = lvlname.upper()
            if lvlname in os.environ.keys():
                v = os.environ[lvlname]
                vint = 0
                try:
                    vint = int(v)
                except:
                    vint = 0
                if vint >= 4:
                    loglvl = logging.DEBUG
                elif vint >= 3:
                    loglvl = logging.INFO
            handler = logging.StreamHandler()
            fmt = "%(levelname)-8s %(message)s"
            fmtname = '%s_LOGFMT'%(cmdname)
            fmtname = fmtname.upper()
            if fmtname in os.environ.keys():
                v = os.environ[fmtname]
                if v is not None and len(v) > 0:
                    fmt = v
            formatter = logging.Formatter(fmt)
            handler.setFormatter(formatter)
            self.__logger.addHandler(handler)
            self.__logger.setLevel(loglvl)
            # we do not want any more output debug
            self.__logger.propagate = False

    def format_string(self,arr):
        s = ''
        if isinstance(arr,list):
            i = 0
            for c in arr:
                s += '[%d]%s\n'%(i,c)
                i += 1
        elif isinstance(arr,dict):
            for c in arr.keys():
                s += '%s=%s\n'%(c,arr[c])
        else:
            s += '%s'%(arr)
        return s

    def format_call_msg(self,msg,callstack):
        inmsg = ''  
        if callstack is not None:
            try:
                frame = sys._getframe(callstack)
                inmsg += '[%-10s:%-20s:%-5s] '%(frame.f_code.co_filename,frame.f_code.co_name,frame.f_lineno)
            except:
                inmsg = ''
        inmsg += msg
        return inmsg

    def info(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.info('%s'%(inmsg))

    def error(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.error('%s'%(inmsg))

    def warn(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.warn('%s'%(inmsg))

    def debug(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.debug('%s'%(inmsg))

    def fatal(self,msg,callstack=1):
        inmsg = msg
        if callstack is not None:
            inmsg = self.format_call_msg(msg,(callstack + 1))
        return self.__logger.fatal('%s'%(inmsg))

    def call_func(self,funcname,*args,**kwargs):
        mname = '__main__'
        fname = funcname
        try:
            if '.' not in funcname:
                m = importlib.import_module(mname)
            else:
                sarr = re.split('\.',funcname)
                mname = '.'.join(sarr[:-1])
                fname = sarr[-1]
                m = importlib.import_module(mname)
        except ImportError as e:
            self.error('can not load %s'%(mname))
            return None

        for d in dir(m):
            if d == fname:
                val = getattr(m,d)
                if hasattr(val,'__call__'):
                    return val(*args,**kwargs)
        self.error('can not call %s'%(funcname))
        return None


class OutputCollect(_LoggerObject):
    def __init__(self,output):
        super(OutputCollect,self).__init__()
        self.__output = output
        self.__input = []
        self.__thread =threading.Thread(target=self.input_handle,args=())
        self.__thread.start()
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

    def input_handle(self):
        for line in iter(self.__output.readline, b''):
            transline = self.__trans_to_string(line)
            self.__input.append(transline)
        return


    def get_lines(self):
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
    rets = ' ' * tabs * 4
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
    if keycls.type == 'list':
        function_code += format_tab_line('local _idx',1)
        function_code += format_tab_line('local _curelm',1)
    if keycls.type == 'list':
        function_code += format_tab_line('unset %s'%(keycls.varname),1)
        function_code += format_tab_line('declare -g -a %s'%(keycls.varname),1)
        logging.info('keycls.optdest [%s]'%(keycls.optdest))
        if getattr(args,keycls.optdest,None) is not None:
            idx = 0
            for c in getattr(args,keycls.optdest,[]):
                function_code += format_tab_line('%s[%d]=%s'%(keycls.varname,idx,c),1)
                idx += 1
    else:
        function_code += format_tab_line('unset %s'%(keycls.varname),1)
        function_code += format_tab_line('declare -g %s'%(keycls.varname),1)
        if keycls.type == 'bool':
            value = getattr(args,keycls.optdest,False)
            if value:
                function_code += format_tab_line('%s=1'%(keycls.varname),1)
            else:
                function_code += format_tab_line('%s=0'%(keycls.varname),1)
        elif keycls.type == 'string':
            value = getattr(args,keycls.optdest,None)
            if value is not None:
                function_code += format_tab_line('%s=%s'%(keycls.varname,value),1)
        elif keycls.type == 'int' or keycls.type == 'count' or keycls.type == 'float':
            value = getattr(args,keycls.optdest,None)
            if value is not None:
                function_code += format_tab_line('%s=%s'%(keycls.varname,value),1)
    function_code += format_tab_line('',1)
    function_code += format_tab_line('EXTARGSPARSE4SH_LONGOPT="%s"'%(keycls.longopt),1)
    if keycls.shortopt is not None:
        function_code += format_tab_line('EXTARGSPARSE4SH_SHORTOPT="%s"'%(keycls.shortopt),1)
    else:
        function_code += format_tab_line('EXTARGSPARSE4SH_SHORTOPT=',1)

    callstr = '%s "%s"'%(keycls.attr.shellfunc,validx)
    for c in params:
        callstr += ' "%s"'%(c)
    function_code += format_tab_line(callstr,1)

    # now we should make sure the test case
    if keycls.type == 'list':
        function_code += format_tab_line('_idx=0',1)
        function_code += format_tab_line('for _curelm in "${%s[@]}"'%(keycls.varname),1)
        function_code += format_tab_line('do',1)
        function_code += format_tab_line('echo "%s[$_idx]=$_curelm"'%(keycls.varname),2)
        function_code += format_tab_line('_idx=`expr $_idx \+ 1`',2)
        function_code += format_tab_line('done',1)
    else:
        function_code += format_tab_line('%s=$%s'%(keycls.varname,keycls.varname),1)
    function_code += format_tab_line('echo ""',1)
    function_code += format_tab_line('return',1)
    function_code += format_tab_line('}',0)

    logging.debug('function_code (%s)'%(function_code))

    p = subprocess.Popen('/bin/bash',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=devnullfd,shell=False)  
    outhdl = OutputCollect(p.stdout)
    # now to give the environment
    if sys.version[0] == '2':
        p.stdin.write(format_out_lines)
        p.stdin.write(function_code)
        p.stdin.write('%s'%(funcname))
        p.stdin.write('declare')
    else:
        p.stdin.write(bytes(format_out_lines,'UTF-8'))
        p.stdin.write(bytes(function_code,'UTF-8'))
        p.stdin.write(bytes('%s\n'%(funcname),'UTF-8'))
        p.stdin.write(bytes('declare\n','UTF-8'))
    p.stdin.close()
    # we get lines
    outlines = outhdl.get_lines()
    outhdl = None
    if devnullfd is not None:
        devnullfd.close()
    devnullfd = None

    # now pass the 
    idx = 0
    numret = 0
    intexpr = re.compile('^(\d+)$')
    listexpr = re.compile('%s\[([\d]+)\]=(.*)'%(keycls.varname))
    intvarexpr = re.compile('%s=([\d]+)'%(keycls.varname))
    floatvarexpr = re.compile('%s=([\d]+(\.[\d]+)?)'%(keycls.varname))
    boolvarexpr = re.compile('%s=([01])'%(keycls.varname))
    strvarexpr = re.compile('%s=(.*)'%(keycls.varname))
    envstarted = 0
    argsvalue = None
    if keycls.type == 'list':
        argsvalue = []
    for l in outlines:  
        idx += 1
        if idx == 1:
            if intexpr.match(l.rstrip('\r\n')):
                numret = int(l.rstrip('\r\n'))
            elif l.rstrip('\r\n') == 'error':
                raise Exception('get error')
        elif envstarted == 0 and l.rstrip('\r\n') == '':
            shell_env_string = ''
            envstarted = 1
        elif envstarted == 0:
            # it is the value one
            startename = '%s'%(keycls.varname)
            if l.startswith(startename):
                if keycls.type == 'list':
                    m = listexpr.findall(l.rstrip('\r\n'))
                    if m is not None and len(m) > 0 and len(m[0]) == 2:
                        listidx = int(m[0][0])
                        v = m[0][1]
                        if listidx == len(argsvalue):
                            argsvalue.append(v)
                        else:
                            logging.warn('[%s] not valid name'%(l.rstrip('\r\n')))
                    else:
                        logging.warn('[%s] not valid for list'%(l.rstrip('\r\n')))
                elif keycls.type == 'string' or (keycls.type == 'unicode' and sys.version[0] == '2'):
                    m = strvarexpr.findall(l.rstrip('\r\n'))
                    if m is not None and argsvalue is None:
                        argsvalue = m[0]
                    else:
                        logging.warn('[%s] not valid for string'%(l.rstrip('\r\n')))
                elif keycls.type == 'count' or keycls.type == 'int' or keycls.type == 'long':
                    m = intvarexpr.findall(l.rstrip('\r\n'))
                    if m is not None and argsvalue is None:
                        argsvalue = int(m[0])
                    else:
                        logging.warn('[%s] not valid for %s'%(l.rstrip('\r\n'),keycls.type))
                elif keycls.type == 'float':
                    m = floatvarexpr.findall(l.rstrip('\r\n'))
                    if m is not None and len(m[0]) > 0 and argsvalue is None:
                        argsvalue = float(m[0][0])
                    else:
                        logging.warn('[%s] not valid for %s'%(l.rstrip('\r\n'),keycls.type))
                elif keycls.type == 'bool':
                    m = boolvarexpr.findall(l.rstrip('\r\n'))
                    if m is not None and len(m) > 0 and argsvalue is None:
                        if int(m[0]) > 0:
                            argsvalue = True
                        else:
                            argsvalue = False
                    else:
                        logging.warn('[%s] not valid for %s'%(l.rstrip('\r\n'),keycls.type))
                else:
                    logging.warn('unknown type [%s]'%(keycls.type))

        else:
            # that is the shell options
            shell_env_string += l
    logging.info('[%s]=(%s)'%(keycls.optdest,argsvalue))
    logging.info('shell_env_string (%s)'%(shell_env_string))
    setattr(args,keycls.optdest,argsvalue)
    return numret

def get_env_string(l):
    s = ''
    if l is not None and len(l) > 0:
        if l[0] == r'%':
            firstdollar = 0
            secdollar = -1
            idx = 1
            while idx < len(l):
                if l[idx] == r'%':
                    secdollar = idx
                    break
                idx += 1
            if secdollar > 0:
                repls = l[:(secdollar+1)]
                s = l.replace(repls,'\n')
    return s

def read_file(infile=None):
    s = ''
    fin = sys.stdin
    if infile is not None:
        fin = open(infile,'rb')
    bmode = False
    if 'b' in fin.mode:
        bmode = True
    logging.info('read [%s]'%(infile))
    for l in fin:
        logging.info('in [%d]'%(len(l)))
        if sys.version[0] == '2' or not bmode:
            s += l
        else:
            s += l.decode(encoding='UTF-8')
    if fin != sys.stdin:
        fin.close()
    fin = None
    return s

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



def main():
    global shell_env_string
    global shell_verbose_mode
    commandline='''
    {
        "verbose|v" : "+",
        "longopt|l" : null,
        "shortopt|s" : null,
        "varname|V" : null,
        "optdest|o" : null,
        "envfile|e" : null,
        "validx|i" : 0,
        "shellfunc|S" : null,
        "type|t" : null,
        "$" : "*"
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line()
    set_log_level(args)
    logging.info('args (%s)'%(args))
    argsopt = extargsparse.ExtArgsOptions()
    keycls = extargsparse.ExtArgsOptions()
    keycls.type = args.type
    keycls.longopt = args.longopt
    keycls.optdest = args.optdest
    keycls.shortopt = args.shortopt
    keycls.varname = args.varname
    keycls.attr = extargsparse.ExtArgsOptions()
    keycls.attr.optparse = 'shell_optparse'
    keycls.attr.shellfunc = args.shellfunc
    shell_env_string = get_env_string(read_file(args.envfile))
    shell_verbose_mode = args.verbose
    random.seed(os.getpid())
    logging.info('keycls [%s]'%(keycls))
    idx = args.validx
    while (idx ) < len(args.args):
        nret = shell_optparse(argsopt,idx,keycls,args.args)
        idx += nret
    return

if __name__ == '__main__':
    main()