# extargsparse4sh
> [extargsparse](https://github.com/jeppeter/extargsparse) transport for bash

### Release History
* Sep 5th 2018 Release 0.3.6 to make help information ok
* Mar 31st 2017 Release 0.3.4 to make opthelp function test ok
* Mar 27th 2017 Release 0.2.8 to keep progressing with callback optparse in extargsparse4sh
* Jan 31st 2017 Release 0.2.6 to fixup bug in the extargsparse when environment for count type
* Jan 28th 2017 Release 0.2.4 to port extargsparse4sh to OS X Sierra
* Jan 3rd 2017 Release 0.2.2 to fixup the bug in multiple definition of same target
* Nov 13th 2016 Release 0.2.0 to make compatible with quote string like "\"variable\""

## simple example

```bash
#! /bin/bash

# use this read link because in mac os x ,this work
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
        local -a _list
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

```

> call command

```shell
bash ./example.sh -vv -p 300 dep cc ss
```

> output

```shell
COMMAND=(dep)
port=(300)
verbose=(2)
DEP_STR=(dep_str)
DEP_LIST total (0)
DEPARGS total (2)
DEPARGS[0]=(cc)
DEPARGS[1]=(ss)
RDEP_LIST total (0)
RDEPARGS total (0)
```

## callback optparse

> will call back for the optparse
* the optparse is the function
    ** input value is validx and params
    ** EXTARGSPARSE4SH_LONGOPT for long option
    ** EXTARGSPARSE4SH_SHORTOPT for short option if any
    ** EXTARGSPARSE4SH_VARNAME for varname

```shell

source extargsparse4sh
function push_pairs_global()
{
    local _validx="$1"
    shift
    local -a _params=($@)
    local _maxneed=`expr $_validx \+ 1`
    local _totalidx=${#ARRAYPAIR[@]}
    if [ $_maxneed -ge ${#_params[@]} ]
        then
        echo "could not get parse" >&2
        echo "error"
        return
    fi
    ARRAYPAIR[$_totalidx]=${_params[$_validx]}
    GLOBAL_ARRAY[$_totalidx]=${_params[$_validx]}
    _totalidx=`expr $_totalidx \+ 1`
    _validx=`expr $_validx \+ 1`
    ARRAYPAIR[$_totalidx]=${_params[$_validx]}
    GLOBAL_ARRAY[$_totalidx]=${_params[$_validx]}
    echo "2"
    return
}

list_debug()
{
    local _lname=$1
    shift
    local _cnt=0
    if [ $# -gt 0 ]
    then
        local -a _list
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


function testcase_push_global()
{
    unset GLOBAL_ARRAY
    declare -g -a GLOBAL_ARRAY
    read -r -d '' OPTIONS<<EOFMM
    {
        "verbose|v<VERBOSE>" : "+",
        "array|a<ARRAYPAIR>!optparse=push_pairs_global!" : [],
        "\$<ARGS>" : "*"
    }
EOFMM
    parse_command_line "$OPTIONS" "-vvvva" "hello" "good" "--array" "new" "cc"

    list_debug "ARRAYPAIR" "${ARRAYPAIR[@]}"
    list_debug "GLOBAL_ARRAY" "${GLOBAL_ARRAY[@]}"
    list_debug "ARGS" "${ARGV[@]}"
    cat <<EOF
VERBOSE [$VERBOSE]
EOF
}

testcase_push_global
```

> result

```shell
ARRAYPAIR total (4)
ARRAYPAIR[0]=(hello)
ARRAYPAIR[1]=(good)
ARRAYPAIR[2]=(new)
ARRAYPAIR[3]=(cc)
GLOBAL_ARRAY total (4)
GLOBAL_ARRAY[0]=(hello)
GLOBAL_ARRAY[1]=(good)
GLOBAL_ARRAY[2]=(new)
GLOBAL_ARRAY[3]=(cc)
ARGS total (0)
VERBOSE [4]
```

## howto compile 
> run in linux or macOS or cygwin 
> type command 

```shell
make
```

> it will output extargsparse4sh
