GREEN="\[$(tput setaf 2)\]"
RESET="\[$(tput sgr0)\]"
BOLD="\[$(tput bold)\]"

LOCAL_PROJ="/c/Users/schunckf/Documents/Florian/papers/nanocosm"
Y_PROJ="/y/Home/schunckf/papers/nanocosm"
x=""
if [ -n ${VIRTUAL_ENV} ]; then
    VENV=`basename $VIRTUAL_ENV`;
    VENV="(${VENV}) "
else
    VENV="";
fi

alias cdy='cd $Y_PROJ'
alias cdl='cd $LOCAL_PROJ'

# PS1="${GREEN}my prompt${RESET}> "
PS1="${VENV}${RESET}${GREEN}\w${RESET}${BOLD} $ ${RESET}"