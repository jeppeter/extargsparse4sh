
ifeq (${V},)
QUIET=@
else
QUIET=
endif

all:extargsparse4sh
	${QUIET}bash ./exttest.sh -v

extargsparse4sh:shellout.py extargsparse4sh.tmpl check
	${QUIET}bash maketmpl shellout.py extargsparse4sh.tmpl extargsparse4sh
	${QUIET}chmod +x extargsparse4sh

check:checkcode shellout.py
	${QUIET}bash checkcode  | sed -e '/^$$/d' >shellout2.py
	${QUIET}cat shellout.py | sed -e '/^$$/d' >shellout3.py
	${QUIET}cmp --quiet shellout2.py shellout3.py ; _res=$$? ; if [ $$_res -ne 0 ] ; then echo "not make same" >&2 ; exit 3 ; fi

checkcode:checkcode.tmpl
	${QUIET}bash maketmpl shellout.py checkcode.tmpl checkcode

clean:
	${QUIET}rm -f extargsparse4sh checkcode shellout2.py shellout3.py
