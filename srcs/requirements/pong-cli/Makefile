########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
NAME		:=	pongCLI

REQ_FILES	:=	requirements.txt

VENV		:=	.venv

TERMINAL	:=	gnome-terminal

SHELL		:=	/bin/zsh

ARGS		?=	# Leave empty
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
all			:	banner .venv

$(VENV)		:	$(VENV)/ts

$(VENV)/ts	:	$(REQ_FILES)
			python3 -m venv $(VENV)
			source $(VENV)/bin/activate ; pip install -r $(REQ_FILES)
			touch $(VENV)/ts

.PHONY: run
run			:	.venv
			python srcs/$(NAME).py

.PHONY: debug
debug		:	.venv
			textual run --dev srcs/$(NAME).py

.PHONY: debug-cons
debug-cons	:	.venv console
			textual run --dev srcs/$(NAME).py

.PHONY: console-here
console-here:
			textual console $(ARGS)

.PHONY: console
console		:	.venv
			$(TERMINAL) -- $(SHELL) -c "printf \"\\e[8;60;150t\"; source $(VENV)/bin/activate ; textual console $(ARGS)"

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
			$(RM) -rf $(VENV)

.PHONY: re
re			:	fclean all
