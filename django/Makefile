
# ---------- VARIABLES ----------------------------------------------------------------------------------------------- #
NAME				=	transcendence_postgre_db
HOST_PATH			=	./postgre_data/
CONTAINER_PATH		=	/var/lib/postgresql/data

POSTGRES_USER		=	fguirama
POSTGRES_PASSWORD	=	123456
POSTGRES_DB			=	auth_db
PORT				=	5432
PORTS				=	$(PORT):$(PORT)
VOLUMES				=	$(HOST_PATH):$(CONTAINER_PATH)

POSTGRES_IP			=	$(shell ifconfig -u | grep 'inet ' | grep -v 127.0.0.1 | cut -d\  -f2 | head -1)


# ---------- RULES --------------------------------------------------------------------------------------------------- #
all:				$(NAME)

$(NAME):			$(HOST_PATH)
					docker run --name $(NAME) -e POSTGRES_USER=$(POSTGRES_USER) -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) -p ${PORTS} -v $(VOLUMES) -d postgres:14

up:
					docker start $(NAME)

it:
					docker exec -it $(NAME) bash

connect:
					psql -h $(POSTGRES_IP) -p $(PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) -W

ps:
					docker ps

restart:
					docker restart $(NAME)

clean:
					docker stop $(NAME)

fclean:
					docker rm $(NAME)
					rm -rf $(HOST_PATH)

prune:
					docker system prune -af

re:					fclean all

$(HOST_PATH):
					mkdir -p $@

.PHONY:				all clean fclean prune re