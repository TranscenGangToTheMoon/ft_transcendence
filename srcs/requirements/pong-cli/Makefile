########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
INCS		:=	\
				colors.h\
				pong-cli.h\

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
LIB_D		:=	lib

CURL		:=	\
				libcurl.a\

CURL_D		:=	$(LIB_D)/curl

CURL_I		:=	$(CURL_D)/include

CURL_M		:=	$(CURL_D)/Makefile

CURL_A		:=	$(CURL:%=$(CURL_D)/build/%)

CURL_F		:=	-L$(CURL_D)/lib/.libs -lcurl

#####FTXUI LIB
FTXUI		:=	\
				libftxui-component.a\
				libftxui-dom.a\
				libftxui-screen.a

FTXUI_D		:=	$(LIB_D)/ftxui

FTXUI_I		:=	$(LIB_D)/ftxui/include/

FTXUI_A		:=	$(FTXUI:%=$(FTXUI_D)/build/%)

FTXUI_F		:=	-L$(FTXUI_D)/build/ -lftxui-component -lftxui-dom -lftxui-screen

#LIBS		:=	$(FTXUI_A) #$(CURL_A)
########################################################################################################################
#                                                        FLAGS                                                         #
########################################################################################################################
CXX			:=	c++ -std=c++17

RM			:=	rm -rf

IFLAGS		:=	-I$(INCS_D) -I$(FTXUI_I) -I$(CURL_I)

DFLAGS		=	-MMD -MP -MT $@ -MF $(DEPS_D)$*.d

OFLAGS		:=	-O3 #-Ofast -march=native -fomit-frame-pointer -funroll-loops

CXXFLAGS	=	-Wall -Wextra -Werror -g $(IFLAGS) $(OFLAGS) $(DFLAGS)

LFLAGS		= 	$(FTXUI_F) $(CURL_F) #-lssl -lcrypto

ARGS		?=	#

########################################################################################################################
#                                                        DEBUG                                                         #
########################################################################################################################
DEBUG		=	no

ifeq ($(DEBUG), yes)
	CXXFLAGS	+=	-fsanitize=address
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

.PHONY: all
all			:	$(NAME) banner

$(NAME)		:	ftxui curl $(OBJS)
			$(CXX) $(CXXFLAGS) -o $(NAME) $(OBJS) $(LFLAGS)

$(OBJS)		:	$(OBJS_D)%.o: $(SRCS_D)%.cpp | $(OBJS_D) $(DEPS_D)
			$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJS_D)	:
			mkdir -p $(OBJS_D)

$(DEPS_D)	:
			mkdir -p $(DEPS_D)

$(LIBS)		:	ftxui

.PHONY: ftxui
ftxui		:	$(FTXUI_D) FORCE
			cmake $(FTXUI_D) -B $(FTXUI_D)/build .
			make -C $(FTXUI_D)/build

$(FTXUI_D)	:
			git clone --depth 1 --branch v5.0.0 https://github.com/ArthurSonzogni/FTXUI.git $@

.PHONY: curl
curl		:	$(CURL_D) $(CURL_M) FORCE
			make -C $(CURL_D)

$(CURL_M)	:
			cd $(CURL_D) ; ./configure --with-openssl --without-libpsl

$(CURL_D)	:
			curl -o	$@.tar.gz https://curl.se/download/curl-8.11.0.tar.gz
			mkdir	$@
			tar -xf	$@.tar.gz	-C $@ --strip-components=1
			rm -rf	$@.tar.gz

.PHONY: leaks
leaks		:	$(NAME)
			$(VALGRIND) ./$(NAME) $(ARGS)

.PHONY: run
run			:	$(NAME)
			./$(NAME) $(ARGS)

.PHONY: fsan
fsan		:
			$(MAKE) fclean $(NAME) DEBUG=yes

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

.PHONY: clean
clean		:
			$(RM) $(OBJS) $(OBJS_D) $(DEPS_D) $(OBJS_B_D) $(DEPS_B_D)

.PHONY: fclean
fclean		:	clean
			$(RM) $(NAME) $(NAME_B)
			rm -rf $(LIB_D)/ftxui $(LIB_D)/curl

.PHONY: re
re			:	fclean all

.PHONY: FORCE
FORCE		: