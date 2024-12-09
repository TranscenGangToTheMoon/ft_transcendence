/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   PongCLI.hpp                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/12/03 17:34:55 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/09 13:49:22 by xcharra          ###   ########.fr       */
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
	PongCLI(CurlWrapper &curl, User &user);
	~PongCLI();

	enum Page {
		LoginPage,
		MainMenuPage,
		SettingsPage,
		GamePage,
	};
//make them private at the end
	void	renderLoginPage();
	void	renderMainMenuPage();
	void	renderSettingsPage();
	void	renderGamePage();
	void	renderDefaultPage();

	void	run();

//make them private at the end
	void	changePage(Page newPage);

	void	setPassword(const std::string &password);
	void	setServer(const std::string &server);
	void	setUsername(const std::string &username);

	[[ nodiscard ]] const std::string	&getPassword() const;
	[[ nodiscard ]] const std::string	&getServer() const;
	[[ nodiscard ]] const std::string	&getUsername() const;

	PongCLI() = delete;
	PongCLI(PongCLI const &src) = delete;
	PongCLI &operator=(PongCLI const &rhs) = delete;

private:
	void	loginAction(std::string &server, std::string &username, std::string &password);
	void	registerAction(std::string &server, std::string &username, std::string &password);
	void	guestUpAction(std::string &server);

	Element	getBanner();

	void	pageRenderer();

	CurlWrapper			&_curl;
	Element				_info;
	Page				_currentPage;
	ScreenInteractive	_screen = ScreenInteractive::Fullscreen();
	User				&_user;
	std::string			_password;
	std::string			_server;
	std::string			_username;
};


#endif //PONGCLI_HPP
