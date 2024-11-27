/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CurlWrapper.hpp                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/27 13:57:16 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/27 18:52:04 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CURLWRAPPER_HPP
# define CURLWRAPPER_HPP

#include "curl/curl.h"
typedef struct	curl_slist curl_slist_t;

class CurlWrapper {
public:
	CurlWrapper() = delete;
	CurlWrapper(const std::string &host);
	CurlWrapper(CurlWrapper const &src) = delete;
	~CurlWrapper();
	CurlWrapper &operator=(CurlWrapper const &rhs) = delete;

	void		test();

	void		addHeader(const std::string &header);
	void		clearHeaders();

	long		getHTTPCode() const;

//Requests
	std::string	GET(const std::string &path = "", std::string data = "");
	std::string	POST(const std::string &path, std::string data = "");
	std::string	PUT(const std::string &path, std::string data = "");
	std::string	PATCH(const std::string &path, std::string data = "");
	std::string	DELETE(const std::string &path, std::string data = "");

private:
	std::string		_host;
	std::string		_SSLCertificate;
	curl_slist_t	*_headers;
	long			_HTTPCode;

	static size_t	writeCallback(void *contents, size_t size, size_t nmemb, std::string &response);
	static size_t	readCallback(void *contents, size_t size, size_t nmemb, std::string &data);
};


#endif //CURLWRAPPER_HPP
