/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/26 22:56:23 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include "pong-cli.h"
#define CONTENT_TYPE	"Content-Type: application/json"

std::string	jsonParser(std::string &json, std::string &key) {
	std::string value;
	std::string formatedKey = "\"" + key + "\":";

	size_t pos = json.find(formatedKey);
	if (pos == std::string::npos) {
		std::cerr << "Key not found" << std::endl;
		return ("");
	}
	pos += formatedKey.length();
	pos = json.find("\"", pos);
	pos++;
	size_t end = json.find("\"", pos);
	value = json.substr(pos, end - pos);
	return (value);
}

static size_t WriteCallback(void *contents, size_t size, size_t nmemb, std::string *s) {
	size_t newLength = size * nmemb;
	try {
		s->append((char*)contents, newLength);
		return newLength;
	}
	catch(std::bad_alloc &e) {
		return 0;
	}
}

CURLcode cURL_POST(std::string &url, std::string &data, struct curl_slist *headers, std::string &response) {
	CURL *curl = curl_easy_init();

	if (!curl) {
		std::cerr << "Failed to init curl" << std::endl;
		throw (std::runtime_error("Failed to init curl"));
	}

	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	std::cout << "Request to: " << url << std::endl;

	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
	curl_easy_setopt(curl, CURLOPT_CAINFO, "./ft_transcendence.crt");


	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
	curl_easy_setopt(curl, CURLOPT_POST, 1L);
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());

	// Callback pour stocker la réponse
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

	CURLcode res = curl_easy_perform(curl);


	curl_easy_cleanup(curl);
	return (res);
}

CURLcode cURL_PUT(std::string &url, std::string &data, struct curl_slist *headers, std::string &response) {
	CURL *curl = curl_easy_init();

	if (!curl) {
		std::cerr << "Failed to init curl" << std::endl;
		throw (std::runtime_error("Failed to init curl"));
	}

	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	std::cout << "Request to: " << url << std::endl;

	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 1L);
	curl_easy_setopt(curl, CURLOPT_CAINFO, "./ft_transcendence.crt");


	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
	curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT");
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, data.c_str());

	// Callback pour stocker la réponse
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

	CURLcode res = curl_easy_perform(curl);


	curl_easy_cleanup(curl);
	return (res);
}

int main() {
	std::cout << G_MSG("Welcome in pong-cli! |.  |") << std::endl;

	std::string	baseURL = "https://localhost:4443";
	std::string	response;

	struct		curl_slist *headers = NULL;

	curl_global_init(CURL_GLOBAL_DEFAULT);


	headers = curl_slist_append(headers, CONTENT_TYPE);
	if (!headers) {
		std::cerr << "Failed to append headers" << std::endl;
		return (1);
	}
	// URL complète
	std::string guest = baseURL + "/api/auth/guest/";
	std::string data = "";
	CURLcode res = cURL_POST(guest, data, headers, response);
	if (res != CURLE_OK)
		std::cerr << "POST failed ! (" << res << "): " << curl_easy_strerror(res) << std::endl;
	else
		std::cout << "POST succeed: \n" << response << std::endl;

	std::string key = "access";
	std::string accessTkn = "Authorization: Bearer ";
	accessTkn += jsonParser(response, key);

	std::cout << "access_token: " << accessTkn << std::endl;
	data = R"({"username":"test","password":"test"})";
	response = "";

	std::cout << data << std::endl;

	headers = curl_slist_append(headers, accessTkn.c_str());
	if (!headers) {
		std::cerr << "Failed to append headers" << std::endl;
		return (1);
	}

	guest = "";
	guest = baseURL + "/api/auth/register/";
	res = cURL_PUT(guest, data, headers, response);
	if (res != CURLE_OK)
		std::cerr << "POST failed ! (" << res << "): " << curl_easy_strerror(res) << std::endl;
	else
		std::cout << "POST succeed: \n" << response << std::endl;

	curl_global_cleanup();
	curl_slist_free_all(headers);

	return 0;
}

