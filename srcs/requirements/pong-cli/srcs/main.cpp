/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/16 19:35:39 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "PongCLI.hpp"
#include "User.hpp"
#include "asio.hpp"
#include "asio/ssl.hpp"

#define HTTPS_SERVER	"https://localhost:4443"
#define WSS_SERVER		"wss://localhost:4443"
int main(void)
{
	{
		CurlWrapper	curl;
		User		user;
		sio::client		test;

		curl.setServer(HTTPS_SERVER);
		curl.addHeader("Content-Type: application/json");

		user.setUsername("monfiacsfddsdsdddi");
		user.setPassword("test");


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
		std::string id;
		try {
			curl.GET("/api/users/me/", "");
			std::cout << "Users me succeed!" << std::endl;
			std::cout << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
			id = std::to_string((int)json::parse(curl.getResponse())["id"]);
			std::cout << id << std::endl;

		}
		catch (std::exception &error) {
			std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
			std::cerr << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
		}
//		// Configuration des options de connexion
//		test.set_open_listener([]() {
//			std::cout << "Connexion établie avec le serveur !" << std::endl;
//		});
//
//		test.set_fail_listener([]() {
//			std::cerr << "La connexion a échoué !" << std::endl;
//		});
//
//		test.set_close_listener([](sio::client::close_reason const& reason) {
//			std::cout << "Connexion fermée, raison: " << static_cast<int>(reason) << std::endl;
//		});


		// Connexion au serveur
//		std::map<std::string, std::string> options = {
//			{"id", id},
//			{"token", "kk"}
//		};
//		test.connect("wss://localhost:4443/socket.io/?EIO=3&transport=websocket?token=kk?user_id=" + id);
//		test.connect("wss://localhost:4443/ws");

//		test.socket()->emit("get_games");
		// Bloquer pour maintenir la connexion active
//		std::cin.get();
		// Déconnexion propre
//		test.close();
		asio::io_service	service;
		asio::ssl::context	ctx(asio::ssl::context::tlsv12);
		ctx.set_verify_mode(asio::ssl::verify_peer);
		ctx.load_verify_file("./ft_transcendence.crt");

		asio::ssl::stream<asio::ip::tcp::socket>	socket = new socket(service, ctx);
//
		sio::client	client;

		client.socket().reset(socket);

		client.set_open_listener([&]() {
			std::cout << "Connected to server!" << std::endl;
		});

		client.set_fail_listener([&]() {
			std::cout << "Failed to connect to server!" << std::endl;
		});

		// Connect to a WSS server
		client.connect("wss://localhost:4443/ws");
		// Send a message
		client.socket()->emit("send_games");

		client.socket()->on("games", [&](sio::event& ev) {
			std::cout << "Received message: " << ev.get_message()->get_string() << std::endl;
		});
		// Handle incoming messages
		client.socket()->on("connect", [](sio::event& ev) {
			std::cout << "Received message: " << ev.get_message()->get_string() << std::endl;
		});

		// Keep the client alive
//		std::this_thread::sleep_for(std::chrono::minutes(10));
		std::cin.get();

		client.close();
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
