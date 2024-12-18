cmake_minimum_required(VERSION 3.16)

project(pongCLI CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_CXX_FLAGS "-Wall -Wextra -Werror")
#set(CMAKE_CXX_LINK_LIBRARY_FLAG "-lftxui")

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

set(BOOST_INCLUDE_LIBRARIES asio beast)
set(BOOST_ENABLE_CMAKE ON)

include(FetchContent)
FetchContent_Declare(
		Boost
		GIT_REPOSITORY https://github.com/boostorg/boost.git
		GIT_TAG boost-1.87.0
)
FetchContent_MakeAvailable(Boost)

FetchContent_Declare(json
		URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
)
FetchContent_MakeAvailable(json)

#FetchContent_Declare(boost
#		URL https://github.com/boostorg/boost/releases/download/boost-1.87.0/boost-1.87.0-cmake.tar.xz
#)
#FetchContent_MakeAvailable(boost)

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
#		PRIVATE ftxui::screen
#		PRIVATE ftxui::dom
#		PRIVATE ftxui::component
#		PRIVATE libcurl
#		PRIVATE nlohmann_json::nlohmann_json
		PRIVATE Boost::asio
		PRIVATE Boost::beast
)
