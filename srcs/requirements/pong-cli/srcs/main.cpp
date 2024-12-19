/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/18 15:41:57 by xcharra          ###   ########.fr       */
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

#define HTTPS_SERVER	"https://xcharra-laptop:4443"
#define WSS_SERVER		"wss://localhost:4443"
int main(void)
{
	{
		CurlWrapper	curl;
		User		user;

		curl.setServer(HTTPS_SERVER);
		curl.addHeader("Content-Type: application/json");

		user.setUsername("test");
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


		// try {
		// 	// Création du contexte d'IO
		// 	asio::io_context io_context;

		// 	// Configuration du contexte SSL pour TLS 1.3
		// 	asio::ssl::context ssl_context(asio::ssl::context::tlsv13_client);

		// 	// Charger le certificat auto-signé
		// 	ssl_context.load_verify_file("ft_transcendence.crt");

		// 	// Activer la vérification stricte (le certificat auto-signé sera accepté grâce à load_verify_file)
		// 	ssl_context.set_verify_mode(asio::ssl::verify_peer);

		// 	// Résolution de l'adresse et du port
		// 	tcp::resolver resolver(io_context);
		// 	auto endpoints = resolver.resolve("localhost", "5500");

		// 	// Création du socket SSL
		// 	asio::ssl::stream<tcp::socket> ssl_socket(io_context, ssl_context);

		// 	// Connexion au serveur
		// 	asio::connect(ssl_socket.lowest_layer(), endpoints);

		// 	// Handshake SSL/TLS
		// 	ssl_socket.handshake(asio::ssl::stream_base::client);

		// 	std::cout << "Connexion sécurisée établie avec TLS 1.3.\n";

		// 	// Envoi d'une requête HTTP basique
		// 	std::string request = "GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n";
		// 	asio::write(ssl_socket, asio::buffer(request));

		// 	// Lecture de la réponse
		// 	boost::system::error_code error;
		// 	asio::streambuf response_buffer;
		// 	asio::read(ssl_socket, response_buffer, asio::transfer_all(), error);

		// 	if (error && error != asio::error::eof) {
		// 		throw boost::system::system_error(error);
		// 	}

		// 	// Affichage de la réponse
		// 	std::istream response_stream(&response_buffer);
		// 	std::cout << "Réponse :\n" << response_stream.rdbuf() << std::endl;

		// } catch (const std::exception& e) {
		// 	std::cerr << "Erreur : " << e.what() << std::endl;
		// }

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
