########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
NAME		:=	ft_transcendence

SRCS_D		:=	srcs

SECRETS_D	:=	secrets

ENV_EXEMPLE	:=	.env_exemple

ENV_FILE	:=	$(SRCS_D)/.env

CONFIG		:=	gameConfig.json

CONFIG_T	:=	$(SRCS_D)/requirements/frontend/static/

CONFIG_F	:=	$(addsuffix $(CONFIG), $(CONFIG_T))

COMPOSE_F	:=	$(SRCS_D)/docker-compose-dev.yml

SERVICE		?=	#Leave blank

########################################################################################################################
#                                                        FLAGS                                                         #
########################################################################################################################
FLAGS		=	-f $(COMPOSE_F)

COMPOSE		=	docker compose

DSHELL		=	/bin/bash
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
all			:	banner $(NAME)

$(NAME)		:	secrets $(CONFIG_F)
			$(COMPOSE) $(FLAGS) up --build $(SERVICE)

CMDS		:=	up build down ps ls images events top
.PHONY: $(CMDS)
$(CMDS)		:
			$(COMPOSE) $(FLAGS) $@ $(SERVICE)

.PHONY: detach
detach		:
			$(COMPOSE) $(FLAGS) up --$@ $(SERVICE)

.PHONY: logs
logs		:	build
			$(COMPOSE) $(FLAGS) $@ -f $(SERVICE)

.PHONY: exec
exec		:
			$(COMPOSE) $(FLAGS) $@ $(SERVICE) $(DSHELL)

.PHONY: banner
banner		:
			@echo -e '$(BLUE)'
			@echo -e '    ______      __                                            __                   '
			@echo -e '   / __/ /_    / /__________ _____  _____________  ____  ____/ /__  ____  ________ '
			@echo -e '  / /_/ __/   / __/ ___/ __ `/ __ \/ ___/ ___/ _ \/ __ \/ __  / _ \/ __ \/ ___/ _ \'
			@echo -e ' / __/ /_    / /_/ /  / /_/ / / / (__  ) /__/  __/ / / / /_/ /  __/ / / / /__/  __/'
			@echo -e '/_/  \__/____\__/_/   \__,_/_/ /_/____/\___/\___/_/ /_/\__,_/\___/_/ /_/\___/\___/ '
			@echo -en '$(BOLD)''$(ITALIC)'
			@echo -e '                                          bajeanno fguirama jcoquard nfaust xcharra'
			@echo -e '$(RESET)'

secrets		:	$(ENV_EXEMPLE)
			mkdir -p $@
			./launch.d/01generatePasswordsAndKeys.sh
			./launch.d/02genreateSSL.sh

$(CONFIG_F)	:	$(CONFIG)
			cp $< $@

.PHONY: clean
clean		:
			$(COMPOSE) $(FLAGS) down --rmi local --remove-orphans

.PHONY: vclean
vclean		:
			$(COMPOSE) $(FLAGS) down -v --remove-orphans
			rm -rf $(ENV_FILE)
			rm -rf $(SECRETS_D)

.PHONY: fclean
fclean		:	dusting
			$(COMPOSE) $(FLAGS) down -v --rmi all --remove-orphans
			docker system prune -af
			rm -rf $(ENV_FILE)
			rm -rf $(SECRETS_D)
			rm -rf $(CONFIG_F)
			rm -rf $(SRCS_D)/requirements/game/django/gameConfig.json
			rm -rf $(SRCS_D)/requirements/pong-cli/gameConfig.json
			rm -rf $(SRCS_D)/requirements/pong-cli/ft_transcendence.crt

.PHONY: dusting
dusting		:
			find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
			find . -path "*/__pycache__/*" -delete
			find . -path "*/__pycache__" -delete

.PHONY: caddy-reload
caddy-reload:
			$(COMPOSE) $(FLAGS) exec -w /etc/caddy frontend caddy reload

.PHONY: image-ls image-rm
image-ls	:
			docker image ls -a
image-rm	:
			docker image rm `docker image ls -qa`

.PHONY: container-ls container-rm
container-ls:
			docker container ls -a
container-rm:
			docker container rm `docker container ls -qa`

.PHONY: volume-ls volume-rm
volume-ls	:
			docker volume ls
volume-rm	:
			docker volume rm `docker volume ls -qa`

.PHONY: network-ls network-rm
network-ls	:
			docker network ls
network-rm	:
			docker network rm `docker network ls -qa`

.PHONY: prune
prune		:
			docker system prune -af

.PHONY: sre
sre			:	clean all

.PHONY: vre
vre			:	vclean all

.PHONY: re
re			:	fclean all
