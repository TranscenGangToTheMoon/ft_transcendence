/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CurlWrapper.cpp                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/27 13:57:24 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/02 17:00:27 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <iostream>
#include <cstring>
#include "CurlWrapper.hpp"
#include "colors.h"

CurlWrapper::CurlWrapper(const std::string &server) : _serverSet(true), _server(server), _SSLCertificate("./ft_transcendence.crt"),
	_headers(nullptr), _HTTPCode(0) {
	std::cout << C_MSG("CurlWrapper default constructor called") << std::endl;

	if (curl_global_init(CURL_GLOBAL_DEFAULT))
		throw (std::runtime_error("Failed to init curl"));
}

CurlWrapper::CurlWrapper() : _serverSet(false), _server(), _SSLCertificate("./ft_transcendence.crt"),
	_headers(nullptr), _HTTPCode(0) {
	std::cout << C_MSG("CurlWrapper default constructor called") << std::endl;

	if (curl_global_init(CURL_GLOBAL_DEFAULT))
		throw (std::runtime_error("Failed to init curl"));
}

CurlWrapper::~CurlWrapper() {
	std::cout << C_MSG("CurlWrapper destructor called") << std::endl;

	if (_headers)
		curl_slist_free_all(_headers);
	curl_global_cleanup();
}

void CurlWrapper::test() {
	GET();
	if (_HTTPCode != 200)
		throw (std::runtime_error("Failed to connect to server"));
}

void CurlWrapper::addHeader(const std::string &header) {
_headers = curl_slist_append(_headers, header.c_str());
	if (!_headers)
		throw (std::runtime_error("Failed to add headers"));
}

void CurlWrapper::clearHeaders() {
	if (_headers)
		curl_slist_free_all(_headers);
	_headers = nullptr;
}

std::string CurlWrapper::GET(const std::string &path, const std::string &data) {
	if (!isServerSet())
		throw (std::invalid_argument("Server not set"));

	std::string	response;
	std::string	url = _server + path;
	CURL		*curl = curl_easy_init();

	if (!curl) {
		std::cerr << "Failed to init curl" << std::endl;
		throw (std::runtime_error("Failed to init curl"));
	}

	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	std::cout << "GET Request to: " << url << std::endl;

	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
	curl_easy_setopt(curl, CURLOPT_CAINFO, _SSLCertificate.c_str());

	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, _headers);

	curl_easy_setopt(curl, CURLOPT_HTTPGET, 1L);

	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

	CURLcode res = curl_easy_perform(curl);

	if (res != CURLE_OK) {
		curl_easy_cleanup(curl);
		throw (std::runtime_error(curl_easy_strerror(res)));
	}
	curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &_HTTPCode);
	curl_easy_cleanup(curl);
	(void)data;
	return (response);
}

std::string CurlWrapper::POST(const std::string &path, const std::string &data) {
	if (!isServerSet())
		throw (std::invalid_argument("Server not set"));

	std::string	response;
	std::string	url = _server + path;
	CURL		*curl = curl_easy_init();

	if (!curl) {
		std::cerr << "Failed to init curl" << std::endl;
		throw (std::runtime_error("Failed to init curl"));
	}

	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	std::cout << "POST Request to: " << url << std::endl;

	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
	curl_easy_setopt(curl, CURLOPT_CAINFO, _SSLCertificate.c_str());

	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, _headers);

	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());

	curl_easy_setopt(curl, CURLOPT_POST, 1L);

	CURLcode res = curl_easy_perform(curl);
	if (res != CURLE_OK) {
		curl_easy_cleanup(curl);
		throw (std::runtime_error(curl_easy_strerror(res)));
	}
	curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &_HTTPCode);
	curl_easy_cleanup(curl);
	return (response);
}

std::string CurlWrapper::PUT(const std::string &path, const std::string &data) {
	if (!isServerSet())
		throw (std::invalid_argument("Server not set"));

	std::string	response;
	std::string	url = _server + path;
	CURL		*curl = curl_easy_init();

	if (!curl) {
		std::cerr << "Failed to init curl" << std::endl;
		throw (std::runtime_error("Failed to init curl"));
	}

	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	std::cout << "PUT Request to: " << url << std::endl;

	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
	curl_easy_setopt(curl, CURLOPT_CAINFO, _SSLCertificate.c_str());

	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, _headers);

	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

	curl_easy_setopt(curl, CURLOPT_READFUNCTION, readCallback);
	curl_easy_setopt(curl, CURLOPT_READDATA, &data);
	curl_easy_setopt(curl, CURLOPT_INFILESIZE, data.length());

	curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);

	CURLcode res = curl_easy_perform(curl);
	if (res != CURLE_OK) {
		curl_easy_cleanup(curl);
		throw (std::runtime_error(curl_easy_strerror(res)));
	}
	curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &_HTTPCode);
	curl_easy_cleanup(curl);
	return (response);
}

size_t CurlWrapper::writeCallback(void *buffer, size_t size, size_t nmemb, std::string &response) {
	size_t	newLength = size * nmemb;

//	std::cout << "size: " << size << " nmemb: " << nmemb << std::endl;
	if (newLength)
		response.append(static_cast<char *>(buffer), newLength);
	return (newLength);
}

size_t CurlWrapper::readCallback(void *buffer, size_t size, size_t nmemb, std::string &data) {
	size_t	totalSize = size * nmemb;

//	std::cout << "size: " << size << " nmemb: " << nmemb << std::endl;
	if (data.empty())
		return (0);

	size_t	copySize = std::min(totalSize, data.length());
	memcpy(buffer, data.c_str(), copySize);
	data.erase(0, copySize);
	return (copySize);
}

void CurlWrapper::setServer(const std::string &server) {
	_server = server;
	_serverSet = true;
}

long CurlWrapper::getHTTPCode() const {
	return (_HTTPCode);
}

bool CurlWrapper::isServerSet() const {
	return (_serverSet);
}
