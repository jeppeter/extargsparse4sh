
ifeq (${V},)
Q=@
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

Q=
endif

all:extargsparse4sh
	${Q}bash ./exttest.sh ${VERBOSE_OPTION}

extargsparse4sh:extargsparse4sh.tmpl check
	${Q}bash maketmpl shellout.py extargsparse4sh.tmpl extargsparse4sh
	${Q}chmod +x extargsparse4sh

check:checkcode
	${Q}bash checkcode >shellout2.py
	${Q}diff -B shellout2.py shellout.py ; _res=$$? ; if [ $$_res -ne 0 ] ; then echo "not make same" >&2 ; exit 3 ; fi

checkcode:checkcode.tmpl shellout.py
	${Q}bash maketmpl shellout.py checkcode.tmpl checkcode

shellout.py:debug
	${Q}python shellout.py -R && (  while [ 1 ];do   if [ -f shellout.py.touched ] ; then rm -f shellout.py.touched ;  break ;  fi ;  python  -c 'import time;time.sleep(0.1)'; done)

debug:shellout.py.tmpl
	${Q}python format_template.py -i shellout.py.tmpl -P "%EXTARGSPARSE_STRIP_CODE%" -r "keyparse\.=" -c ExtArgsParse.get_subcommands -c ExtArgsParse.get_cmdopts -E "^debug_.*" -m "[r'^##extractstart.*',r'^##extractend.*']" -m "[r'^##importdebugstart.*',r'^##importdebugend.*']" -vvvv -o shellout.py extargsparse.__key__ extargsparse.__lib__
	${Q}python shellout.py --test ; _res=$$? ; if  [ $$_res -ne 0 ] ; then /bin/echo "can not run test shellout.py ok ($$_res)" >&2 ; exit $$_res ; fi

clean:
	${Q}rm -f extargsparse4sh checkcode shellout2.py shellout3.py shellout.py shellout.py.touched
