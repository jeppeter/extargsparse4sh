
ifeq (${V},)
QUIET=@
VERBOSE_OPTION:=
else
ifeq (${V},1)
VERBOSE_OPTION:=-v
else
ifeq (${V},2)
VERBOSE_OPTION:=-vv
else
VERBOSE_OPTION:=-vvv
endif
endif

QUIET=
endif

all:extargsparse4sh
	${QUIET}bash ./exttest.sh ${VERBOSE_OPTION}

extargsparse4sh:shellout.py extargsparse4sh.tmpl check
	${QUIET}bash maketmpl shellout.py extargsparse4sh.tmpl extargsparse4sh
	${QUIET}chmod +x extargsparse4sh

check:checkcode shellout.py
	${QUIET}bash checkcode  | sed -e '/^$$/d' >shellout2.py
	${QUIET}cat shellout.py | sed -e '/^$$/d' >shellout3.py
	${QUIET}cmp --quiet shellout2.py shellout3.py ; _res=$$? ; if [ $$_res -ne 0 ] ; then echo "not make same" >&2 ; exit 3 ; fi

checkcode:checkcode.tmpl
	${QUIET}bash maketmpl shellout.py checkcode.tmpl checkcode

shellout.py:debug
	${QUIET}python shellout.py -R && (  while [ 1 ];do   if [ -f shellout.py.touched ] ; then rm -f shellout.py.touched ;  break ;  fi ;  python  -c 'import time;time.sleep(0.1)'; done)

debug:shellout.py.tmpl
	${QUIET}python format_template.py -i shellout.py.tmpl -P "%EXTARGSPARSE_STRIP_CODE%" -r "keyparse\.=" -c ExtArgsParse.get_subcommands -c ExtArgsParse.get_cmdopts -E "^debug_.*" -m "[r'^##extractstart.*',r'^##extractend.*']" -m "[r'^##importdebugstart.*',r'^##importdebugend.*']" -vvvv -o shellout.py extargsparse.__key__ extargsparse.__lib__
	${QUIET}python shellout.py --test ; _res=$$? ; if  [ $$_res -ne 0 ] ; then /bin/echo "can not run test shellout.py ok ($$_res)" >&2 ; exit $$_res ; fi

clean:
	${QUIET}rm -f extargsparse4sh checkcode shellout2.py shellout3.py shellout.py shellout.py.touched
