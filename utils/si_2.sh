#!/bin/bash
#desc: run script only one at any time
#author: jack

#source the system environment
. /etc/profile 2>/dev/null
. ~/.bashrc 2>/dev/null
#

si_log_path="/var/log/si_run_2"
first_log_path="/var/log/si.log"

function is_root()
{
    if [ $(id -u) -eq 0 ];then
        echo -e "yes"
    else
        echo -e "no"
    fi
}

function run_bin()
{
    local si_path="$1"
    local script_file="$2"
    local file_type="$3"
    shift 3
    left_all_args="$*"
    # echo -e "si_path $si_path, script_file $script_file file_type $file_type" >> /tmp/k_check
    # echo -e "left_all_args $left_all_args" >> /tmp/k_check
    local script_file="`pwd`/${script_file}"
    if [ "$file_type" == "shell" ];then
        log_path="$shell_log"
    elif [ "$file_type" == "python" ];then
        log_path="$python_log"
    elif [ "$file_type" == "perl" ];then
        log_path="$perl_log"
    elif [ "$file_type" == "php" ];then
        log_path="$php_log"
    elif [ "$file_type" == "unknown" ];then
        log_path="$unknown_log"
    else:
        log_path="$unknown_log"
    fi
    if [ ! -f "$script_file" ];then
        echo -e "[Sorry..$script_file not found]" >> $log_path
        exit 2
    fi
    if [ "$file_type" == "unknown" ];then
        echo -e "[Sorry..$file_type is unknown]" >> $log_path
        exit 2
    fi
    if [ "$file_type" == "shell" ];then
        echo -e "【It's a shell..】" >> $log_path
        echo -e "============================= Begin for $script_file:【`date +%F_%H:%M:%S`】==========================" >> $log_path
        shell_bin=$(which bash 2>/dev/null|column -t)
        if [ "$use_own" == "yes" ];then
            echo -e "Use own." >> $log_path
            chmod +x $script_file && $script_file $left_all_args 1>>$log_path 2>&1
        else
            if [ "$shell_bin" == " " ];then
                echo -e "Sorry..shell_bin is null..Cant run cause not found bash" >> $log_path
                exit 2
            fi
            $shell_bin $script_file $left_all_args 1>>$log_path 2>&1
        fi
        echo -e "============================= End for $script_file:【`date +%F_%H:%M:%S`】==========================\n" >> $log_path
    elif [ "$file_type" == "python" ];then
        echo -e "【It's a python..】" >> $log_path
        echo -e "============================= Begin for $script_file:【`date +%F_%H:%M:%S`】==========================" >> $log_path
        python_bin=$(which python 2>/dev/null|column -t)
        if [ "$use_own" == "yes" ];then
            echo -e "Use own." >> $log_path
            chmod +x $script_file && $script_file $left_all_args 1>>$log_path 2>&1
        else
            if [ "$python_bin" == " " ];then
                echo -e "Sorry..python_bin is null..Cant run cause not found bash" >> $log_path
                exit 2
            fi
            $python_bin $script_file $left_all_args 1>>$log_path 2>&1
        fi
        echo -e "============================= End for $script_file:【`date +%F_%H:%M:%S`】==========================\n" >> $log_path
    elif [ "$file_type" == "perl" ];then
        echo -e "【It's a perl..】" >> $log_path
        echo -e "============================= Begin for $script_file:【`date +%F_%H:%M:%S`】==========================" >> $log_path
        perl_bin=$(which perl 2>/dev/null|column -t)
        if [ "$use_own" == "yes" ];then
            echo -e "Use own." >> $log_path
            chmod +x $script_file && $script_file $left_all_args 1>>$log_path 2>&1
        else
            if [ "$perl_bin" == " " ];then
                echo -e "Sorry..perl_bin is null..Cant run cause not found bash" >> $log_path
                exit 2
            fi
            $perl_bin $script_file $left_all_args 1>>$log_path 2>&1
        fi
        echo -e "============================= End for $script_file:【`date +%F_%H:%M:%S`】==========================\n" >> $log_path
    elif [ "$file_type" == "php" ];then
        echo -e "【It's a php..】" >> $log_path
        echo -e "============================= Begin for $script_file:【`date +%F_%H:%M:%S`】==========================" >> $log_path
        php_bin=$(which php 2>/dev/null|column -t)
        if [ "$use_own" == "yes" ];then
            echo -e "Use own." >> $log_path
            chmod +x $script_file && $script_file $left_all_args 1>>$log_path 2>&1
        else
            if [ "$php_bin" == " " ];then
                echo -e "Sorry..php_bin is null..Cant run cause not found bash" >> $log_path
                exit 2
            fi
            $php_bin $script_file $left_all_args 1>>$log_path 2>&1
        fi
        echo -e "============================= End for $script_file:【`date +%F_%H:%M:%S`】==========================\n" >> $log_path
    fi
}

function usage()
{
    echo -e "Usage:\n\t$0 /path/to/the/script"
    exit
}

function cd_into_right_path()
{
    file_path=$1
    base_path=$(dirname $file_path)
    if [ -d $base_path ];then
        cd $base_path
    else
        echo -e "Wrong.. No parent path for script $file_path found"
        exit
    fi
}

function make_the_log_dirs()
{
    local only_name="$1"
    if [ ! -d "$si_log_path" ];then
        mkdir -p ${si_log_path}/{php,shell,python,perl,unknown}
    fi
    php_log_dir="${si_log_path}/php/$(date +%F)"
    if [ ! -d "$php_log_dir" ];then
        mkdir -p $php_log_dir
    fi
    python_log_dir="${si_log_path}/python/$(date +%F)"
    if [ ! -d "$python_log_dir" ];then
        mkdir -p $python_log_dir
    fi
    shell_log_dir="${si_log_path}/shell/$(date +%F)"
    if [ ! -d "$shell_log_dir" ];then
        mkdir -p $shell_log_dir
    fi
    perl_log_dir="${si_log_path}/perl/$(date +%F)"
    if [ ! -d "$perl_log_dir" ];then
        mkdir -p $perl_log_dir
    fi
    unknown_log_dir="${si_log_path}/unknown/$(date +%F)"
    if [ ! -d "$unknown_log_dir" ];then
        mkdir -p $unknown_log_dir
    fi
    export php_log="${php_log_dir}/${only_name}.log"
    export shell_log="${shell_log_dir}/${only_name}.log"
    export python_log="${python_log_dir}/${only_name}.log"
    export perl_log="${perl_log_dir}/${only_name}.log"
    export unknown_log="${unknown_log_dir}/${only_name}.log"
}

function get_the_script_type()
{
    file_path=$1
    if [ ! -f $file_path ];then
        echo -e "Sorry..No file $file_path found.EXIT now."
        exit
    fi
    file_name=$(basename $file_path)
    last=$(echo -e "$file_name"|cut -d. -f2|column -t)
    if [ "$last" == "sh" ];then
        script_type="shell"
    elif [ "$last" == "py" ];then
        script_type="python"
    elif [ "$last" == "pl" ];then
        script_type="perl"
    elif [ "$last" == "php" ];then
        script_type="php"
    else
        script_type="unknown"
    fi
    echo -e "$script_type"
}

function check_os()
{
    if [ -f "/etc/os-release" ];then
        suse_N=$(cat /etc/os-release|egrep -i suse|wc -l)
        ubuntu_N=$(cat /etc/os-release|egrep -i ubuntu|wc -l)
        redhat_N=$(cat /etc/os-release|egrep -i rehl|wc -l)
        centos_N=$(cat /etc/os-release|egrep -i cent|wc -l)
        if [ $suse_N -ge 1 ];then
            echo -e "suse"
        elif [ $ubuntu_N -ge 1 ];then
            echo -e "ubuntu"
        elif [ $redhat_N -ge 1 ];then
            echo -e "redhat"
        elif [ $centos_N -ge 1 ];then
            echo -e "centos"
        else
            echo -e "unknown"
        fi
    else
        echo -e "unknown"
    fi
}

function check_already()
{
    local file_path=$1
    local si_path="$2"
    if [ ! -f $file_path ];then
        echo -e "Sorry..No file $file_path found.EXIT now."
        exit
    fi
    file_name=$(basename $file_path)
    N=`ps -e faux -j|egrep "$file_name"|egrep "$si_path"| egrep -v grep|wc -l`
    if [ "$(check_os)" == "suse" ];then
        the_check_N=3
        the_check_N_2=3
    elif [ "$(check_os)" == "ubuntu" ];then
        the_check_N=4
        the_check_N_2=3
    else
        the_check_N=4
        the_check_N_2=4
    fi
    if [ $N -gt $the_check_N ];then
        echo -e "yes"
    elif [ $N -eq $the_check_N -o $N -eq $the_check_N_2 ];then
        echo -e "no"
    else
        echo -e "Fuck...I don't know what is going wrong.."
        exit
    fi
}

function check_already_2()
{
    local file_path="$1"
    shift
    local other_args="$*"
    #echo -e "file_path [$file_path] other_args [$other_args]" >> /tmp/kk_1
    if [ ! -f $file_path ];then
        echo -e "Sorry..No file $file_path found.EXIT now."
        exit
    fi
    file_name=$(basename $file_path)
    si_check_process_file="/var/lock/si/${file_name}"
    if [ ! -d "/var/lock/si" ];then
        mkdir -p /var/lock/si
    fi
    if [ ! -f "$si_check_process_file" ];then
        echo -e "$file_name $other_args" > $si_check_process_file
        echo -e "no"
    else
        local N=$(cat $si_check_process_file|egrep "^$file_name $other_args$"|wc -l)
        if [ $N -ge 1 ];then
            echo -e "yes"
        else
            echo -e "no"
            echo -e "$file_name $other_args" >> $si_check_process_file
        fi
    fi
}


function after_this_run()
{
    local file_path="$1"
    shift
    local other_args="$*"
    #echo -e "file_path [$file_path] other_args [$other_args]" >> /tmp/kk_2
    file_name=$(basename $file_path)
    si_check_process_file="/var/lock/si/$file_name"
    if [ ! -d "/var/lock/si" ];then
        mkdir -p /var/lock/si
    fi
    si_check_process_file_tmp="${si_check_process_file}_tmp"
    cat $si_check_process_file |egrep -v -w "^$file_name $other_args$" > $si_check_process_file_tmp
    mv $si_check_process_file_tmp $si_check_process_file
}

function main()
{
    if [ "$(is_root)" != "yes" ];then
        echo -e "You should run me by root"
        exit 1
    fi
    #source the system environment
    . /etc/profile
    . /root/.bashrc
    . ~/.bashrc
    #
    if [ $# -lt 1 ];then
        usage
    fi
    si_path="$0"
    file=$1
    if [ ! -f "$file" ];then
        echo -e "[$file] not found"
        echo -e "[`date +%F_%T`] [$file] not found" >> $first_log_path
        exit 2
    fi
    shift 1
    other_args="$*"
    use_own="no"
    file_name=$(basename $file)
    make_the_log_dirs $file_name
    return_type=$(get_the_script_type $file)
    return_already=$(check_already_2 $file $other_args)
    cd_into_right_path $file

    if [ "$return_type" == "shell" ];then
        log_path="$shell_log"
    elif [ "$return_type" == "python" ];then
        log_path="$python_log"
    elif [ "$return_type" == "perl" ];then
        log_path="$perl_log"
    elif [ "$return_type" == "php" ];then
        log_path="$php_log"
    elif [ "$return_type" == "unknown" ];then
        log_path="$unknown_log"
    else:
        log_path="$unknown_log"
    fi

    #deal with the script...
    if [ "$return_already" == "yes" ];then
        echo -e "Already one guy doing something...OK..Let's have a rest..See you later...^__^..." >> $log_path
        exit
    elif [ "$return_already" == "no" ];then
        echo -e "OK...Let's rock it...Baby..^__^..." >> $log_path
        sleep 1
        run_bin $si_path $file_name $return_type $other_args
        after_this_run $file $other_args
    else
        echo -e "Hello...Is anybody here?...Something is going wrong...EXIT now.." >> $log_path
        exit
    fi
}

main $*
