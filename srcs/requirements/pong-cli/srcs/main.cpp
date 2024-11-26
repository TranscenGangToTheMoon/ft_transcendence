/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/26 19:35:34 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include "pong-cli.h"
#define CONTENT_TYPE	"Content-Type: application/json"

std::string	jsonParser(std::string &json, std::string &key) {
	std::string	value;
	size_t		pos = 0;
	size_t		start = 0;
	size_t		end = 0;

	if ((pos = json.find(key)) != std::string::npos) {
		start = json.find(":", pos);
		if (start != std::string::npos) {
			start = json.find("\"", start);
			if (start != std::string::npos) {
				start++;
				end = json.find("\"", start);
				if (end != std::string::npos) {
					value = json.substr(start, end - start);
				}
			}
		}
	}
	return value;
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
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, "");

	// Callback pour stocker la réponse
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);

	CURLcode res = curl_easy_perform(curl);
	if (res != CURLE_OK)
		std::cerr << "POST failed ! (" << res << "): " << curl_easy_strerror(res) << std::endl;
	else
		std::cout << "POST succeed: \n" << response << std::endl;

	curl_easy_cleanup(curl);
	return (res)
}

int main() {
	std::cout << G_MSG("Welcome in pong-cli! |.  |") << std::endl;

	std::string	baseURL = "https://localhost:4443";
	std::string	response;

	struct 		curl_slist *headers = NULL;

	curl_global_init(CURL_GLOBAL_DEFAULT);


	headers = curl_slist_append(headers, CONTENT_TYPE);
	if (!headers) {
		std::cerr << "Failed to append headers" << std::endl;
		return (1);
	}
	// URL complète
	std::string guest = baseURL + "/api/auth/guest/";

	CURLcode res = cURL_POST(guest, (std::string &)"", headers, response);







	curl_global_cleanup();
	curl_slist_free_all(headers);

	return 0;
}

