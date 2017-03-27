
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

ifeq (${P},)
PYTHON:=$(shell which python)
else
PYTHON:=${P}
endif

TOPDIR:=$(shell ${PYTHON} -c "import sys;import os;print('%s'%(os.path.realpath(sys.argv[1])))" .)

export PYTHON TOPDIR

all:${TOPDIR}/extargsparse4sh
	${Q}bash ./exttest.sh ${VERBOSE_OPTION}

${TOPDIR}/extargsparse4sh:${TOPDIR}/extargsparse4sh.tmpl check_shellout 
	${Q}${PYTHON} ${TOPDIR}/insertcode -i $<  -p '%EXTARGSPARSE%' bashstring ${TOPDIR}/shellout.py | \
		${PYTHON} ${TOPDIR}/insertcode -p '%EXTARGSPARSE4SH_VERSION%' -o $@ bashinsert ${TOPDIR}/VERSION 
	${Q}chmod +x extargsparse4sh

check_shellout:${TOPDIR}/shellout.py
	${Q}(${PYTHON} ${TOPDIR}/insertcode -i ${TOPDIR}/echocode.tmpl bashstring $< | /bin/bash | diff -B - $< ) || ( echo "can not check $<" ; exit 4)


${TOPDIR}/shellout.py:debug
	${Q}${PYTHON} shellout.py release && (  while [ 1 ];do   if [ -f shellout.py.touched ] ; then rm -f shellout.py.touched ;  break ;  fi ;  ${PYTHON}  -c 'import time;time.sleep(0.1)'; done)

debug:shellout.py.tmpl
	${Q}${PYTHON} format_template.py -i shellout.py.tmpl -P "%EXTARGSPARSE_STRIP_CODE%" -r "keyparse\.=" -c ExtArgsParse.get_subcommands -c ExtArgsParse.get_cmdopts -E "^debug_.*" -m "[r'^##extractstart.*',r'^##extractend.*']" -m "[r'^##importdebugstart.*',r'^##importdebugend.*']" -vvvv -o shellout.py extargsparse.__key__ extargsparse.__lib__
	${Q}${PYTHON} shellout.py ${VERBOSE_OPTION} test || (echo "can not run test ok" >&2 ; exit 5)

clean:
	${Q}rm -f extargsparse4sh shellout.py shellout.py.touched
