/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   User.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/28 13:59:31 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/28 15:48:49 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <iostream>
#include <cstring>
#include "User.hpp"
#include "colors.h"

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

User::User() : _accessToken(), _password(), _refreshToken(), _username() {
	std::cout << C_MSG("User default constructor called") << std::endl;
}

User::~User() {
	std::cout << C_MSG("User destructor called") << std::endl;
}

void User::initializeConnection(CurlWrapper &curl) {
	curl.addHeader("Content-Type: application/json");

	std::string json = curl.POST("/api/auth/guest/", "");

	setAccessToken(jsonParser(json, "access"));
	setRefreshToken(jsonParser(json, "refresh"));

	curl.addHeader("Authorization: Bearer " + getAccessToken());


	if (curl.getHTTPCode() < 300)
		std::cout << I_MSG("(" << curl.getHTTPCode() << ") Tokens obtained !") << std::endl;
}

void User::signUpUser(CurlWrapper &curl) {
	std::string data = R"({"username": ")" + getUsername() +
		R"(", "password": ")" + getPassword() + R"("})";

	std::cout << "Try to register: " << data << std::endl;

	std::string res = curl.PUT("/api/auth/register/", data);
	if (curl.getHTTPCode() >=300) {
		std::cout << "Failed to register\n" << res << std::endl;
		throw (std::runtime_error("Failed to register"));
	}
}

void User::signInUser(CurlWrapper &curl) {
	(void)curl;
}

void User::setAccessToken(const std::string &accessToken) {
	if (!accessToken.empty())
		_accessToken = accessToken;
}

void User::setPassword(const std::string &password) {
	if (!password.empty())
		_password = password;
}

void User::setRefreshToken(const std::string &refreshToken) {
	if (!refreshToken.empty())
		_refreshToken = refreshToken;
}

void User::setUsername(const std::string &username) {
	if (!username.empty())
		_username = username;
}

const std::string &User::getAccessToken() const { return (_accessToken); }
const std::string &User::getPassword() const { return (_password); }
const std::string &User::getRefreshToken() const { return (_refreshToken); }
const std::string &User::getUsername() const { return (_username); }
