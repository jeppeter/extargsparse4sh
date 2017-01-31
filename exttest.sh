#! /bin/bash

if [ -n "$EXTTEST_DEBUG" ] && [ $EXTTEST_DEBUG -gt 3 ]
	then
	set -x
fi

_scriptfile=`perl -e "use Cwd abs_path; print abs_path(shift);" $0`
scriptdir=`dirname $_scriptfile`
test_verbose=0
EXTARGSPARSE_LOGLEVEL=0
DEBUG_LEVEL=2
INFO_LEVEL=1

source $scriptdir/extargsparse4sh

function __Debug()
{
	local _fmt=$1
	shift
	local _backstack=0
	if [ $# -gt 0 ]
		then
		_backstack=$1
	fi
	
	_fmtstr=""
	if [ $test_verbose -gt 2 ]
		then
		_fmtstr="${BASH_SOURCE[$_backstack]}:${BASH_LINENO[$_backstack]} "
	fi

	_fmtstr="$_fmtstr$_fmt"
	echo -e "$_fmtstr" >&2
}

function Debug()
{
	local _fmt=$1
	shift
	local _backstack=0
	if [ $# -gt 0 ]
		then
		_backstack=$1
	fi
	_backstack=`expr $_backstack \+ 1`
	
	if [ $test_verbose -ge $DEBUG_LEVEL ]	
		then
		__Debug "$_fmt" "$_backstack"
	fi
	return
}

function Info()
{
	local _fmt=$1
	shift
	local _backstack=0
	if [ $# -gt 0 ]
		then
		_backstack=$1
	fi
	_backstack=`expr $_backstack \+ 1`
	
	if [ $test_verbose -ge $INFO_LEVEL ]
		then
		__Debug "$_fmt" "$_backstack"
	fi
	return
}



function ErrorExit()
{
	local _ec=$1
	local _fmt="$2"
	local _backstack=0
	if [ $# -gt 2 ]
		then
		_backstack=$3
	fi
	local _fmtstr=""

	if [ $test_verbose -gt 2 ]
		then
		_fmtstr="${BASH_SOURCE[$_backstack]}:${BASH_LINENO[$_backstack]} "
	fi
	_fmtstr="$_fmtstr$_fmt"
	echo -e "$_fmtstr" >&2
	exit $_ec
}

__check_in_list()
{
    local _chkitem="$1"
    shift
    local _curitem
    local _i
    _i=0
    for _curitem in "$@"
    do
        if [ "$_chkitem" = "$_curitem" ]
          then
          return $_i
        fi
        _i=`expr $_i \+ 1`
    done
    return -1
}

__check_file_operator()
{
  local _operator="$1"
  local _res
  __check_in_list "$_operator" "-a" "-b" "-c" "-d" "-e" "-f" "-g" "-h" "-k" "-p" "-r" "-s" "-t" "-u" "-w" "-x" "-G" "-L" "-N" "-O" "-S" "-o" "-v" "-R" "-z" "-n"
  _res=$?
  return $_res
}


__assert ()
{
  local _res
  local _callnum=1
  local _nextnum
  local _expr1
  local _expr2
  local _expr3
  local _expr4
  local _resstr
  __check_file_operator "$2" 
  _res=$?
  if [ $_res -eq 255 ]
    then
      if [ $# -lt 4 ]
        then
        ErrorExit 3 "$@ not valid"
      fi
      if [ $# -gt 4 ]
        then
        _callnum="$5"
      fi

      if [ "$2" "$3" "$4" ]
        then
        _resstr="true"
      else
        _resstr="false"
      fi
  else
     if [ $# -lt 3 ]
      then
      ErrorExit 3 "$@ not valid"
    fi
    if [ $# -gt 3 ]
      then
      _callnum="$4"
    fi

    if [ "$2" "$3" ]
      then
      _resstr="true"
    else
      _resstr="false"
    fi
  fi

  if [ "$_resstr" != "$1" ]
    then  
    _nextnum=`expr $_callnum \+ 1`
    ErrorExit 3 "assert ($*) failed" $_nextnum
  fi


}


assert() {
  local _expr1="$1"
  local _expr2="$2"
  local _expr3="$3"
  local _expr4="$4"
  local _callnum=1
  local _nextnum
  local _res
  __check_file_operator "$1" 
  _res=$?
  if [ $_res -eq 255 ]
    then
    if [ $# -lt 3 ]
      then
      ErrorExit 3 "can not accept($*)"
    fi
    if [ -n "$_expr4" ]
      then
      _callnum="$_expr4"
    fi
    _nextnum=`expr $_callnum \+ 1`
    __assert "true" "$_expr1" "$_expr2" "$_expr3" $_nextnum
    Debug "assert ( $_expr1 $_expr2 $_expr3 ) succ"
  else
      if [ $# -lt 2 ]
        then
        ErrorExit 3 "can not accept($*)"
      fi
    if [ -n "$_expr3" ]
      then
      _callnum="$_expr3"
    fi
    _nextnum=`expr $_callnum \+ 1`
    __assert "true" "$_expr1" "$_expr2" $_nextnum
    Debug "assert ($_expr1 $_expr2) succ"
  fi
}

assert_fail() {
  local _expr1="$1"
  local _expr2="$2"
  local _expr3="$3"
  local _expr4="$4"
  local _callnum=1
  local _nextnum
  local _res
  __check_file_operator "$1" 
  _res=$?
  if [ $_res -eq 255 ]
    then
    if [ $# -lt 3 ]
      then
      ErrorExit 3 "can not accept($*)"
    fi
    if [ -n "$_expr4" ]
      then
      _callnum="$_expr4"
    fi
    _nextnum=`expr $_callnum \+ 1`
    __assert "false" "$_expr1" "$_expr2" "$_expr3" $_nextnum
  else
      if [ $# -lt 2 ]
        then
        ErrorExit 3 "can not accept($*)"
      fi
    if [ -n "$_expr3" ]
      then
      _callnum="$_expr3"
    fi
    _nextnum=`expr $_callnum \+ 1`
    __assert "false" "$_expr1" "$_expr2" $_nextnum
  fi
}

function assert_int_equal()
{
	local _a="$1"
	local _b="$2"
	local _backstack=0
	if [ $# -gt 2 ]
		then
		_backstack=$3
	fi
	_backstack=`expr $_backstack \+ 1`
	assert "$_a" -eq "$_b" $_backstack
	return
}

function assert_str_equal()
{
	local _a="$1"
	local _b="$2"
	local _backstack=0
	if [ $# -gt 2 ]
		then
		_backstack=$3
	fi
	_backstack=`expr $_backstack \+ 1`
	assert "$_a" = "$_b" $_backstack
	return
}

function assert_arr_equal()
{
	local _aname="$1"
	shift
	local _bname="$1"
	shift
	local -a _arr
	local -i _cnt
	local -i _mod
	local -i _len
	local -i _pair
	_cnt=0
	while [ $# -gt 0 ]
	do
		_arr[$_cnt]="$1"
		_cnt=`expr $_cnt \+ 1`
		shift
	done

	_mod=`expr $_cnt % 2`
	if [ $_mod -ne 0 ]
		then
		ErrorExit 3 "input ($_aname) != ($_bname) _cnt($_cnt) ${_arr[@]}" 1
	fi

	_len=`expr $_cnt / 2`
	_mod=0
	while [ $_mod -lt $_len ]
	do
		_pair=`expr $_mod \+ $_len`
		Debug "[$_mod] ${_arr[$_mod]} [$_pair] ${_arr[$_pair]}"
		assert_str_equal "${_arr[$_mod]}" "${_arr[$_pair]}" 1
		_mod=`expr $_mod \+ 1`
	done
	return
}

function testcase_cdrun_case()
{
	DEF_BASEDIR=`pwd`
	read -r -d '' OPTIONS<<EOF
		{
			"verbose|v<verbose>## to specify verbose mode default(0)##" : "+",
			"vnc|V<vncmode>## to specify vnc mode default(0)##" : false,
			"debug|d<debugmode>## to specify debug mode##" : false,
			"\$debugflag<debugflaginner>## to specify debug flag default() ##" : "",
			"log|l<debugfileinner>## to specify debug flag default()##" : "",
			"monitor|m<monitormode>## to specify monitor mode default(0)##" : false,
			"trace|t<traceflaginner>## to make trace file default(stderr) ##" : "",
			"cdrom|c<cdromfile>## to specify cdromfile default()##" : "",
			"order|o<bootordercmdlineinner>## to specify bootorder default()##" : "",
			"vdi|f<vdifile>## specify vdi file ##" : "" ,
			"\$<basedirarr>## [basedir] default($DEF_BASEDIR) ##" : "+"
		}
EOF

	parse_command_line "$OPTIONS" -vvvV -d -l "/tmp/cdrun" -t "css" -o "bootorder=cc" -f "/tmp/win10.vdi" "vv"
	Debug "verbose[$verbose]"
	assert_int_equal "$verbose"	 3
	Debug "vncmode[$vncmode]"
	assert_int_equal "$vncmode" 1
	assert_int_equal "$debugmode" 1
	assert_str_equal "$debugfileinner" "/tmp/cdrun"
	assert_str_equal "$traceflaginner" "css"
	assert_str_equal "$bootordercmdlineinner" "bootorder=cc"
	assert_str_equal "$vdifile" "/tmp/win10.vdi"
	assert_arr_equal "basedirarr" "inputarr" "${basedirarr[@]}" "vv"
	return
}

function testcase_kernel_compile()
{
	default_versionname="newversion"
	def_numjobs=4
	read -r -d '' OPTIONS <<EOF
	{
		"reconfig|r##to specify reconfig##" : false,
		"link|l<linkfiles>##to specify the linkfiles##" : "",
		"verbose|v##to specify##to specify ##" :  "+",
		"versionname|V##to specify the versionname for current default($default_versionname)##" : "$default_versionname",
		"job|j<numjobs>##to specify the parallevel jobs current default($def_numjobs)##" : $def_numjobs,
		"debug|d<debugmode>##to specify debug mode default(0)##" : false,
		"clean|c<cleanmode>##to specify clean mode default(0)##" : false,
		"\$<moduledirs>##to compile modules for specified directory##" : "*"
	}
EOF
	parse_command_line "$OPTIONS" -vvv -V "debug1" -j 5 -dddd -r -l "/tmp/linkfile" "arch/x86"
	assert_int_equal "$verbose" 3
	assert_str_equal "$versionname" "debug1"
	assert_int_equal "$numjobs" 5
	assert_int_equal "$debugmode" 1
	assert_str_equal "$linkfiles" "/tmp/linkfile"
	assert_arr_equal "moduledirs" "inputarr" "${moduledirs[@]}" "arch/x86"
	return
}

function testcase_qemu_compile()
{
	def_numjobs=4
	read -r -d '' OPTIONS<<EOFMM
		{
			"reconfig|r##to specify reconfig default(0)##" : false,
			"verbose|v" : "+",
			"job|j<numjobs>##to specify the parallevel jobs current default($def_numjobs)##" : $def_numjobs,
			"debug|d<debugmode>##to specify the debug mode##" : false,
			"makedebug|m<makedebugmode>##to specify make running in debug mode##" : false,
			"reserve|R<reservemode>##to specify not delete mediate file##" : false,
			"\$<notusedarr>" : 0
		}
EOFMM
	
	parse_command_line "$OPTIONS" -vvvv -d -m -R 
	assert_int_equal "$verbose" 4
	assert_int_equal "$numjobs" 4
	assert_int_equal "$debugmode" 1
	assert_int_equal "$makedebugmode" 1
	assert_int_equal "$reservemode" 1
	assert_arr_equal "notusedarr" "inputarr" "${notusedarr[@]}"
	return
}

function testcase_seabios_compile()
{
	def_numjobs=4
	read -r -d '' OPTIONS<<EOFMM
		{
			"reconfig|r##to specify reconfig default(0)##" : false,
			"verbose|v" : "+",
			"job|j<numjobs>##to specify the parallevel jobs current default($def_numjobs)##" : $def_numjobs,
			"debug|d<debugmode>##to specify the debug mode##" : false,
			"\$<notusedarr>" : 0
		}
EOFMM
	parse_command_line "$OPTIONS" -v -d -j 3
	assert_int_equal "$verbose" 1
	assert_int_equal "$reconfig" 0
	assert_int_equal "$numjobs" 3
	assert_int_equal "$debugmode" 1
	assert_arr_equal "notusedarr" "inputarr" "${notusedarr[@]}"
	return
}

function testcase_quote_commandline()
{
	default_versionname="newversion"
	def_numjobs=4
	read -r -d '' OPTIONS <<EOF
	{
		"reconfig|r##to specify reconfig##" : false,
		"link|l<linkfiles>##to specify the linkfiles##" : "",
		"verbose|v##to specify##to specify ##" :  "+",
		"versionname|V##to specify the versionname for current default($default_versionname)##" : "$default_versionname",
		"job|j<numjobs>##to specify the parallevel jobs current default($def_numjobs)##" : $def_numjobs,
		"debug|d<debugmode>##to specify debug mode default(0)##" : false,
		"clean|c<cleanmode>##to specify clean mode default(0)##" : false,
		"\$<moduledirs>##to compile modules for specified directory##" : "*"
	}
EOF
	parse_command_line "$OPTIONS" -vvv -V "debug1" -j 5 -dddd -r -l "/tmp/linkfile" "'arch/x86'" "\"cc dd\""
	assert_int_equal "$verbose" 3
	assert_str_equal "$versionname" "debug1"
	assert_int_equal "$numjobs" 5
	assert_int_equal "$debugmode" 1
	assert_str_equal "$linkfiles" "/tmp/linkfile"
	assert_arr_equal "moduledirs" "inputarr" "${moduledirs[@]}" "'arch/x86'" "\"cc dd\""
	return
}

function testcase_subcommand()
{
	subcommand=''
	read -r -d '' OPTIONS <<EOF
        {
            "fdisk<CHOICECOMMAND>" : {
                "\$<packages>##to specify packages additional installed##" : "*"
            },
            "debootstrap<CHOICECOMMAND>" : {
                "\$<packages>##to specify packages additional installed##" : "*"
            },
            "mountalldir<CHOICECOMMAND>" : {
            	"\$<packages>##to specify packages additional installed##" : "*"
            },
            "\$<packages>##to specify packages additional installed##" : "*"
        }
EOF
	parse_command_line "$OPTIONS" "debootstrap" "hello" "ok"
	assert_str_equal "$CHOICECOMMAND" "debootstrap"
	assert_arr_equal "packages" "inputarr" "${packages[@]}" "hello" "ok"
	return
}

function testcase_zero_args()
{
	DEF_KERNELDIR=/lib/modules/`uname -r`
	read -r -d '' OPTIONS<<EOFMM
	{
		"verbose|v<verbose>##verbose mode##" : "+",
		"kernel|k<KERNELDIR>##specify kernel dir default($DEF_KERNELDIR)##" : "$DEF_KERNELDIR",
		"$<DIRS>##[srcdir] [inst]##" : "*"
	}
EOFMM
	parse_command_line "$OPTIONS"
	assert_int_equal "$verbose" 0
	assert_str_equal "$KERNELDIR" "$DEF_KERNELDIR"
	assert_arr_equal "DIRS" "inputarr" "${DIRS[@]}"
	return
}

function testcase_extargs_version()
{
	fileversion=$(cat "$scriptdir/VERSION")
	echoversion=$(extargsparse4sh_version)
	assert_str_equal "$fileversion" "$echoversion"
	return
}

function testcase_environ_get()
{
	read -r -d '' OPTIONS<<EOFMM
	{
		"verbose|v" : "+",
		"offset|o" : 150
	}
EOFMM
	export EXTARGS_VERBOSE=4
	export EXTARGS_OFFSET=0x40
	parse_command_line "$OPTIONS"
	assert_int_equal "$verbose" "4"
	assert_int_equal "$offset" "64"
	unset EXTARGS_OFFSET
	unset EXTARGS_VERBOSE
	return
}


function get_testcase_funcnames()
{
	declare -f  | perl -ne 'if ($_ =~ m/^(testcase_[\w]+)\s+.*/o){print "$1\n";}'
	return
}

Usage()
{
	local -i _ec=$1
	local _fmt=$2
	local _fp=2
	local _funcstr
	local _funcs
	local _item
	local -i _funccnt
	_funcs=$(get_testcase_funcnames)
	_funccnt=0
	_funcstr=""
	for _item in $_funcs
	do
		if [ $_funccnt -gt 0 ]
			then
			_funcstr="$_funcstr|"
		fi
		_funcstr="$_funcstr$_item"
		_funccnt=`expr $_funccnt \+ 1`
	done

	if [ $_ec -eq 0 ]
		then
		_fp=1
	fi

	if [ -n "$_fmt" ]
		then
		echo "$_fmt" >&$_fp
	fi

	echo "$0 [OPTIONS] [funcname]..." >&$_fp
	echo "  -h|--help                      to display this help information" >&$_fp
	echo "  -v|--verbose                   to specify verbose mode" >&$_fp
	echo " [funcname]                      can be ($_funcstr)" >&$_fp
	exit $_ec
}

while [ $# -gt 0 ]
do
	key="$1"
	longopt=`echo "$key" | grep -e '^--' | wc -l | tr -d [:space:]`
	shortopt=`echo "$key" | grep -e '^-' | wc -l | tr -d [:space:]`
	longkey=`echo "$key" | sed 's/^--\(.*\)/\1/'`
	shortkey=`echo "$key" | sed 's/^-\(.*\)/\1/'`
	if [ $longopt -gt 0 ]
		then
		case "$longkey" in
			help)
				Usage 0 ""
				;;
			verbose)
				test_verbose=`expr $test_verbose \+ 1`
				;;
			*)
				Usage 3 "unknown ($key)"
				;;
		esac
	elif [ $shortopt -gt 0 ]
		then
		keys=$(echo "$shortkey" | sed 's/\(.\)/\1 /g' | tr [:space:] "\n" )
		for i in $keys
		do
			case "$i" in
				h)
					Usage 0 ""
					;;
				v)
					test_verbose=`expr $test_verbose \+ 1`
					;;
				*)
					Usage 3 "unknown ($i)"
					;;
			esac
		done
	else
		break
	fi
	shift
done

EXTARGSPARSE_LOGLEVEL=$test_verbose
export EXTARGSPARSE_LOGLEVEL

if [ $# -ne 0 ]
	then
	for funcname in "$@"
	do
		founded=0
		for cmpnames in $(get_testcase_funcnames)
		do
			if [ "$cmpnames" = "$funcname" ]
				then
				founded=1
				Info "$funcname"
				eval "$funcname"
				break
			fi
		done
		if [ $founded -eq 0 ]
			then
			ErrorExit 3 "can not find function($funcname)"
		fi
	done
else
	for funcname in $(get_testcase_funcnames)
	do
		Info "$funcname"
		eval "$funcname"
	done
fi

