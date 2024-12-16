/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/16 13:17:43 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "PongCLI.hpp"
#include "User.hpp"

#define SERVER	"https://localhost:4443"

int main(void)
{
	{
		CurlWrapper	curl;
		User		user;
//		client	client;

//		client.connect(SERVER);
		curl.setServer(SERVER);
		user.setUsername("xcharra");
		user.setPassword("test");
		curl.addHeader("Content-Type: application/json");

		try {
			user.loginUser(curl);
			std::cout << "Login Succeed" << std::endl;
		}
		catch (std::exception &error) {
			if (curl.getHTTPCode() == 401)
				try {
					user.registerUser(curl);
					std::cout << "Register Succeed" << std::endl;
				}
				catch (std::exception &error) {
					std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
				}
		}

		try {
			curl.POST("/api/play/duel/", "");
			std::cout << "Duel request Succeed" << std::endl;
			std::cout << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
		}
		catch (std::exception &error) {
			std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
			std::cerr << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
		}
	}
	{
//		CurlWrapper	curl;
//		User		user;
//		PongCLI		app(curl, user);
//
//		curl.addHeader("Content-Type: application/json");
////		app.run();
//		app.changePage(PongCLI::Page::MainMenuPage);
//
//		std::cout << "server: " << app.getServer() << std::endl;
//		std::cout << "username: " << app.getUsername() << std::endl;
//		std::cout << "password: " << app.getPassword() << std::endl;
	}
	{
//		CurlWrapper	curl("https://localhost:4443");
//		User		user;
//
//		curl.addHeader("Content-Type: application/json");
//		//login test test
//		user.setUsername("test");
//		user.setPassword("test");
//		try {
//			user.loginUser(curl);
//		}
//		catch (std::exception &error) {
//			std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
//		}
//
////		int			id = 9;
//		std::string	username;
//		bool		guest;
////	profile_picture: None, // not handle yet
////	status: None, // not handle yet
////		int			stardust = 12996;
////		int			aura = 1200;
////	current_rank: None, // not handle yes
////	friends: None,
//		bool		accept_friend_request;
//		bool		accept_chat_from;
//
//		Component	pageComponents = Container::Vertical({
//		});
//		std::string	json;
//		std::string info;
//		try {
//			curl.addHeader("Authorization: Bearer " + user.getAccessToken());
//			curl.GET("/api/users/me/", "");
//			json = curl.getResponse();
//			std::cerr << json << std::endl;
//			info = "id";
////			id = std::stoi(jsonParser(json, "id"));
//			info = "username";
//			username = jsonParser(json, "username");
//			info = "is_guest";
//			guest = jsonParser(json, "is_guest") == "true";
//			info = "coins";
////			stardust = std::stoi(jsonParser(json, "coins"));
//			info = "trophies";
////			aura = std::stoi(jsonParser(json, "trophies"));
//			info = "accept_friend_request";
//			accept_friend_request = jsonParser(json, "accept_friend_request") == "true";
//			info = "accept_chat_from";
//			accept_chat_from = jsonParser(json, "accept_chat_from") == "true";
//			//request to /api/user/me >> get user information
//		}
//		catch (std::exception &error) {
//			std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what() + info) << std::endl;
//		}
	}
	return (0);
}

//std::string generateCustomID(size_t length) {
//	const char charset[] = "0123456789abcdef";
//	const s	xize_t charsetSize = sizeof(charset) - 1;
//
//	std::random_device				rd;
//	std::mt19937					gen(rd());
//	std::uniform_int_distribution<>	dist(0, charsetSize - 1);
//
//	std::string id;
//	id.reserve(length);
//	for (size_t i = 0; i < length; ++i) {
//		id += charset[dist(gen)];
//	}
//
//	return (id);
//}
//
//int main() {
//	std::cout << G_MSG("Welcome in pong-cli! |.  |") << std::endl;
//
//	CurlWrapper	curl("https://localhost:4443");
//	User		user;
//
//	user.setUsername("xavier" + generateCustomID(4));
//	user.setPassword("pass");
//
//	try { user.initializeConnection(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.signUpUser(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.signInUser(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.tokenRefresh(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.signInUser(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	return 0;
//}
