/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CurlWrapper.hpp                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/27 13:57:16 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/02 16:26:20 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CURLWRAPPER_HPP
# define CURLWRAPPER_HPP

#include "curl/curl.h"
typedef struct	curl_slist curl_slist_t;

class CurlWrapper {
public:
	CurlWrapper();
	CurlWrapper(const std::string &server);
	~CurlWrapper();

	CurlWrapper(CurlWrapper const &src) = delete;
	CurlWrapper &operator=(CurlWrapper const &rhs) = delete;

	void	test();

	void	addHeader(const std::string &header);
	void	clearHeaders();

	void	setServer(const std::string &server);

	long	getHTTPCode() const;
	bool	isServerSet() const;

//Requests
	std::string	GET(const std::string &path = "", const std::string &data = "");
	std::string	POST(const std::string &path, const std::string &data = "");
	std::string	PUT(const std::string &path, const std::string &data = "");
	std::string	PATCH(const std::string &path, const std::string &data = "");
	std::string	DELETE(const std::string &path, const std::string &data = "");

private:
	bool			_serverSet;
	std::string		_server;
	std::string		_SSLCertificate;
	curl_slist_t	*_headers;
	long			_HTTPCode;

	static size_t	writeCallback(void *buffer, size_t size, size_t nmemb, std::string &response);
	static size_t	readCallback(void *buffer, size_t size, size_t nmemb, std::string &data);
};


#endif //CURLWRAPPER_HPP
