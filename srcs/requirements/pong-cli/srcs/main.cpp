/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/17 19:14:41 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "PongCLI.hpp"
#include "User.hpp"
//#include "boost/asio.hpp"
//#include "boost/asio/ssl.hpp"
//#include "boost/beast.hpp"

#define HTTPS_SERVER	"https://localhost:4443"
#define WSS_SERVER		"wss://localhost:4444"
int main(void)
{
	{
		CurlWrapper	curl;
		User		user;

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
			// std::cerr << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
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
			// std::cerr << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
		}

		// boost::asio::io_context io_context;
		// boost::asio::ssl::context ssl_context(boost::asio::ssl::context::tlsv12_client);
		//
		// boost::asio::ip::tcp::resolver resolver(io_context);
		// auto const results = resolver.resolve("localhost", "4444");
		//
		// boost::asio::ssl::stream<boost::asio::ip::tcp::socket> ws(io_context, ssl_context);
		// boost::asio::connect(ws.next_layer(), results.begin(), results.end());
		// ws.handshake(boost::asio::ssl::stream_base::client);
		//
		// ws.next_layer().handshake(boost::asio::ssl::stream_base::client);
		// ws.handshake("localhost", "/");
		//
		// std::cout << "Connected to WebSocket server" << std::endl;


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
