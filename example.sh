#! /bin/bash


_scriptfile=`perl -e "use Cwd abs_path; print abs_path(shift);" $0`
scriptdir=`dirname $_scriptfile`


. $scriptdir/extargsparse4sh

RDEP_LIST=cc
RDEPARGS=bbs
DEP_LIST=BBD
DEPARGS=csw

read -r -d '' OPTIONS <<EOF
	{
		"port|p<portnum>## port to specified ##" : 3000,
		"verbose|v<verbosemode>" : "+",
		"dep<COMMAND>## dep to handle ##"  : {
			"string<DEP_STR>" : "dep_str",
			"list<DEP_LIST>" : [],
			"$<DEPARGS>" : "*"
		},
		"rdep<COMMAND>## reverse dep to handle##" : {
			"string<RDEP_STR>" : "rdep_str",
			"list<RDEP_LIST>" : [],
			"$<RDEPARGS>" : "*"
		}
	}
EOF

list_debug()
{
	local _lname=$1
	shift
	local _cnt=0
	if [ $# -gt 0 ]
	then
		local -A _list
		_cnt=0
		for _item in "$@"
		do
			_list[$_cnt]=$_item
			_cnt=`expr $_cnt \+ 1`
		done

	else
		local _list=()
	fi
	_cnt=0
	local _totalcnt=${#_list[@]}
	echo "$_lname total ($_totalcnt)"
	for _item in "${_list[@]}"
	do
		echo "$_lname[$_cnt]=($_item)"
		_cnt=`expr $_cnt \+ 1`
	done
}

parse_command_line "$OPTIONS" "$@"

cat <<EOF
COMMAND=($COMMAND)
port=($portnum)
verbose=($verbosemode)
EOF

if [ "$COMMAND" = "dep" ]
	then
	echo "DEP_STR=($DEP_STR)"
	list_debug "DEP_LIST" "${DEP_LIST[@]}"
	list_debug "DEPARGS" "${DEPARGS[@]}"
	list_debug "RDEP_LIST" "${RDEP_LIST[@]}"
	list_debug "RDEPARGS" "${RDEPARGS[@]}"
elif [ "$COMMAND" = "rdep" ]
	then
	echo "RDEP_STR=($RDEP_STR)"
	list_debug "DEP_LIST" "${DEP_LIST[@]}"
	list_debug "DEPARGS" "${DEPARGS[@]}"
	list_debug "RDEP_LIST" "${RDEP_LIST[@]}"
	list_debug "RDEPARGS" "${RDEPARGS[@]}"
else
	echo "not specified command"
fi