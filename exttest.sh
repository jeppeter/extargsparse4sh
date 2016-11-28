#! /bin/bash

_scriptfile=`readlink -f $0`
scriptdir=`dirname $_scriptfile`
test_verbose=0
EXTARGSPARSE_LOGLEVEL=0

source $scriptdir/extargsparse4sh

function Debug()
{
	local _fmt=$1
	shift
	local _backstack=0
	if [ $# -gt 0 ]
		then
		_backstack=$1	
	fi
	
	if [ $test_verbose -gt 0 ]	
		then
		_fmtstr=""
		if [ $test_verbose -gt 2 ]
			then
			_fmtstr="${BASH_SOURCE[$_backstack]}:${BASH_LINENO[$_backstack]} "
		fi

		_fmtstr="$_fmtstr$_fmt"
		echo -e "$_fmtstr" >&2
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

function assert()
{
	local _assval="$1"
	local _backstack=0
	if [ $# -gt 1 ]
		then
		_backstack=$2
	fi
	_backstack=`expr $_backstack \+ 1`

	if [ ! $_assval ] ; then
		Debug "assert ($_assval) failed" $_backstack
		exit 3
	else
		Debug "assert ($_assval) succ" $_backstack
	fi
	return
}

function assert_int_equal()
{
	local _a="$1"
	local _b="$2"
	local _ass=" $_a -eq $_b "
	local _backstack=0
	if [ $# -gt 2 ]
		then
		_backstack=$3
	fi
	_backstack=`expr $_backstack \+ 1`
	assert "$_ass" $_backstack
	return
}

function assert_str_equal()
{
	local _a="$1"
	local _b="$2"
	local _ass=" \"$_a\" = \"$_b\" "
	local _backstack=0
	if [ $# -gt 2 ]
		then
		_backstack=$3
	fi
	_backstack=`expr $_backstack \+ 1`
	assert "$_ass" $_backstack
	return
}

function assert_arr_equal()
{
	local _aname="$1"
	shift
	local _bname="$1"
	shift
	local -A _arr
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
	assert_int_equal "$verbose"	 3
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
	longopt=`expr match "$key" '--.*'`
	shortopt=`expr match "$key" '-.*'`
	longkey=`expr match "$key" '--\(.*\)'`
	shortkey=`expr match "$key" '-\(.*\)'`
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
		keys=$(echo "$shortkey" | sed 's/\(.\)/\1\n/g')
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
		eval "$funcname"
	done
fi

