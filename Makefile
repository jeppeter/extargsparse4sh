
ifeq (${V},)
QUIET=@
else
QUIET=
endif

all:extargsparse4sh
	${QUIET}bash ./exttest.sh -v

extargsparse4sh:extargsparse4sh.tmpl check
	${QUIET}bash maketmpl shellout.py extargsparse4sh.tmpl extargsparse4sh
	${QUIET}chmod +x extargsparse4sh

check:checkcode
	${QUIET}bash checkcode  | sed -e '/^$$/d' >shellout2.py
	${QUIET}cat shellout.py | sed -e '/^$$/d' >shellout3.py
	${QUIET}cmp --quiet shellout2.py shellout3.py ; _res=$$? ; if [ $$_res -ne 0 ] ; then echo "not make same" >&2 ; exit 3 ; fi

checkcode:checkcode.tmpl shellout.py
	${QUIET}bash maketmpl shellout.py checkcode.tmpl checkcode

shellout.py:debug
	# we should remove the touched file as it will give output test
	${QUIET}rm -f shellout.py.touched
	${QUIET}python shellout.py -R && _checked=0;_cnt=0;_maxcnt=0;while [ 1 ] ;do if [ -f shellout.py.touched ] ; then _checked=`expr $$_checked \+ 1`;if [ $$_checked -gt 3 ] ; then break; fi; 	python -c 'import time;time.sleep(0.1)' ; else  _checked=0;  python -c 'import time;time.sleep(0.1)'; fi; done

debug:shellout.py.tmpl
	${QUIET}python format_template.py -i shellout.py.tmpl -P "%EXTARGSPARSE_STRIP_CODE%" -r "keyparse\.=" -c ExtArgsParse.get_subcommands -c ExtArgsParse.get_cmdopts -E "^debug_.*" -m "[r'^##extractstart.*',r'^##extractend.*']" -m "[r'^##importdebugstart.*',r'^##importdebugend.*']" -vvvv -o shellout.py extargsparse.__key__ extargsparse.__lib__

clean:
	${QUIET}rm -f extargsparse4sh checkcode shellout2.py shellout3.py shellout.py shellout.py.touched
