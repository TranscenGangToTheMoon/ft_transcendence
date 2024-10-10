########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
NAME		:=	ft_transcentest

SRCS_D		:=	srcs

SECRETS_D	:=	secrets/

VOLS		:=	\
				algo-stats-db\
				authentication-db\
				chat-db\
				game-db

VOLS_PATH	:=	$(HOME)/transcendence/

VOLUMES		:=	$(addprefix $(VOLS_PATH),$(VOLS))

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

$(NAME)		:	volumes #secrets
			$(COMPOSE) $(FLAGS) up --build

volumes		:	$(VOLUMES)

$(VOLUMES)	:
			mkdir -p $@

build		:
			$(COMPOSE) $(FLAGS) $@

up			:	build
			$(COMPOSE) $(FLAGS) $@

dettach		:	build
			$(COMPOSE) $(FLAGS) up -d

banner		:
			@echo -e '$(BLUE)'
			@echo -e '    ______      __                                        __            __ '
			@echo -e '   / __/ /_    / /__________ _____  _____________  ____  / /____  _____/ /_'
			@echo -e '  / /_/ __/   / __/ ___/ __ `/ __ \/ ___/ ___/ _ \/ __ \/ __/ _ \/ ___/ __/'
			@echo -e ' / __/ /_    / /_/ /  / /_/ / / / (__  ) /__/  __/ / / / /_/  __(__  ) /_  '
			@echo -e '/_/  \__/____\__/_/   \__,_/_/ /_/____/\___/\___/_/ /_/\__/\___/____/\__/  '
			@echo -en '$(BOLD)''$(ITALIC)'
			@echo -e '                                                                    xcharra'
			@echo -e '$(RESET)'

clean		:
			$(COMPOSE) $(FLAGS) down

secrets		:
			mkdir $@
			openssl req -x509 -newkey rsa:2048 -keyout ./secrets/ssl.key -out ./secrets/ssl.crt -days 365 -nodes -subj "/CN=xcharra.42.fr"
			openssl rand -hex -out ./secrets/db_pass 32
			openssl rand -hex -out ./secrets/db_root_pass 32
			openssl rand -hex -out ./secrets/wp_admin_pass 32
fclean		:
			# docker run --rm -v $(HOME)/data:/data debian:11 bash -c "rm -rf /data/database/*  /data/wordpress/*"
			# docker run --rm -v $(HOME)/data:/data busybox sh -c "rm -rf /data/database/* /data/wordpress/*"
			docker image prune -af
			$(COMPOSE) $(FLAGS) down -v --rmi all
			rm -rf $(SECRETS_D)

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

.PHONY		: all re clean fclean
