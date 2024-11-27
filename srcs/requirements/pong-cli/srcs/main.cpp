/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/27 18:57:05 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include "pong-cli.h"
#include "CurlWrapper.hpp"

std::string	jsonParser(const std::string &json, const std::string &key) {
	std::string value;
	std::string formatedKey = "\"" + key + "\":";

	size_t pos = json.find(formatedKey);
	if (pos == std::string::npos) {
		throw (std::invalid_argument("Key not found in json"));
	}
	pos += formatedKey.length();
	pos = json.find("\"", pos);
	pos++;
	size_t end = json.find("\"", pos);
	value = json.substr(pos, end - pos);
	return (value);
}

int main() {
	std::cout << G_MSG("Welcome in pong-cli! |.  |") << std::endl;

	const std::string contentType = "Content-Type: application/json";
	CurlWrapper	curl("https://localhost:4443");
	try {
		curl.addHeader(contentType);
		curl.test();
		std::cout << "Test connection succeed !" << std::endl;
	}
	catch (std::exception &e) {
		std::cerr << E_MSG(e.what()) << std::endl;
		return (1);
	}

	std::cout << "Get authorization token" << std::endl;
	const std::string	key = "access";
	try {
		std::string json = curl.POST("/api/auth/guest/", "");
		std::string accessToken = "Authorization: Bearer ";
		accessToken += jsonParser(json, key);
		curl.addHeader(accessToken);
		std::cout << "Access token obtained !" << std::endl;
	}
	catch (std::exception &e) {
		std::cout << "HTTP code: " << curl.getHTTPCode()<< std::endl;
		std::cerr << E_MSG(e.what()) << std::endl;
		return (1);
	}

	std::string	username = "jules";
	std::string	password = "zgege";
	std::string data = R"({"username": ")" +username +
		R"(", "password": ")" + password + R"("})";

	std::cout << "Try to register: " << data << std::endl;
	try {
		std::string res = curl.PUT("/api/auth/register/", data);
		if (curl.getHTTPCode() >=300) {
			std::cout << "Failed to register\n" << res << std::endl;
			return (1);
		}
		std::cout << "Register succeed !\n" << res << std::endl;
	}
	catch (std::exception &e) {
		std::cerr << E_MSG(e.what()) << std::endl;
		return (1);
	}

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

