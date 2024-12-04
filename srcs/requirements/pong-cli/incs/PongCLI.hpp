/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   PongCLI.hpp                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/12/03 17:34:55 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/04 00:27:10 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PONGCLI_HPP
# define PONGCLI_HPP

#include "ftxui/component/screen_interactive.hpp"
#include "ftxui/dom/elements.hpp"
#include "ftxui/screen/screen.hpp"
#include "ftxui/component/component.hpp"

#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "PongCLI.hpp"
#include "User.hpp"

using namespace ftxui;

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

	Component	renderLoginPage();
	Component	renderMainMenuPage();
	Component	renderSettingsPage();
	Component	renderGamePage();
	Component	renderDefaultPage();

	void	appRenderer();

	PongCLI(CurlWrapper &curl, User &user);
	PongCLI() = delete;
	PongCLI(PongCLI const &src) = delete;
	~PongCLI();
	PongCLI &operator=(PongCLI const &rhs) = delete;

private:
	Page				_currentPage = LoginPage;
	CurlWrapper			&_curl;
	User				&_user;
	ScreenInteractive	_screen;
};


#endif //PONGCLI_HPP
