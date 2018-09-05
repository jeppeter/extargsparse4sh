#! /usr/bin/env python

import extargsparse
import sys
import logging
import re

def set_log_level(args):
    loglvl= logging.ERROR
    if args.verbose >= 3:
        loglvl = logging.DEBUG
    elif args.verbose >= 2:
        loglvl = logging.INFO
    elif args.verbose >= 1 :
        loglvl = logging.WARN
    # we delete old handlers ,and set new handler
    if logging.root is not None and len(logging.root.handlers) > 0:
        logging.root.handlers = []
    logging.basicConfig(level=loglvl,format='%(asctime)s:%(filename)s:%(funcName)s:%(lineno)d\t%(message)s')
    return

def testfindline_handler(args,parser):
    set_log_level(args)
    expr = re.compile(args.subnargs[0])
    idx = int(args.subnargs[1])
    sarr = re.split('\n', args.subnargs[2])
    retval = 1
    if len(sarr) > idx:
        m = expr.findall(sarr[idx])        
        if len(m) > 0:
            logging.info('find [%s] in [%s] [%s]'%(args.subnargs[0],sarr[idx],m))
            retval = 0
        else:
            logging.info('not find [%s] in [%s]'%(args.subnargs[0],sarr[idx]))
    sys.exit(retval)
    return


def main():
    commandline='''
    {
        "verbose|v" : "+",
        "testfindline<testfindline_handler>##restr num instr##"  : {
            "$" : 3
        }
    }
    '''
    parser = extargsparse.ExtArgsParse()
    parser.load_command_line_string(commandline)
    args = parser.parse_command_line(None,parser)
    raise Exception("[%s] not supported"%(args.subcommand))
    return

if __name__ == '__main__':
    main()