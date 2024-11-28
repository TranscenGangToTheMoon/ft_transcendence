/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/28 15:46:16 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "User.hpp"

#include <random>
std::string generateCustomID(size_t length) {
	const char charset[] = "0123456789abcdef";
	const size_t charsetSize = sizeof(charset) - 1;

	std::random_device				rd;
	std::mt19937					gen(rd());
	std::uniform_int_distribution<>	dist(0, charsetSize - 1);

	std::string id;
	id.reserve(length);
	for (size_t i = 0; i < length; ++i) {
		id += charset[dist(gen)];
	}

	return (id);
}



int main() {
	std::cout << G_MSG("Welcome in pong-cli! |.  |") << std::endl;

	CurlWrapper	curl("https://localhost:4443");
	User		user;

	user.setUsername("xavier" + generateCustomID(4));
	user.setPassword("pass");

	try { user.initializeConnection(curl); }
	catch (std::exception &e) { return (std::cerr << E_MSG(e.what()) << std::endl, 1); }

	try { user.signUpUser(curl); }
	catch (std::exception &e) { return (std::cerr << E_MSG(e.what()) << std::endl, 1); }

	std::string data = R"({"username": ")" + user.getUsername() +
		R"(", "password": ")" + user.getPassword() + R"("})";
	std::cout << "Try to login: " << data << std::endl;
	try {
		std::string res = curl.POST("/api/auth/login/", data);
		if (curl.getHTTPCode() >=300) {
			std::cout << "Failed to login\n" << res << std::endl;
			return (1);
		}
		std::cout << "Login succeed !\n" << res << std::endl;
	}
	catch (std::exception &e) {
		std::cerr << E_MSG(e.what()) << std::endl;
		return (1);
	}
	return 0;
}

