/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   User.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/28 13:59:31 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/13 17:21:51 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <iostream>
#include <cstring>
#include "User.hpp"
#include "colors.h"

#include "nlohmann/json.hpp"

using namespace nlohmann;

User::User() : _accessToken(), _password(), _refreshToken(), _username() {
	std::cout << C_MSG("User default constructor called") << std::endl;
}

User::~User() {
	std::cout << C_MSG("User destructor called") << std::endl;
}

void User::guestUser(CurlWrapper &curl) {
	curl.getResponse().clear();
	curl.POST("/api/auth/guest/", "");
	if (curl.getHTTPCode() >= 300)
		throw (std::runtime_error("Failed to guest up !"));
	basic_json	json = json::parse(curl.getResponse());

	setAccessToken(json["access"]);
	setRefreshToken(json["refresh"]);
	curl.addHeader("Authorization: Bearer " + getAccessToken());
}

void User::registerGuestUser(CurlWrapper &curl) {
	json	data;

	data["username"] = getUsername();
	data["password"] = getPassword();

	curl.getResponse().clear();
	curl.PUT("/api/auth/register/guest/", data.dump());
	if (curl.getHTTPCode() >= 300)
		throw (std::runtime_error("Failed to register guest !" + curl.getResponse()));
	basic_json	json = json::parse(curl.getResponse());

	setAccessToken(json["access"]);
	setRefreshToken(json["refresh"]);
	curl.addHeader("Authorization: Bearer " + getAccessToken());
}

void User::registerUser(CurlWrapper &curl) {
	json	data;

	data["username"] = getUsername();
	data["password"] = getPassword();

	curl.getResponse().clear();
	curl.POST("/api/auth/register/", data.dump());
	if (curl.getHTTPCode() >= 300)
		throw (std::runtime_error("Failed to register !"));
	basic_json	json = json::parse(curl.getResponse());

	setAccessToken(json["access"]);
	setRefreshToken(json["refresh"]);
	curl.addHeader("Authorization: Bearer " + getAccessToken());
}

void User::loginUser(CurlWrapper &curl) {
	json	data;

	data["username"] = getUsername();
	data["password"] = getPassword();

	curl.getResponse().clear();
	curl.POST("/api/auth/login/", data.dump());
	if (curl.getHTTPCode() >= 300)
		throw (std::runtime_error("Failed to sign in !"));
	basic_json	json = json::parse(curl.getResponse());

	setAccessToken(json["access"]);
	setRefreshToken(json["refresh"]);
	curl.addHeader("Authorization: Bearer " + getAccessToken());
}

void User::tokenRefresh(CurlWrapper &curl) {
	json	data;

	data["refresh"] = getRefreshToken();
	curl.getResponse().clear();
	curl.POST("/api/auth/refresh/", data);
	if (curl.getHTTPCode() >= 300)
		throw (std::runtime_error("Failed to refresh token !"));
	basic_json	json = json::parse(curl.getResponse());

	setAccessToken(json["access"]);
	setRefreshToken(json["refresh"]);
	curl.clearHeaders();
	curl.addHeader("Content-Type: application/json");
	curl.addHeader("Authorization: Bearer " + getAccessToken());
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
