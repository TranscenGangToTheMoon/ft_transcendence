########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
NAME		:=	pongCLI

SRCS_D		:=	srcs

REQ_FILES	:=	requirements.txt

VENV		:=	.venv

TERMINAL	:=	gnome-terminal

SHELL		:=	/bin/zsh

SOURCE		:=	source $(VENV)/bin/activate

ARGS		?=	-x SYSTEM -x EVENT -x DEBUG -x INFO# Leave empty

CLI_FLAGS	?=	-s localhost:4443 -u xcharra -p Azerty43## Leave empty
########################################################################################################################
#                                                        COLORS                                                        #
########################################################################################################################
BLUE		:=	\001\033[34m\002

BOLD		:=	\001\033[1m\002

ITALIC		:=	\001\033[3m\002

RESET		:=	\001\033[0m\002

########################################################################################################################
#                                                        RULES                                                         #
########################################################################################################################
.DEFAULT_GOAL = all

.PHONY: all
all			:	.venv

$(VENV)		:	$(VENV)/ts banner

$(VENV)/ts	:	$(REQ_FILES)
			python3 -m venv $(@D)
			$(SOURCE); pip install -r $<
			touch $@

.PHONY: run
run			:	.venv
			$(SOURCE); python srcs/$(NAME).py $(CLI_FLAGS)

.PHONY: debug
debug		:	.venv
			$(SOURCE); textual run --dev "srcs/$(NAME).py $(CLI_FLAGS)"

.PHONY: console
console		:	.venv
			$(SOURCE); textual console $(ARGS)

.PHONY: free-run
free-run	:	.venv
			$(TERMINAL) -- $(SHELL) -c "$(SOURCE); python srcs/$(NAME).py $(CLI_FLAGS)"

.PHONY: free-debug
free-debug	:	.venv
			$(TERMINAL) -- $(SHELL) -c "$(SOURCE); textual run --dev \"srcs/$(NAME).py $(CLI_FLAGS)\""

.PHONY: free-console
free-console:	.venv
			$(TERMINAL) -- $(SHELL) -c "$(SOURCE); textual console $(ARGS)"

.PHONY: debug-cons
debug-cons	:	.venv free-console debug

.PHONY: cons-debug
cons-debug	:	.venv free-debug console

########################################################################################################################
#                                                    MISCELLANEOUS                                                     #
########################################################################################################################
.PHONY: banner
banner		:
			@echo -en '$(BLUE)'
			@echo -e '                                        ___ '
			@echo -e '    ____  ____  ____  ____ _      _____/ (_)'
			@echo -e '   / __ \/ __ \/ __ \/ __ `/_____/ ___/ / / '
			@echo -e '  / /_/ / /_/ / / / / /_/ /_____/ /__/ / /  '
			@echo -e ' / .___/\____/_/ /_/\__, /      \___/_/_/   '
			@echo -e '/_/                /____/                   '
			@echo -en '$(BOLD)''$(ITALIC)'
			@echo -e '                           🍦   xcharra'
			@echo -e '$(RESET)'

.PHONY: fclean
fclean		:
			$(RM) -r $(VENV)
			$(RM) ft_transcendence.crt

.PHONY: re
re			:	fclean all
