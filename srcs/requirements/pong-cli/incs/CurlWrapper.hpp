/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CurlWrapper.hpp                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/27 13:57:16 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/04 14:54:45 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CURLWRAPPER_HPP
# define CURLWRAPPER_HPP

#include "curl/curl.h"
typedef struct	curl_slist curl_slist_t;

class CurlWrapper {
public:
	CurlWrapper();
	explicit CurlWrapper(const std::string &server);
	~CurlWrapper();

	CurlWrapper(CurlWrapper const &src) = delete;
	CurlWrapper &operator=(CurlWrapper const &rhs) = delete;

	void	test();

	void	addHeader(const std::string &header);
	void	clearHeaders();

	void	setServer(const std::string &server);

	[[ nodiscard ]] long		getHTTPCode() const;
	[[ nodiscard ]] bool		isServerSet() const;
	[[ nodiscard ]] std::string	getResponse() const;

//Requests
	void	GET(const std::string &path = "", const std::string &data = "");
	void	POST(const std::string &path, const std::string &data = "");
	void	PUT(const std::string &path, const std::string &data = "");
	void	PATCH(const std::string &path, const std::string &data = "") = delete;
	void	DELETE(const std::string &path, const std::string &data = "") = delete;

private:
	bool			_serverSet;
	std::string		_server;
	std::string		_SSLCertificate;
	curl_slist_t	*_headers;
	long			_HTTPCode;
	std::string		_response;

	static size_t	writeCallback(void *buffer, size_t size, size_t nmemb, std::string &response);
	static size_t	readCallback(void *buffer, size_t size, size_t nmemb, std::string &data);
};


#endif //CURLWRAPPER_HPP
