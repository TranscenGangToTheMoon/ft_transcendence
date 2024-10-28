########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
NAME		:=	ft_transcendence

SRCS_D		:=	srcs

SECRETS_D	:=	secrets/

VOLS		:=	\
				auth-db\
				chat-db\
				game-db\
				matchmaking-db\
				users-db\

VOLS_PATH	:=	$(HOME)/transcendence/

VOLUMES		:=	$(addprefix $(VOLS_PATH),$(VOLS))

ENV_EXEMPLE	:=	.env_exemple

ENV_FILE	:=	./srcs/.env

########################################################################################################################
#                                                        FLAGS                                                         #
########################################################################################################################
FLAGS		=	--project-directory $(SRCS_D)

COMPOSE		=	docker compose

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

$(NAME)		:	volumes secrets
			$(COMPOSE) $(FLAGS) up --build

volumes		:	$(VOLUMES)

$(VOLUMES)	:
			mkdir -p $@

build		:
			$(COMPOSE) $(FLAGS) $@

up			:	build
			$(COMPOSE) $(FLAGS) $@

down		:
			$(COMPOSE) $(FLAGS) $@

dettach		:	build
			$(COMPOSE) $(FLAGS) up -d

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
			$(COMPOSE) $(FLAGS) down -v --rmi local
			docker run --rm -v $(VOLS_PATH):/transcendence busybox sh -c "rm -rf transcendence/*"
			rm -rf $(ENV_FILE)
#			rm -rf $(SECRETS_D)

fclean		:
			$(COMPOSE) $(FLAGS) down -v --rmi all
			docker run --rm -v $(VOLS_PATH):/transcendence busybox sh -c "rm -rf transcendence/*"
			docker image prune -af
			rm -rf $(VOLS_PATH)
			rm -rf $(ENV_FILE)
#			rm -rf $(SECRETS_D)

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

re			:	fclean all

sre			:	clean all

.PHONY		:	all volumes build up down dettach banner secrets clean fclean \
				image-ls image-rm container-ls container-rm volume-ls volume-rm \
				network-ls network-rm prune re
