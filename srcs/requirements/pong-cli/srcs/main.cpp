/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/19 18:48:02 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pong-cli.h"
#include "CurlWrapper.hpp"
//#include "PongCLI.hpp"
#include "User.hpp"
#include "boost/asio.hpp"
#include "boost/asio/ssl.hpp"
#include "boost/beast.hpp"


#include <iostream>
#include <string>

namespace asio = boost::asio;
namespace beast = boost::beast;
namespace http = beast::http;
namespace ssl = asio::ssl;


using boost::asio::ip::tcp;
namespace ssl = boost::asio::ssl;
using SSLSocket = ssl::stream<tcp::socket>;

//put the hostname of the website
#define HTTPS_SERVER	"https://localhost:4443"
#define WSS_SERVER		"wss://localhost:4443"
int main(void)
{
	{
//		CurlWrapper	curl;
//		User		user;
//
//		curl.setServer(HTTPS_SERVER);
//		curl.addHeader("Content-Type: application/json");
//
//		user.setUsername("test");
//		user.setPassword("test");
//
//
//		try {
//			user.loginUser(curl);
//			std::cout << "Login Succeed" << std::endl;
//		}
//		catch (std::exception &error) {
//			if (curl.getHTTPCode() == 401)
//				try {
//					user.registerUser(curl);
//					std::cout << "Register Succeed" << std::endl;
//				}
//				catch (std::exception &error) {
//					std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
//				}
//		}
//
//		try {
//			curl.POST("/api/play/duel/", "");
//			std::cout << "Duel request Succeed" << std::endl;
//			std::cout << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
//		}
//		catch (std::exception &error) {
//			std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
//			// std::cerr << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
//		}
//		std::string id;
//		try {
//			curl.GET("/api/users/me/", "");
//			std::cout << "Users me succeed!" << std::endl;
//			std::cout << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
//			id = std::to_string((int)json::parse(curl.getResponse())["id"]);
//			std::cout << id << std::endl;
//
//		}
//		catch (std::exception &error) {
//			std::cerr << ("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) << std::endl;
//			// std::cerr << json::parse(curl.getResponse()).dump(1, '\t') << std::endl;
//		}


		 try {
			asio::io_context io_context;
			asio::ssl::context ssl_context(asio::ssl::context::tlsv13_client);

			ssl_context.load_verify_file("ft_transcendence.crt");
			ssl_context.set_verify_mode(asio::ssl::verify_peer);

			// Résolution de l'adresse et du port
			tcp::resolver resolver(io_context);
			auto endpoints = resolver.resolve("localhost", "4444");

			// Création du socket SSL
			asio::ssl::stream<tcp::socket> ssl_socket(io_context, ssl_context);

			// Connexion au serveur
			asio::connect(ssl_socket.next_layer(), endpoints);

			// Handshake SSL/TLS
			ssl_socket.handshake(asio::ssl::stream_base::client);


			 // Create HTTP GET request
			 const std::string request =
				 "GET /ws/?EIO=4&transport=websocket HTTP/1.1\r\n"
				 "Host: localhost\r\n"
				 "Connection: Upgrade\r\n\r\n";

			std::cout << "Ca a pas throw" << std::endl;

			// Envoi d'une requête HTTP basique
			asio::write(ssl_socket, asio::buffer(request));

			char buffer[4096];
			boost::asio::read(ssl_socket, boost::asio::buffer(buffer, 4096));
			std::cout << buffer << std::endl;
//			boost::asio::async_read(ssl_socket, boost::asio::buffer(buffer, 4096), [&] (boost::system::error_code ec, std::size_t length) {
//				std::cout << buffer << std::endl;
//				(void)ec;
//				(void)length;
//			});
//			std::cin.get();
			// Affichage de la réponse
//			std::istream response_stream(&response_buffer->data());
//			std::cout << "Réponse :\n" << response_stream.rdbuf() << std::endl;

			}
			catch (const std::exception& e) {
				std::cerr << "Erreur : " << e.what() << std::endl;
			}

		return 0;
	}

// 	{
// 		CurlWrapper	curl;
// 		User		user;
// 		PongCLI		app(curl, user);

// 		curl.addHeader("Content-Type: application/json");
// //		app.run();
// 		app.changePage(PongCLI::Page::MainMenuPage);

// 		std::cout << "server: " << app.getServer() << std::endl;
// 		std::cout << "username: " << app.getUsername() << std::endl;
// 		std::cout << "password: " << app.getPassword() << std::endl;
// 	 }
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
