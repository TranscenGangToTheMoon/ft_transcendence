cmake_minimum_required(VERSION 3.22)

project(pongCLI CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "-Wall -Wextra -Werror")
#set(CMAKE_CXX_LINK_LIBRARY_FLAG "-lftxui")
#find_package(CURL REQUIRED)

include_directories(incs)
include(FetchContent)

FetchContent_Declare(ftxui
		GIT_REPOSITORY https://github.com/ArthurSonzogni/ftxui
		GIT_TAG v5.0.0
)
FetchContent_MakeAvailable(FTXUI)

FetchContent_Declare(curl
		URL https://curl.se/download/curl-8.11.0.tar.gz
)
FetchContent_MakeAvailable(curl)

find_package(curl)

set(SRCS
	srcs/CurlWrapper.cpp
	srcs/main.cpp
	srcs/PongCLI.cpp
	srcs/User.cpp
)

set(INCS
	incs/colors.h
	incs/CurlWrapper.hpp
	incs/pong-cli.h
	incs/PongCLI.hpp
	incs/User.hpp
)

add_executable(pongCLI ${SRCS} ${INCS})

target_link_libraries(pongCLI
		PRIVATE ftxui::screen
		PRIVATE ftxui::dom
		PRIVATE ftxui::component
)

target_link_libraries(pongCLI
		PRIVATE libcurl
)