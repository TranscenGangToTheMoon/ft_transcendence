########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
INCS		:=	\
				colors.h\

SRCS		:=	\
				main.cpp\

INCS_D		:=	incs/

SRCS_D		:=	srcs/

OBJS_D		:=	objs/

DEPS_D		:=	deps/

OBJS		:=	$(SRCS:%.cpp=$(OBJS_D)%.o)

DEPS		:=	$(SRCS:%.cpp=$(DEPS_D)%.d)

NAME		:=	pong-cli

########################################################################################################################
#                                                         LIB                                                          #
########################################################################################################################
FTXUI			:=	\
					libftxui-component.a\
					libftxui-dom.a\
					libftxui-screen.a

FTXUI_D			:=	ftxui/

FTXUI_I			:=	ftxui/include/

FTXUI_A			:=	$(FTXUI:%=$(FTXUI_D)/build/%)

FTXUI_F			:=	-L$(FTXUI_D)build/ -lftxui-component -lftxui-dom -lftxui-screen

########################################################################################################################
#                                                        FLAGS                                                         #
########################################################################################################################
CC			:=	c++ -std=c++17

RM			:=	rm -rf

IFLAGS		:=	-I$(INCS_D) -I$(FTXUI_I)

DFLAGS		=	-MMD -MP -MT $@ -MF $(DEPS_D)$*.d

CFLAGS		=	-Wall -Wextra -Werror -g3 $(IFLAGS)

OFLAGS		:=	-O3 #-Ofast -march=native -fomit-frame-pointer -funroll-loops

ARGS		?=	#

########################################################################################################################
#                                                        DEBUG                                                         #
########################################################################################################################
DEBUG		=	no

ifeq ($(DEBUG), yes)
	CFLAGS	+=	-fsanitize=address
endif

IGN_LEAK	:=	valgrind_ignore_leaks.txt

VALGRIND	:=	valgrind --leak-check=full --show-leak-kinds=all\
				--track-fds=yes --show-mismatched-frees=yes --read-var-info=yes --track-origins=yes -s
#				--default-suppressions=no

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
-include $(DEPS)

.DEFAULT_GOAL = all

all			:	$(NAME) banner #mlx

$(NAME)		:	$(OBJS) $(FTXUI_A)
			$(CC) $(CFLAGS) $(OFLAGS) -o $(NAME) $(OBJS) $(FTXUI_F)

$(OBJS)		:	$(OBJS_D)%.o: $(SRCS_D)%.cpp | $(OBJS_D) $(DEPS_D)
			$(CC) $(CFLAGS) $(OFLAGS) $(DFLAGS) -c $< -o $@

$(OBJS_D)	:
			mkdir -p $(OBJS_D)

$(DEPS_D)	:
			mkdir -p $(DEPS_D)

ftxui		:
			cmake $(FTXUI_D) -B $(FTXUI_D)build . && make -C $(FTXUI_D)build

$(FTXUI_A)	:	FORCE
			cmake $(FTXUI_D) -B $(FTXUI_D)build . && make -C $(FTXUI_D)build
# mlx			:
# 			cmake $(MLX_D) -B $(MLX_D)/build && make -C $(MLX_D)/build -j4
#$(MLX_A)	:	FORCE
#			$(MAKE) -C $(MLX_D) 2>/dev/null

leaks		:	$(NAME)
			$(VALGRIND) ./$(NAME) $(ARGS)

run			:	$(NAME)
			./$(NAME) $(ARGS)

fsan		:
			$(MAKE) fclean $(NAME) DEBUG=yes

########################################################################################################################
#                                                    MISCELLANEOUS                                                     #
########################################################################################################################
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



clean		:
			$(RM) $(OBJS) $(OBJS_D) $(DEPS_D) $(OBJS_B_D) $(DEPS_B_D)

fclean		:	clean
			$(RM) $(NAME) $(NAME_B)
			rm -rf ftxui/build/
#			$(MAKE) fclean -C $(LIB_D)
#			$(MAKE) clean -C $(MLX_D)

re			:	fclean all

FORCE		:

.PHONY		:	all debug leaks re clean fclean FORCE