# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history. See bash(1) for more options
# ... or force ignoredups and ignorespace
HISTCONTROL=ignoredups:ignorespace

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
#alias l='ls -CF'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
#if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
#    . /etc/bash_completion
#fi




alias rm='rm'
alias ssh-set='eval `ssh-agent`; ssh-add'
alias suu='sudo su '
alias ss='ssh -C -X -l hamada'
alias ssj='ssh -C -X -l xu30 xd1gate.cray.co.jp'
alias ssc='ssh -C -X -l hhd096 xd1'
alias langj='export LANG=ja_JP.eucJP'
alias langc='export LANG=C'
alias cd='pushd ./ 1>/dev/null 2>/dev/null;echo $PWD;cd $ARG'
alias bk='dirs +2;popd 1>/dev/null 2>/dev/null;' 
alias er='rm -r *~'
alias err='rm -r .*~'
alias mule='emacs' 
alias cls='clear'
alias l='emacs -nw'
alias ls='ls -F --color=tty'
alias la='ls -la --color=tty'
alias ll='ls -l --color=tty'
alias less='less -X'
alias sch='source ~/.bashrc; echo .bashrc'
alias kterm='kterm -fg wheat -bg black -km euc -sl 2000'
alias xterm='xterm -bg "#001f33" -fg "#FFF0F0"'
alias console='kterm -T gentoo -bg "#777777" -fg "#ffffff"'
alias setx='xsetroot -mod 2 2 -fg "#003322" -bg "#003322"'

alias amek='make'
alias amke='make'
alias mkae='make'
alias muel='mule'
alias moer='more'
alias mroe='more'
alias mre='more'
alias meor='more'
alias sl='ls'

# Ubuntu
#export LANG=C

# ATI Stream
export ATISTREAMSDKROOT=/opt/green/ati-stream-sdk-v2.3-lnx64
export ATISTREAMSDKSAMPLESROOT=/opt/green/ati-stream-sdk-v2.3-lnx64/samples
export LD_LIBRARY_PATH=$ATISTREAMSDKROOT/lib/x86_64:$LD_LIBRARY_PATH

# ATI sample bin
export PATH=$PATH:/opt/green/ati-stream-sdk-v2.3-lnx64/samples/cal/bin/x86_64
export PATH=$PATH:/opt/green/ati-stream-sdk-v2.3-lnx64/samples/opencl/bin/x86_64


# OpenMPI IB
export PATH=/usr/mpi/gcc/openmpi-1.4.3/bin:$PATH
export LD_LIBRARY_PATH=/usr/mpi/gcc/openmpi-1.4.3/lib64:$LD_LIBRARY_PATH

# export-bin
export PATH=$PATH:/export/opt/bin



