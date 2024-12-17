########################################################################################################################
#                                                       VARIABLE                                                       #
########################################################################################################################
INCS		:=	\
				colors.h\
				pong-cli.h\
				PongCLI.hpp\
				Renderer.hpp\
				User.hpp

SRCS		:=	\
				CurlWrapper.cpp\
				PongCLI.cpp\
				User.cpp\
				main.cpp\

INCS_D		:=	incs/

SRCS_D		:=	srcs/

OBJS_D		:=	objs/

DEPS_D		:=	deps/

OBJS		:=	$(SRCS:%.cpp=$(OBJS_D)%.o)

DEPS		:=	$(SRCS:%.cpp=$(DEPS_D)%.d)

NAME		:=	pong-cli

CERT		:=	ft_transcendence.crt

########################################################################################################################
#                                                         LIB                                                          #
########################################################################################################################
LIB_D		:=	lib

###############cURL###############
CURL		:=	\
				libcurl.a\

CURL_D		:=	$(LIB_D)/curl

CURL_I		:=	$(CURL_D)/include

CURL_M		:=	$(CURL_D)/Makefile

CURL_A		:=	$(CURL:%=$(CURL_D)/%)

CURL_F		:=	-L$(CURL_D)/lib/.libs -lcurl

###############FTXUI###############
FTXUI		:=	\
				libftxui-component.a\
				libftxui-dom.a\
				libftxui-screen.a

FTXUI_D		:=	$(LIB_D)/ftxui

FTXUI_I		:=	$(FTXUI_D)/include

FTXUI_A		:=	$(FTXUI:%=$(FTXUI_D)/build/%)

FTXUI_F		:=	-L$(FTXUI_D)/build/ -lftxui-component -lftxui-dom -lftxui-screen

###############JSON###############
JSON		:=	\

JSON_D		:=	$(LIB_D)/json

JSON_I		:=	$(JSON_D)/single_include

JSON_A		:=	$(JSON:%=$(JSON_D)/build/%)

################SOCKT###############
#SOKCT		:=	\
#				libsioclient.a\
#				libsioclient_tls.a
#
#SOKCT_D		:=	$(LIB_D)/socketio
#
#SOKCT_I		:=	$(SOKCT_D)/src
#
#SOKCT_A		:=	$(SOKCT:%=$(SOKCT_D)/build/%)
#
#SOKCT_F		:=	-L$(SOKCT_D)/build/ -lsioclient_tls

###############BOOST###############
BOOST		:=	\

BOOST_D		:=	$(LIB_D)/boost

BOOST_I		:=	\
				-I$(BOOST_D)/libs/asio/include\
				-I$(BOOST_D)/libs/beast/include\
				-I$(BOOST_D)/libs/config/include\
				-I$(BOOST_D)/libs/assert/include\
				-I$(BOOST_D)/libs/throw_exception/include\
				-I$(BOOST_D)/libs/system/include\
				-I$(BOOST_D)/libs/date_time/include\
				-I$(BOOST_D)/libs/smart_ptr/include\
				-I$(BOOST_D)/libs/core/include\
				-I$(BOOST_D)/libs/utility/include\
				-I$(BOOST_D)/libs/static_assert/include\
				-I$(BOOST_D)/libs/type_traits/include\
				-I$(BOOST_D)/libs/numeric/conversion/include\
				-I$(BOOST_D)/libs/mpl/include\
				-I$(BOOST_D)/libs/preprocessor/include\
				-I$(BOOST_D)/libs/optional/include\
				-I$(BOOST_D)/libs/mp11/include\
				-I$(BOOST_D)/libs/bind/include\
				-I$(BOOST_D)/libs/intrusive/include\
				-I$(BOOST_D)/libs/move/include\
				-I$(BOOST_D)/libs/logic/include\
				-I$(BOOST_D)/libs/static_string/include\
				-I$(BOOST_D)/libs/container_hash/include\
				-I$(BOOST_D)/libs/describe/include\
				-I$(BOOST_D)/libs/io/include\
				-I$(BOOST_D)/libs/endian/include\


BOOST_A		:=	$(BOOST:%=$(BOOST_D)/build/%)

BOOST_F		:=	#-L$(BOOST_D)/build/
########################################################################################################################
#                                                        FLAGS                                                         #
########################################################################################################################
CXX			:=	c++ -std=c++17

MFLAGS		:=	--jobs=$(shell nproc)

RM			:=	rm -rf

IFLAGS		:=	-I$(INCS_D) -I$(FTXUI_I) -I$(CURL_I) -I$(JSON_I) $(BOOST_I)

DFLAGS		=	-MMD -MP -MT $@ -MF $(DEPS_D)$*.d

OFLAGS		:=	#-O3 #-Ofast -march=native -fomit-frame-pointer -funroll-loops

CXXFLAGS	=	-Wall -Wextra -Werror -g  $(IFLAGS) $(OFLAGS) $(DFLAGS)

LFLAGS		= 	$(FTXUI_F) $(CURL_F) $(SOKCT_F) -lssl -lcrypto

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

$(NAME)		:	ftxui curl json socketio $(CERT) $(OBJS)
			$(CXX) $(CXXFLAGS) -o $(NAME) $(OBJS) $(LFLAGS)

$(OBJS)		:	$(OBJS_D)%.o: $(SRCS_D)%.cpp $(FTXUI_D) $(CURL_D) $(JSON_D) $(SOKCT_D) | $(OBJS_D) $(DEPS_D)
			$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJS_D)	:
			mkdir -p $(OBJS_D)

$(DEPS_D)	:
			mkdir -p $(DEPS_D)

.PHONY: ftxui
ftxui		:	$(FTXUI_D)
			cmake $(FTXUI_D) -B $(FTXUI_D)/build
			$(MAKE) $(MFLAGS) -C $(FTXUI_D)/build

$(FTXUI_D)	:
			git clone --depth 1 --branch v5.0.0 https://github.com/ArthurSonzogni/FTXUI.git $@

.PHONY: curl
curl		:	$(CURL_M)
			$(MAKE) $(MFLAGS) -C $(CURL_D)

$(CURL_M)	:	$(CURL_D)
			@if [ ! -f $@ ]; then \
				cd $< ; ./configure --with-openssl --without-libpsl; \
			fi

$(CURL_D)	:
			curl -o	$@.tar.gz https://curl.se/download/curl-8.11.0.tar.gz
			mkdir	$@
			tar -xf	$@.tar.gz	-C $@ --strip-components=1
			rm -rf	$@.tar.gz

.PHONY: json
json		:	$(JSON_D)
			cmake $(JSON_D) -B $(JSON_D)/build
			$(MAKE) $(MFLAGS) -C $(JSON_D)/build

$(JSON_D)	:
			git clone --depth 1 --branch v3.11.3 git@github.com:nlohmann/json.git $@

#.PHONY: socketio
#socketio	:	$(SOKCT_D)
#			cmake $(SOKCT_D) -B $(SOKCT_D)/build -DCMAKE_CXX_FLAGS="-DSIO_TLS"
#			$(MAKE) $(MFLAGS) -C $(SOKCT_D)/build
#
#$(SOKCT_D)	:
#			git clone --recurse-submodules --depth 1 https://github.com/socketio/socket.io-client-cpp.git  $@

.PHONY: boost
boost		:	$(BOOST_D)
			cmake $(BOOST_D) -B $(BOOST_D)/build
			$(MAKE) $(MFLAGS) -C $(BOOST_D)/build

$(BOOST_D)	:
			curl -o	$@.tar.gz -L https://github.com/boostorg/boost/releases/download/boost-1.87.0/boost-1.87.0-cmake.tar.gz
			mkdir	$@
			tar -xf	$@.tar.gz	-C $@ --strip-components=1
			rm -rf	$@.tar.gz

$(CERT)		:
			openssl s_client -connect localhost:4443 -servername localhost </dev/null \
				| sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > $(CERT)

.PHONY: run
run			:	$(NAME)
			./$(NAME) $(ARGS)

.PHONY: fast
fast		:	$(OBJS)
			$(CXX) $(CXXFLAGS) -o $(NAME) $(OBJS) $(LFLAGS)

.PHONY: run/fast
run/fast	:	fast
			./$(NAME) $(ARGS)

.PHONY: leaks/fast
leaks/fast	:	fast
			$(VALGRIND) ./$(NAME) $(ARGS)

.PHONY: leaks
leaks		:	$(NAME)
			$(VALGRIND) ./$(NAME) $(ARGS)

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
			$(RM) $(LIB_D)
			$(RM) $(CERT)

.PHONY: re
re			:	fclean all

.PHONY: FORCE
FORCE		: