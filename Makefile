########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
NAME		:=	ft_transcendence

SRCS_D		:=	srcs

SECRETS_D	:=	secrets/

ENV_EXEMPLE	:=	.env_exemple

ENV_FILE	:=	./$(SRCS_D)/.env

COMPOSE_F	:=	./$(SRCS_D)/docker-compose-dev.yml

SERVICE		?=	#Leave blank

########################################################################################################################
#                                                        FLAGS                                                         #
########################################################################################################################
FLAGS		=	-f $(COMPOSE_F)

COMPOSE		=	docker compose

DSHELL		=	sh -c bash
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

all			:	banner $(NAME)

$(NAME)		:	secrets
			$(COMPOSE) $(FLAGS) up --build $(SERVICE)

build		:
			$(COMPOSE) $(FLAGS) $@ $(SERVICE)

up			:	build
			$(COMPOSE) $(FLAGS) $@ $(SERVICE)

down		:
			$(COMPOSE) $(FLAGS) $@ $(SERVICE)

dettach		:	build
			$(COMPOSE) $(FLAGS) up -d $(SERVICE)

exec		:
			$(COMPOSE) $(FLAGS) $@ $(SERVICE) $(DSHELL)

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

secrets		:	$(ENV_FILE) #if secrets directory are needed delete phony secrets
#			mkdir $@

$(ENV_FILE)	:	$(ENV_EXEMPLE)
			./launch.d/01passwords.sh $(ENV_EXEMPLE) $(ENV_FILE)

clean		:
			$(COMPOSE) $(FLAGS) down --rmi local --remove-orphans
#			rm -rf $(ENV_FILE)
#			rm -rf $(SECRETS_D)

vclean		:
			$(COMPOSE) $(FLAGS) down -v --remove-orphans
			rm -rf $(ENV_FILE)

fclean		:
			$(COMPOSE) $(FLAGS) down -v --rmi all --remove-orphans
			docker image prune -af
			rm -rf $(VOLS_PATH)
			rm -rf $(ENV_FILE)
#			rm -rf $(SECRETS_D)

dusting		:
			find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
			find . -path "*/__pycache__/*" -delete
			find . -path "*/__pycache__" -delete
#			rm -rf `find . | grep __init__.py`
#			rm -rf `find . | grep db.sqlite3`

caddy-reload:
			$(COMPOSE) $(FLAGS) exec -w /etc/caddy frontend caddy reload

image-ls	:
			docker image ls -a
image-rm	:
			docker image rm `docker image ls -qa`

container-ls:
			docker container ls -a
container-rm:
			echo docker container rm `docker container ls -qa`

volume-ls	:
			docker volume ls
volume-rm	:
			docker volume rm `docker volume ls -qa`

network-ls	:
			docker network ls
network-rm	:
			docker network rm `docker network ls -qa`

prune		:
			docker system prune -af

sre			:	clean all

vre			:	vclean all

re			:	fclean all

.PHONY		:	all volumes build up down dettach banner secrets clean vclean \
			fclean image-ls image-rm container-ls container-rm volume-ls \
			volume-rm network-ls network-rm prune sre vre re
