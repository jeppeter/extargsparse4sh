import argparse
import os
import sys
import json
import logging
import re
import importlib
if sys.version[0] == '2':
    import StringIO
else:
    import io as StringIO


class TypeClass(object):
    def __init__(self,v):
        self.__type = type(v)
        if isinstance(v,str):
            self.__type = 'string'
        elif isinstance(v,dict):
            self.__type = 'dict'
        elif isinstance(v,list):
            self.__type = 'list'
        elif isinstance(v,bool):
            self.__type = 'bool'
        elif isinstance (v,int):
            self.__type = 'int'
        elif isinstance(v ,float):
            self.__type = 'float'
        elif sys.version[0] == '2' and isinstance(v,unicode):
            self.__type = 'unicode'
        elif v is None:
            # we use default string
            self.__type = 'string'
        elif isinstance(v,long):
            self.__type = 'long'
        else:
            raise Exception('(%s)unknown type (%s)'%(v,type(v)))
        return

    def get_type(self):
        return self.__type

    def __str__(self):
        return self.__type

    def __repr__(self):
        return self.__type

class Utf8Encode:
    def __dict_utf8(self,val):
        newdict =dict()
        for k in val.keys():
            newk = self.__encode_utf8(k)
            newv = self.__encode_utf8(val[k])
            newdict[newk] = newv
        return newdict

    def __list_utf8(self,val):
        newlist = []
        for k in val:
            newk = self.__encode_utf8(k)
            newlist.append(newk)
        return newlist

    def __encode_utf8(self,val):
        retval = val

        if sys.version[0]=='2' and isinstance(val,unicode):
            retval = val.encode('utf8')
        elif isinstance(val,dict):
            retval = self.__dict_utf8(val)
        elif isinstance(val,list):
            retval = self.__list_utf8(val)
        return retval

    def __init__(self,val):
        self.__val = self.__encode_utf8(val)
        return

    def __str__(self):
        return self.__val

    def __repr__(self):
        return self.__val
    def get_val(self):
        return self.__val

class ExtKeyParse:
    flagspecial = ['value','prefix']
    flagwords = ['flagname','helpinfo','shortflag','nargs','varname']
    cmdwords = ['cmdname','function','helpinfo']
    otherwords = ['origkey','iscmd','isflag','type']
    formwords = ['longopt','shortopt','optdest']
    def __reset(self):
        self.__value = None
        self.__prefix = ''
        self.__flagname = None
        self.__helpinfo = None
        self.__shortflag = None
        self.__nargs = None
        self.__varname = None
        self.__cmdname = None
        self.__function = None
        self.__origkey = None
        self.__iscmd = None
        self.__isflag = None
        self.__type = None
        return

    def __validate(self):
        if self.__isflag:
            assert(not self.__iscmd )
            if self.__function is not None:
                raise Exception('(%s) can not accept function'%(self.__origkey))
            if self.__type == 'dict' and self.__flagname:
                # in the prefix we will get dict ok
                raise Exception('(%s) flag can not accept dict'%(self.__origkey))
            if self.__type != str(TypeClass(self.__value)) and self.__type != 'count':
                raise Exception('(%s) value (%s) not match type (%s)'%(self.__origkey,self.__value,self.__type))
            if self.__flagname is None :
                # we should test if the validate flag
                if self.__prefix is None:
                    raise Exception('(%s) should at least for prefix'%(self.__origkey))
                self.__type = 'prefix'
                if str(TypeClass(self.__value)) != 'dict':
                    raise Exception('(%s) should used dict to make prefix'%(self.__origkey))
                if self.__helpinfo :
                    raise Exception('(%s) should not have help info'%(self.__origkey))
                if self.__shortflag:
                    raise Exception('(%s) should not set shortflag'%(self.__origkey))
            elif self.__flagname == '$':
                # this is args for handle
                self.__type = 'args'
                if self.__shortflag :
                    raise Exception('(%s) can not set shortflag for args'%(self.__origkey))
            else:
                if len(self.__flagname) <= 0:
                    raise Exception('(%s) can not accept (%s)short flag in flagname'%(self.__origkey,self.__flagname))
            if self.__shortflag:
                if len(self.__shortflag) > 1:
                    raise Exception('(%s) can not accept (%s) for shortflag'%(self.__origkey,self.__shortflag))

            if self.__type == 'bool':
                # this should be zero
                if self.__nargs is not None and self.__nargs != 0:
                    raise Exception('bool type (%s) can not accept 0 nargs'%(self.__origkey))
                self.__nargs = 0
            elif self.__type != 'prefix' and self.__flagname != '$' and self.__type != 'count':
                if self.__flagname != '$' and self.__nargs != 1 and self.__nargs is not None:
                    raise Exception('(%s)only $ can accept nargs option'%(self.__origkey))
                self.__nargs = 1
            else:
                if self.__flagname == '$' and self.__nargs is None:
                    # we make sure any args to have
                    self.__nargs = '*'
        else:
            if self.__cmdname is None or len(self.__cmdname) == 0 :
                raise Exception('(%s) not set cmdname'%(self.__origkey))
            if self.__shortflag :
                raise Exception('(%s) has shortflag (%s)'%(self.__origkey,self.__shortflag))
            if self.__nargs:
                raise Exception('(%s) has nargs (%s)'%(self.__origkey,self.__nargs))
            if self.__type != 'dict':
                raise Exception('(%s) command must be dict'%(self.__origkey))
            self.__prefix = self.__cmdname
            self.__type = 'command'
        if self.__isflag and self.__varname is None and self.__flagname is not None:
            if self.__flagname != '$':
                self.__varname = self.optdest
            else:
                if len(self.__prefix) > 0:
                    self.__varname = 'subnargs'
                else:
                    self.__varname = 'args'
        return

    def __set_flag(self,prefix,key,value):
        self.__isflag = True
        self.__iscmd = False
        self.__origkey = key
        if 'value' not in value.keys():
            self.__value = None
            self.__type = 'string'

        for k in value.keys():
            if k in self.__class__.flagwords:
                innerkey = self.__get_inner_name(k)
                if self.__dict__[innerkey] and self.__dict__[innerkey] != value[k]:
                    raise Exception('set (%s) for not equal value (%s) (%s)'%(k,self.__dict__[innerkey],value[k]))
                if not (str(TypeClass(value[k])) == 'string' or str(TypeClass(value[k])) == 'int' or str(TypeClass(value[k])== 'unicode')):
                    raise Exception('(%s)(%s)(%s) can not take other than int or string (%s)'%(self.__origkey,k,value[k],TypeClass(value[k])))              
                self.__dict__[innerkey] = value[k]
            elif k in self.__class__.flagspecial:
                innerkey = self.__get_inner_name(k)
                if k == 'prefix':
                    if str(TypeClass(value[k])) != 'string' or value[k] is None:
                        raise Exception('(%s) prefix not string or None'%(self.__origkey))
                    newprefix = ''
                    if prefix and len(prefix):
                        newprefix += '%s_'%(prefix)
                    newprefix += value[k]
                    self.__prefix = newprefix
                elif k == 'value':
                    if str(TypeClass(value[k])) == 'dict':
                        raise Exception('(%s)(%s) can not accept dict'%(self.__origkey,k))
                    self.__value = value[k]
                    self.__type = str(TypeClass(value[k]))
                else:
                    self.__dict__[innerkey] = value[k]                  
        if len(self.__prefix) == 0  and len(prefix) > 0:
            self.__prefix = prefix
        return


    def __parse(self,prefix,key,value,isflag):
        flagmod = False
        cmdmod = False
        flags = None
        self.__origkey = key
        if '$' in self.__origkey:
            if self.__origkey[0] != '$':
                raise Exception('(%s) not right format for ($)'%(self.__origkey))
            ok = 1
            try:
                idx = self.__origkey.index('$',1)
                ok = 0
            except:
                pass
            if ok == 0 :
                raise Exception('(%s) has ($) more than one'%(self.__origkey))
        if isflag :
            m = self.__flagexpr.findall(self.__origkey)
            if m and len(m)>0:
                flags = m[0]
            if flags is None :
                m = self.__mustflagexpr.findall(self.__origkey)
                if m and len(m) > 0:
                    flags = m[0]
            if flags is None and self.__origkey[0] == '$':
                self.__flagname = '$'
                flagmod = True
            if flags is not None:
                if '|' in flags:
                    sarr = re.split('\|',flags)
                    if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
                        raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
                    self.__flagname = sarr[0]
                    self.__shortflag = sarr[1]
                else:
                    self.__flagname = flags
                flagmod = True
        else:
            m = self.__mustflagexpr.findall(self.__origkey)
            if m and len(m) > 0:
                flags = m[0]
                if '|' in flags:
                    sarr = re.split('\|',flags)
                    if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
                        raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
                    self.__flagname = sarr[0]
                    self.__shortflag = sarr[1]
                else:
                    if len(flags) <= 1 :
                        raise Exception('(%s) flag must have long opt'%(self.__origkey))
                    self.__flagname = flags
                flagmod = True
            elif self.__origkey[0] == '$':
                # it means the origin is '$'
                self.__flagname = '$'
                flagmod = True
            m = self.__cmdexpr.findall(self.__origkey)
            if m and len(m) > 0:
                assert(not flagmod)
                if '|' in m[0]:
                    flags = m[0]
                    if '|' in flags:
                        sarr = re.split('\|',flags)
                        if len(sarr) > 2 or len(sarr[1]) != 1 or len(sarr[0]) <= 1 :
                            raise Exception('(%s) (%s)flag only accept (longop|l) format'%(self.__origkey,flags))
                        self.__flagname = sarr[0]
                        self.__shortflag = sarr[1]
                    else:
                        assert( False )
                    flagmod = True
                else:
                    self.__cmdname = m[0]
                    cmdmod = True

        m = self.__helpexpr.findall(self.__origkey)
        if m and len(m) > 0:
            self.__helpinfo = m[0]
        newprefix = ''
        if prefix and len(prefix) > 0 :
            newprefix = '%s_'%(prefix)
        m = self.__prefixexpr.findall(self.__origkey)
        if m and len(m) > 0:
            newprefix += m[0]
            self.__prefix = newprefix
        else:
            if len(prefix) > 0:
                self.__prefix = prefix
        if flagmod :
            self.__isflag = True
            self.__iscmd = False
        if cmdmod :
            self.__iscmd = True
            self.__isflag = False
        if  not flagmod and not cmdmod :
            self.__isflag = True
            self.__iscmd = False
        self.__value = value
        self.__type = str(TypeClass(value))
        if cmdmod and self.__type != 'dict':
            flagmod = True
            cmdmod = False
            self.__isflag = True
            self.__iscmd = False
            self.__flagname = self.__cmdname
            self.__cmdname = None

        if self.__isflag and self.__type == 'string' and self.__value == '+' and self.__flagname != '$':
            self.__value = 0
            self.__type = 'count'
            self.__nargs = 0

        if self.__isflag and self.__flagname == '$' and self.__type != 'dict':
            if not ((self.__type == 'string' and (self.__value  in '+?*' )) or self.__type == 'int') :
                raise Exception('(%s)(%s)(%s) for $ should option dict set opt or +?* specialcase or type int'%(prefix,self.__origkey,self.__value))
            else:
                self.__nargs = self.__value
                self.__value = None
                self.__type = 'string'
        if self.__isflag and self.__type == 'dict' and self.__flagname:
            self.__set_flag(prefix,key,value)

        # we put here for the lastest function
        m = self.__funcexpr.findall(self.__origkey)
        if m and len(m):
            if flagmod:
                # we should put the flag mode
                self.__varname = m[0]
            else:
                self.__function = m[0]
        self.__validate()
        return

    def __get_inner_name(self,name):
        innerkeyname = name
        if (name in self.__class__.flagwords) or \
            (name in self.__class__.flagspecial) or \
           (name in self.__class__.cmdwords) or \
           (name in self.__class__.otherwords):
            innerkeyname = '_%s__%s'%(self.__class__.__name__,name)
        return innerkeyname



    def __init__(self,prefix,key,value,isflag=False):
        key = Utf8Encode(key).get_val()
        prefix = Utf8Encode(prefix).get_val()
        value = Utf8Encode(value).get_val()

        self.__reset()
        self.__helpexpr = re.compile('##([^#]+)##$',re.I)
        self.__cmdexpr = re.compile('^([^\#\<\>\+\$]+)',re.I)
        self.__prefixexpr = re.compile('\+([^\+\#\<\>\|\$ \t]+)',re.I)
        self.__funcexpr = re.compile('<([^\<\>\#\$\| \t]+)>',re.I)
        self.__flagexpr = re.compile('^([^\<\>\#\+\$ \t]+)',re.I)
        self.__mustflagexpr = re.compile('^\$([^\$\+\#\<\>]+)',re.I)
        self.__origkey = key
        if isinstance(key,dict):
            raise Exception('can not accept key for dict type')
        else:

            self.__parse(prefix,key,value,isflag)
        return

    def __form_word(self,keyname):
        if keyname == 'longopt':
            if not self.__isflag or self.__flagname is None or self.__type == 'args':
                raise Exception('can not set (%s) longopt'%(self.__origkey))
            longopt = '--'
            if self.__type == 'bool' and self.__value :
                # we set no
                longopt += 'no-'
            if len(self.__prefix) > 0 :
                longopt += '%s_'%(self.__prefix)
            longopt += self.__flagname
            longopt = longopt.lower()
            longopt = longopt.replace('_','-')
            return longopt
        elif keyname == 'shortopt':
            if not self.__isflag or self.__flagname is None or self.__type == 'args':
                raise Exception('can not set (%s) shortopt'%(self.__origkey))
            shortopt = None
            if self.__shortflag:
                shortopt = '-%s'%(self.__shortflag)
            return shortopt
        elif keyname == 'optdest':
            if not self.__isflag or self.__flagname is None or self.__type == 'args':
                raise Exception('can not set (%s) optdest'%(self.__origkey))
            optdest = ''
            if len(self.__prefix) > 0:
                optdest += '%s_'%(self.__prefix)
            optdest += self.__flagname
            optdest = optdest
            optdest = optdest.lower()
            optdest = optdest.replace('-','_')
            return optdest

        assert(False)
        return



    def __getattr__(self,keyname):
        if keyname in self.__class__.formwords:
            return self.__form_word(keyname)
        innername = self.__get_inner_name(keyname)
        return self.__dict__[innername]

    def __setattr__(self,keyname,value):
        if (keyname in self.__class__.flagspecial) or \
            (keyname in self.__class__.flagwords) or \
            (keyname in self.__class__.cmdwords) or \
            (keyname in self.__class__.otherwords):
            raise AttributeError
        self.__dict__[keyname] = value
        return

    def __format_string(self):
        s = '{'
        s += '<type:%s>'%(self.__type)
        if self.__iscmd:
            s += '<cmdname:%s>'%(self.__cmdname)
            if self.__function:
                s += '<function:%s>'%(self.__function)
            if self.__helpinfo:
                s += '<helpinfo:%s>'%(self.__helpinfo)
            if len(self.__prefix) > 0:
                s += '<prefix:%s>'%(self.__prefix)
        if self.__isflag:
            if self.__flagname:
                s += '<flagname:%s>'%(self.__flagname)
            if self.__shortflag:
                s += '<shortflag:%s>'%(self.__shortflag)
            if len(self.__prefix) > 0 :
                s += '<prefix:%s>'%(self.__prefix)
            if self.__nargs is not None  :
                s += '<nargs:%s>'%(self.__nargs)
            if self.__varname is not None:
                s += '<varname:%s>'%(self.__varname)
            if self.__value is not None:
                s += '<value:%s>'%(self.__value)
        s += '}'
        return s

    def __str__(self):
        return self.__format_string()
    def __repr__(self):
        return self.__format_string()

    def change_to_flag(self):
        if not self.__iscmd or self.__isflag:
            raise Exception('(%s) not cmd to change'%(self.__origkey))
        if self.__function is not None:
            self.__varname = self.__function
            self.__function = None
        assert(self.__flagname is None)
        assert(self.__shortflag is None)
        assert(self.__cmdname is not None)
        self.__flagname = self.__cmdname
        self.__cmdname = None
        self.__iscmd = False
        self.__isflag = True
        self.__validate()
        return



COMMAND_SET = 10
SUB_COMMAND_JSON_SET = 20
COMMAND_JSON_SET = 30
ENVIRONMENT_SET = 40
ENV_SUB_COMMAND_JSON_SET = 50
ENV_COMMAND_JSON_SET = 60
DEFAULT_SET = 70

extargs_shell_out_mode=0

def set_attr_args(self,args,prefix):
    if not issubclass(args.__class__,argparse.Namespace):
        raise Exception('second args not valid argparse.Namespace subclass')
    for p in vars(args).keys():
        if len(prefix) == 0 or p.startswith('%s_'%(prefix)):
            setattr(self,p,getattr(args,p))
    return

def call_func_args(funcname,args,Context):
    global extargs_shell_out_mode
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
        sys.stderr.write('can not load %s\n'%(mname))
        return args

    for d in dir(m):
        if d == fname:
            val = getattr(m,d)
            if hasattr(val,'__call__'):
                val(args,Context)
                return args
    if extargs_shell_out_mode == 0:
        sys.stderr.write('can not call %s\n'%(funcname))
    return args




class IntAction(argparse.Action):
     def __init__(self, option_strings, dest, nargs=1, **kwargs):
        super(IntAction,self).__init__(option_strings, dest, **kwargs)
        return

     def __call__(self, parser, namespace, values, option_string=None):
        try:
            if values.startswith('x') or values.startswith('0x'):
                intval = int(values,16)
            else:
                intval = int(values)
        except:
            raise Exception('%s not valid number'%(values))
        setattr(namespace,self.dest,intval)
        return


class _ParserCompact(object):
    pass

class ArrayAction(argparse.Action):
     def __init__(self, option_strings, dest, nargs=1, **kwargs):
        argparse.Action.__init__(self,option_strings, dest, **kwargs)
        return

     def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace,self.dest) is None:
            setattr(namespace,self.dest,[])
        lists = getattr(namespace,self.dest)
        if values not in lists:
            lists.append(values)
        setattr(namespace,self.dest,lists)
        return

class FloatAction(argparse.Action):
     def __init__(self, option_strings, dest, nargs=1, **kwargs):
        super(IntAction,self).__init__(option_strings, dest, **kwargs)
        return

     def __call__(self, parser, namespace, values, option_string=None):
        try:
            fval = float(values)
        except:
            raise Exception('%s not valid number'%(values))
        setattr(namespace,self.dest,fval)
        return



class ExtArgsParse(argparse.ArgumentParser):
    reserved_args = ['subcommand','subnargs','json','nargs','extargs']
    priority_args = [SUB_COMMAND_JSON_SET,COMMAND_JSON_SET,ENVIRONMENT_SET,ENV_SUB_COMMAND_JSON_SET,ENV_COMMAND_JSON_SET]
    def error(self,message):
        global extargs_shell_out_mode
        if extargs_shell_out_mode == 0:
            s = 'parse command error\n'
            s += '    %s'%(message)
            sys.stderr.write('%s'%(s))
        else:
            s = ''
            s += 'cat >&2 <<EXTARGSEOF\n'
            s += 'parse command error\n    %s\n'%(message)
            s += 'EXTARGSEOF\n'
            s += 'exit 3\n'
            sys.stdout.write('%s'%(s))
        sys.exit(3)
        return
    def __get_help_info(self,keycls):
        helpinfo = ''
        if keycls.type == 'bool':
            if keycls.value :
                helpinfo += '%s set false default(True)'%(keycls.optdest)
            else:
                helpinfo += '%s set true default(False)'%(keycls.optdest)
        elif keycls.type == 'string' and keycls.value == '+':
            if keycls.isflag:
                helpinfo += '%s inc'%(keycls.optdest)
            else:
                raise Exception('cmd(%s) can not set value(%s)'%(keycls.cmdname,keycls.value))
        else:
            if keycls.isflag:
                helpinfo += '%s set default(%s)'%(keycls.optdest,keycls.value)
            else:
                helpinfo += '%s command exec'%(keycls.cmdname)
        if keycls.helpinfo:
            helpinfo = keycls.helpinfo
        return helpinfo

    def __check_flag_insert(self,keycls,curparser=None):
        if curparser :
            for k in curparser.flags:
                if k.flagname != '$' and keycls.flagname != '$':
                    if k.optdest == keycls.optdest:
                        return False
                elif k.flagname == keycls.flagname:
                    return False
            curparser.flags.append(keycls)
        else:
            for k in self.__flags:
                if (k.flagname != '$') and (keycls.flagname != '$'):
                    if k.optdest == keycls.optdest:
                        return False
                elif k.flagname == keycls.flagname:
                    return False
            self.__flags.append(keycls)
        return True

    def __check_flag_insert_mustsucc(self,keycls,curparser=None):
        valid = self.__check_flag_insert(keycls,curparser)
        if not valid:
            cmdname = 'main'
            if curparser:
                cmdname = curparser.cmdname
            raise Exception('(%s) already in command(%s)'%(keycls.flagname,cmdname))
        return

    def __load_command_line_string(self,prefix,keycls,curparser=None):
        self.__check_flag_insert_mustsucc(keycls,curparser)
        longopt = keycls.longopt
        shortopt = keycls.shortopt
        optdest = keycls.optdest
        putparser = self
        if curparser is not None:
            putparser = curparser.parser
        helpinfo = self.__get_help_info(keycls)
        if shortopt:
            putparser.add_argument(shortopt,longopt,dest=optdest,default=None,help=helpinfo)
        else:
            putparser.add_argument(longopt,dest=optdest,default=None,help=helpinfo)
        return True

    def __load_command_line_count(self,prefix,keycls,curparser=None):
        self.__check_flag_insert_mustsucc(keycls,curparser)
        longopt = keycls.longopt
        shortopt = keycls.shortopt
        optdest = keycls.optdest
        putparser = self
        if curparser is not None:
            putparser = curparser.parser
        helpinfo = self.__get_help_info(keycls)
        if shortopt:
            putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='count',help=helpinfo)
        else:
            putparser.add_argument(longopt,dest=optdest,default=None,action='count',help=helpinfo)
        return True


    def __load_command_line_int(self,prefix,keycls,curparser=None):
        self.__check_flag_insert_mustsucc(keycls,curparser)
        longopt = keycls.longopt
        shortopt = keycls.shortopt
        optdest = keycls.optdest
        helpinfo = self.__get_help_info(keycls)
        putparser = self
        if curparser is not None:
            putparser = curparser.parser

        if shortopt :
            putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=IntAction,help=helpinfo)
        else:
            putparser.add_argument(longopt,dest=optdest,default=None,action=IntAction,help=helpinfo)
        return True


    def __load_command_line_float(self,prefix,keycls,curparser=None):
        self.__check_flag_insert_mustsucc(keycls,curparser)
        longopt = keycls.longopt
        shortopt = keycls.shortopt
        optdest = keycls.optdest
        helpinfo = self.__get_help_info(keycls)
        putparser = self
        if curparser is not None:
            putparser = curparser.parser

        if shortopt :
            putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=FloatAction,help=helpinfo)
        else:
            putparser.add_argument(longopt,dest=optdest,default=None,action=FloatAction,help=helpinfo)
        return True

    def __load_command_line_list(self,prefix,keycls,curparser=None):
        self.__check_flag_insert_mustsucc(keycls,curparser)
        longopt = keycls.longopt
        shortopt = keycls.shortopt
        optdest = keycls.optdest
        helpinfo = self.__get_help_info(keycls)
        putparser = self
        if curparser is not None:
            putparser = curparser.parser
        if shortopt :
            putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action=ArrayAction,help=helpinfo)
        else:
            putparser.add_argument(longopt,dest=optdest,default=None,action=ArrayAction,help=helpinfo)
        return True

    def __load_command_line_bool(self,prefix,keycls,curparser=None):
        self.__check_flag_insert_mustsucc(keycls,curparser)
        longopt = keycls.longopt
        shortopt = keycls.shortopt
        optdest = keycls.optdest
        helpinfo = self.__get_help_info(keycls)
        putparser = self
        if curparser is not None:
            putparser = curparser.parser
        if keycls.value :
            if shortopt :
                putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='store_false',help=helpinfo)
            else:
                putparser.add_argument(longopt,dest=optdest,default=None,action='store_false',help=helpinfo)
        else:
            if shortopt :
                putparser.add_argument(shortopt,longopt,dest=optdest,default=None,action='store_true',help=helpinfo)
            else:
                putparser.add_argument(longopt,dest=optdest,default=None,action='store_true',help=helpinfo)
        return True

    def __load_command_line_args(self,prefix,keycls,curparser=None):
        valid = self.__check_flag_insert(keycls,curparser)
        if not valid :
            return False
        putparser = self
        optdest = 'args'
        if curparser:
            putparser = curparser.parser
            optdest = 'subnargs'
        helpinfo = '%s set '%(optdest)
        if keycls.helpinfo:
            helpinfo = keycls.helpinfo
        if keycls.nargs != 0:
            #logging.info('optdest %s'%(optdest))
            putparser.add_argument(optdest,metavar=optdest,type=str,nargs=keycls.nargs,help=helpinfo)
        return True

    def __load_command_line_jsonfile(self,keycls,curparser=None):
        valid = self.__check_flag_insert(keycls,curparser)
        if not valid:
            return False
        putparser = self
        if curparser :
            putparser = curparser.parser
        longopt = keycls.longopt
        optdest = keycls.optdest
        helpinfo = self.__get_help_info(keycls)
        putparser.add_argument(longopt,dest=optdest,action='store',default=None,help=helpinfo)
        return True

    def __load_command_line_json_added(self,curparser=None):
        prefix = ''
        key = 'json## json input file to get the value set ##'
        value = None
        if curparser :
            prefix = curparser.cmdname
        keycls = ExtKeyParse(prefix,key,value,True)
        return self.__load_command_line_jsonfile(keycls,curparser)


    def __init__(self,prog=None,usage=None,description=None,epilog=None,version=None,
                 parents=[],formatter_class=argparse.HelpFormatter,prefix_chars='-',
                 fromfile_prefix_chars=None,argument_default=None,
                 conflict_handler='error',add_help=True,priority=[SUB_COMMAND_JSON_SET,COMMAND_JSON_SET,ENVIRONMENT_SET,ENV_SUB_COMMAND_JSON_SET,ENV_COMMAND_JSON_SET]):
        if sys.version[0] == '2':
            super(ExtArgsParse,self).__init__(prog,usage,description,epilog,version,parents,formatter_class,prefix_chars,
                fromfile_prefix_chars,argument_default,conflict_handler,add_help)
        else:
            super(ExtArgsParse,self).__init__(prog,usage,description,epilog,parents,formatter_class,prefix_chars,
                fromfile_prefix_chars,argument_default,conflict_handler,add_help)                
        self.__logger = logging.getLogger('extargsparse')
        if len(self.__logger.handlers) == 0:
            loglvl = logging.WARN
            if 'EXTARGSPARSE_LOGLEVEL' in os.environ.keys():
                v = os.environ['EXTARGSPARSE_LOGLEVEL']
                if v == 'DEBUG':
                    loglvl = logging.DEBUG
                elif v == 'INFO':
                    loglvl = logging.INFO
            handler = logging.StreamHandler()
            fmt = "%(levelname)-8s [%(filename)-10s:%(funcName)-20s:%(lineno)-5s] %(message)s"
            if 'EXTARGSPARSE_LOGFMT' in os.environ.keys():
                v = os.environ['EXTARGSPARSE_LOGFMT']
                if v is not None and len(v) > 0:
                    fmt = v
            formatter = logging.Formatter(fmt)
            handler.setFormatter(formatter)
            self.__logger.addHandler(handler)
            self.__logger.setLevel(loglvl)
        self.__subparser = None
        self.__cmdparsers = []
        self.__flags = []
        self.__load_command_map = {
            'string' : self.__load_command_line_string,
            'unicode' : self.__load_command_line_string,
            'int' : self.__load_command_line_int,
            'long' : self.__load_command_line_int,
            'float' : self.__load_command_line_float,
            'list' : self.__load_command_line_list,
            'bool' : self.__load_command_line_bool,
            'args' : self.__load_command_line_args,
            'command' : self.__load_command_subparser,
            'prefix' : self.__load_command_prefix,
            'count': self.__load_command_line_count
        }
        for p in priority:
            if p not in self.__class__.priority_args:
                raise Exception('(%s) not in priority values'%(p))
        self.__load_priority = priority
        self.__parse_set_map = {
            SUB_COMMAND_JSON_SET : self.__parse_sub_command_json_set,
            COMMAND_JSON_SET : self.__parse_command_json_set,
            ENVIRONMENT_SET : self.__parse_environment_set,
            ENV_SUB_COMMAND_JSON_SET : self.__parse_env_subcommand_json_set,
            ENV_COMMAND_JSON_SET : self.__parse_env_command_json_set
        }
        return

    def __find_subparser_inner(self,name):
        for k in self.__cmdparsers:
            if k.cmdname == name:
                return k
        return None


    def __get_subparser_inner(self,keycls):
        cmdparser = self.__find_subparser_inner(keycls.cmdname)
        if cmdparser is not None:
            return cmdparser
        if self.__subparser is None:
            self.__subparser = self.add_subparsers(help='',dest='subcommand')
        helpinfo = self.__get_help_info(keycls)
        parser = self.__subparser.add_parser(keycls.cmdname,help=helpinfo)
        cmdparser = _ParserCompact()
        cmdparser.parser = parser
        cmdparser.flags = []
        cmdparser.cmdname = keycls.cmdname
        cmdparser.typeclass = keycls
        self.__cmdparsers.append(cmdparser)
        return cmdparser


    def __load_command_subparser(self,prefix,keycls,lastparser=None):
        if lastparser :
            raise Exception('(%s) can not make command recursively'%(keycls.origkey))
        if not isinstance( keycls.value,dict):
            raise Exception('(%s) value must be dict'%(keycls.origkey))
        parser = self.__get_subparser_inner(keycls)
        self.__load_command_line_inner(keycls.prefix,keycls.value,parser)
        return True

    def __load_command_prefix(self,prefix,keycls,curparser=None):
        self.__load_command_line_inner(keycls.prefix,keycls.value,curparser)
        return True

    def __load_command_line_inner(self,prefix,d,curparser=None):
        self.__load_command_line_json_added(curparser)
        for k in d.keys():
            v = d[k]
            if curparser:
                # if we have in the mode for this we should make it
                # must be the flag mode
                self.__logger.info('%s , %s , %s , True'%(prefix,k,v))
                keycls = ExtKeyParse(prefix,k,v,True)
            else:
                # we can not make sure it is flag mode
                self.__logger.info('%s , %s , %s , False'%(prefix,k,v))
                keycls = ExtKeyParse(prefix,k,v,False)
            valid = self.__load_command_map[keycls.type](prefix,keycls,curparser)
            if not valid:
                raise Exception('can not add (%s)'%(k,v))
        return

    def load_command_line(self,d):
        if not isinstance(d,dict):
            raise Exception('input parameter(%s) not dict'%(d))
        self.__load_command_line_inner('',d,None)
        return


    def load_command_line_string(self,s):
        try:
            d = json.loads(s)
        except:
            raise Exception('(%s) not valid json string'%(s))
        #self.__logger.info('d (%s)'%(d))
        self.load_command_line(d)
        return


    def __set_jsonvalue_not_defined(self,args,flagarray,key,value):
        for p in flagarray:
            if p.isflag and p.type != 'prefix' and p.type != 'args':
                if p.optdest == key:
                    if getattr(args,key,None) is None:
                        if str(TypeClass(value)) != str(TypeClass(p.value)):
                            self.__logger.warn('%s  type (%s) as default value type (%s)'%(key,str(TypeClass(value)),str(TypeClass(p.value))))
                        self.__logger.info('set (%s)=(%s)'%(key,value))
                        setattr(args,key,value)
                    return args
        # we search for other value
        for p in self.__flags:
            if p.isflag and p.type != 'prefix' and p.type != 'args':
                if p.optdest == key:
                    if getattr(args,key,None) is None:
                        if str(TypeClass(value)) != str(TypeClass(p.value)):
                            self.__logger.warn('%s  type (%s) as default value type (%s)'%(key,str(TypeClass(value)),str(TypeClass(p.value))))
                        self.__logger.info('set (%s)=(%s)'%(key,value))
                        setattr(args,key,value)
                    return args
        for parser in self.__cmdparsers:
            for p in parser.flags:
                if p.isflag and p.type != 'prefix' and p.type != 'args':
                    if p.optdest == key:
                        if getattr(args,key,None) is None:
                            if str(TypeClass(value)) != str(TypeClass(p.value)):
                                self.__logger.warn('%s  type (%s) as default value type (%s)'%(key,str(TypeClass(value)),str(TypeClass(p.value))))
                            self.__logger.info('set (%s)=(%s)'%(key,value))
                            setattr(args,key,value)
                        return args
        self.__logger.warn('can not search for (%s)'%(key))
        return args

    def __load_jsonvalue(self,args,prefix,jsonvalue,flagarray):
        for k in jsonvalue:
            if isinstance(jsonvalue[k],dict):
                newprefix = ''
                if len(prefix) > 0:
                    newprefix += '%s_'%(prefix)
                newprefix += k
                args = self.__load_jsonvalue(args,newprefix,jsonvalue[k],flagarray)
            else:
                newkey = ''
                if (len(prefix) > 0):
                    newkey += '%s_'%(prefix)
                newkey += k
                args = self.__set_jsonvalue_not_defined(args,flagarray,newkey,jsonvalue[k])
        return args


    def __load_jsonfile(self,args,cmdname,jsonfile,curparser=None):
        assert(jsonfile is not None)
        prefix = ''
        if cmdname is not None :
            prefix += cmdname
        flagarray = self.__flags
        if curparser :
            flagarray = curparser.flags

        fp = None
        try:
            fp = open(jsonfile,'r+')
        except:
            raise Exception('can not open(%s)'%(jsonfile))
        try:
            jsonvalue = json.load(fp)
            fp.close()
            fp = None
        except:
            if fp is not None:
                fp.close()
            fp = None
            raise Exception('can not parse (%s)'%(jsonfile))
        jsonvalue = Utf8Encode(jsonvalue).get_val()
        return self.__load_jsonvalue(args,prefix,jsonvalue,flagarray)



    def __set_parser_default_value(self,args,flagarray):
        for keycls in flagarray:
            if keycls.isflag and keycls.type != 'prefix' and keycls.type != 'args':
                self.__set_jsonvalue_not_defined(args,flagarray,keycls.optdest,keycls.value)
        return args

    def __set_default_value(self,args):
        for parser in self.__cmdparsers:
            args = self.__set_parser_default_value(args,parser.flags)

        args = self.__set_parser_default_value(args,self.__flags)
        return args

    def __set_environ_value_inner(self,args,prefix,flagarray):
        for keycls in flagarray:
            if keycls.isflag and keycls.type != 'prefix' and keycls.type != 'args':
                optdest = keycls.optdest
                oldopt = optdest
                if getattr(args,oldopt,None) is not None:
                    # have set ,so we do not set it
                    continue
                optdest = optdest.upper()
                optdest = optdest.replace('-','_')
                if '_' not in optdest:
                    optdest = 'EXTARGS_%s'%(optdest)
                val = os.getenv(optdest,None)               
                if val is not None:
                    # to check the type
                    val = Utf8Encode(val).get_val()
                    if keycls.type == 'string':
                        setattr(args,oldopt,val)
                    elif keycls.type == 'bool':                     
                        if val.lower() == 'true':
                            setattr(args,oldopt,True)
                        elif val.lower() == 'false':
                            setattr(args,oldopt,False)
                    elif keycls.type == 'list':
                        try:
                            lval = eval(val)
                            lval = Utf8Encode(lval).get_val()
                            if not isinstance(lval,list):
                                raise Exception('(%s) environ(%s) not valid'%(optdest,val))
                            setattr(args,oldopt,lval)
                        except:
                            self.__logger.warn('can not set (%s) for %s = %s'%(optdest,oldopt,val))
                    elif keycls.type == 'int':
                        try:
                            lval = int(val)
                            setattr(args,oldopt,lval)
                        except:
                            self.__logger.warn('can not set (%s) for %s = %s'%(optdest,oldopt,val))
                    elif keycls.type == 'float':
                        try:
                            lval = float(val)
                            setattr(args,oldopt,lval)
                        except:
                            self.__logger.warn('can not set (%s) for %s = %s'%(optdest,oldopt,val))
                    else:
                        raise Exception('internal error when (%s) type(%s)'%(keycls.optdest,keycls.type))
        return args



    def __set_environ_value(self,args):
        for parser in self.__cmdparsers:
            args = self.__set_environ_value_inner(args,parser.cmdname,parser.flags)
        args = self.__set_environ_value_inner(args,'',self.__flags)
        return args

    def __set_command_line_self_args(self):
        for parser in self.__cmdparsers:
            curkey = ExtKeyParse(parser.cmdname,'$','*',True)
            self.__load_command_line_args(parser.cmdname,curkey,parser)
        curkey = ExtKeyParse('','$','*',True)
        self.__load_command_line_args('',curkey,None)
        return

    def __parse_sub_command_json_set(self,args):
        # now we should get the 
        # first to test all the json file for special command
        if self.__subparser and args.subcommand is not None:
            jsondest = '%s_json'%(args.subcommand)
            curparser = self.__find_subparser_inner(args.subcommand)
            assert(curparser is not None)
            jsonfile = getattr(args,jsondest,None)
            if jsonfile is not None:
                # ok we should make this parse
                args = self.__load_jsonfile(args,args.subcommand,jsonfile,curparser)
        return args

    def __parse_command_json_set(self,args):
        # to get the total command
        if args.json is not None:
            jsonfile = args.json
            args = self.__load_jsonfile(args,'',jsonfile,None)
        return args

    def __parse_environment_set(self,args):
        # now get the environment value
        args = self.__set_environ_value(args)
        return args

    def __parse_env_subcommand_json_set(self,args):
        # now to check for the environment as the put file
        if self.__subparser and args.subcommand is not None:
            jsondest = '%s_json'%(args.subcommand)
            curparser = self.__find_subparser_inner(args.subcommand)
            assert(curparser is not None)
            jsondest = jsondest.replace('-','_')
            jsondest = jsondest.upper()
            jsonfile = os.getenv(jsondest,None)
            if jsonfile is not None:
                # ok we should make this parse
                args = self.__load_jsonfile(args,args.subcommand,jsonfile,curparser)
        return args

    def __parse_env_command_json_set(self,args):
        # to get the json existed 
        jsonfile = os.getenv('EXTARGSPARSE_JSON',None)
        if jsonfile is not None:
            args = self.__load_jsonfile(args,'',jsonfile,None)
        return args

    def __check_help_options(self,params):
        showhelp = False
        for s in params:
            if s == '--':
                break
            elif s.startswith('--'):
                if s == '--help':
                    showhelp = True
                    break
            elif s.startswith('-'):
                if 'h' in s:
                    showhelp = True
                    break
        if not showhelp:
            return None
        return self.__print_out_help()



    def parse_command_line(self,params=None,Context=None):
        # we input the self command line args by default
        self.__set_command_line_self_args()
        if params is None:
            params = sys.argv[1:]

        s = self.__check_help_options(params)
        if s is not None:
            return s
        args = self.parse_args(params)

        for p in self.__load_priority:
            args = self.__parse_set_map[p](args)

        # set the default value
        args = self.__set_default_value(args)

        # now test whether the function has
        if self.__subparser and args.subcommand is not None:
            parser = self.__find_subparser_inner(args.subcommand)
            assert(parser is not None)
            funcname = parser.typeclass.function
            if funcname is not None:
                return call_func_args(funcname,args,Context)
        return args

    def __print_out_help(self):
        global extargs_shell_out_mode
        s = ''
        sio = StringIO.StringIO()
        self.print_help(sio)
        if extargs_shell_out_mode == 0:
            s += sio.getvalue()
            sys.stdout.write(s)
            sys.exit(0)
        else:
            s +=  'cat << EXTARGSEOF\n'
            s +=  '%s\n'%(sio.getvalue())
            s += 'EXTARGSEOF\n'
            s += 'exit 0\n'
        return s



    def __shell_eval_out_flagarray(self,args,flagarray,ismain=True,curparser=None):
        s = ''
        for flag in flagarray:
            if flag.isflag and flag.flagname is not None:
                if flag.type == 'args' or flag.type == 'list':
                    if flag.flagname == '$' :
                        if curparser is None and self.__subparser is not None:
                            continue
                        elif curparser is not None and curparser.typeclass.cmdname != args.subcommand:
                            # we do not output args
                            if flag.varname != 'subnargs':
                                # to not declare this one
                                s += 'unset %s\n'%(flag.varname)
                                s += 'declare -A -g %s\n'%(flag.varname)
                            continue
                    # make the global variable access
                    s += 'unset %s\n'%(flag.varname)
                    s += 'declare -A -g %s\n'%(flag.varname)
                    if flag.flagname == '$':
                        if  not ismain:
                            value = getattr(args,'subnargs',None)
                        else:
                            value = getattr(args,'args',None)
                    else:
                        value = getattr(args,flag.optdest,None)
                    if value is not None:
                        i = 0
                        for v in value:
                            if isinstance(v,str):
                                s += '%s[%d]=\'%s\'\n'%(flag.varname,i,v)
                            else:
                                s += '%s[%d]=%s\n'%(flag.varname,i,v)
                            i += 1
                else:
                    if ismain and flag.optdest == 'json' :
                        continue
                    elif curparser is not None:
                        finddest = '%s_json'%(curparser.typeclass.cmdname)
                        if flag.optdest == finddest:
                            continue
                    value = getattr(args,flag.optdest)
                    if flag.type == 'bool':
                        if value :
                            s += '%s=1\n'%(flag.varname)
                        else:
                            s += '%s=0\n'%(flag.varname)
                    else:
                        if flag.type == 'string' :
                            s += '%s=\'%s\'\n'%(flag.varname,value)
                        else:
                            s += '%s=%s\n'%(flag.varname,value)
        return s

    def shell_eval_out(self,params=None,Context=None):
        global extargs_shell_out_mode
        extargs_shell_out_mode = 1
        args = self.parse_command_line(params,Context)
        extargs_shell_out_mode = 0
        if isinstance(args,str):
            # that is help information
            return args
        # now we should found out the params
        # now to check for the type
        # now to give the value
        s = ''
        s += self.__shell_eval_out_flagarray(args,self.__flags)
        if self.__subparser is not None:            
            curparser = self.__find_subparser_inner(args.subcommand)
            assert(curparser is not None)
            keycls = curparser.typeclass
            if keycls.function is not None:
                s += '%s=%s\n'%(keycls.function,args.subcommand)
            else:
                s += 'subcommand=%s\n'%(args.subcommand)
            for curparser in self.__cmdparsers:
                s += self.__shell_eval_out_flagarray(args,curparser.flags,False,curparser)
        self.__logger.info('shell_out\n%s'%(s))
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

def parse_inner(args):
    set_log_level(args)
    commandline = ''
    fin = sys.stdin
    if args.input is not None:
        fin = open(args.input,'r+')
    for l in fin:
        commandline += l
    if fin != sys.stdin:
        fin.close()
    fin = None
    i=0
    for a in args.args:
        logging.info('[%d]=%s'%(i,a))
        i += 1        
    parser = ExtArgsParse(usage='%s [OPTIONS] ...'%(args.caption))
    parser.load_command_line_string(commandline)    
    s = parser.shell_eval_out(args.args,None)
    sys.stdout.write('%s'%(s))
    return

def main():
    inner_command='''
    {
        "verbose|v" : "+",
        "catch|C## to not catch the exception ##" : true,
        "input|i## to specify input default(stdin)##" : null,
        "$caption## set caption ##" : "runcommand",
        "$" : "+"
    }
    '''
    parser = ExtArgsParse()
    parser.load_command_line_string(inner_command)
    args = parser.parse_command_line()
    if args.catch:
        try:
            parse_inner(args)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            sys.stdout.write('cat <<EOM\n%s:%s:%s\nEOM\n'%(exc_type,exc_value,exc_traceback))
            sys.stdout.write('exit 3')
            sys.exit(3)
    else:
        parse_inner(args)
    return

main()