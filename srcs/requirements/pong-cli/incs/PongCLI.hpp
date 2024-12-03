/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   PongCLI.hpp                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/12/03 17:34:55 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/03 19:10:04 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PONGCLI_HPP
# define PONGCLI_HPP

# include "colors.h"
# include "CurlWrapper.hpp"
# include "User.hpp"

class PongCLI {
public:
	enum Page {
		LoginPage,
		MainMenuPage,
		SettingsPage,
		GamePage,
	};

	void test() {
		std::cout << "PongCLI test on: " << _currentPage << std::endl;
		std::cout << "PongCLI test on: " << _curl.isServerSet() << std::endl;
		try { _user.initializeConnection(_curl); }
			catch (std::exception &e) { return ((void)(std::cerr << E_MSG( "(" << _curl.getHTTPCode() << ") " << e.what()) << std::endl)); }
	}
	PongCLI(CurlWrapper &curl, User &user);
	PongCLI() = delete;
	PongCLI(PongCLI const &src) = delete;
	~PongCLI();
	PongCLI &operator=(PongCLI const &rhs);

private:
	Page		_currentPage = LoginPage;
	CurlWrapper	&_curl;
	User		&_user;
};


#endif //PONGCLI_HPP
