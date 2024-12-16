/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   User.hpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/28 13:58:57 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/09 13:49:22 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef USER_HPP
# define USER_HPP

# include "pong-cli.h"
# include "CurlWrapper.hpp"

class User {
public:
	User();
	~User();

	User(User const &src) = delete;
	User	&operator=(User const &rhs) = delete;

	void	guestUser(CurlWrapper &curl);

	void	registerUser(CurlWrapper &curl);
	void	registerGuestUser(CurlWrapper &curl);
	void	loginUser(CurlWrapper &curl);

	void	tokenRefresh(CurlWrapper &curl);

	void	setAccessToken(const std::string &accessToken);
	void	setPassword(const std::string &password);
	void	setRefreshToken(const std::string &refreshToken);
	void	setUsername(const std::string &username);

	[[ nodiscard ]] const std::string	&getAccessToken() const;
	[[ nodiscard ]] const std::string	&getPassword() const;
	[[ nodiscard ]] const std::string	&getRefreshToken() const;
	[[ nodiscard ]] const std::string	&getUsername() const;

private:
	std::string	_accessToken;
	std::string	_password;
	std::string	_refreshToken;
	std::string	_username;
};

#endif //USER_HPP
