/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   PongCLI.cpp                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/12/03 17:35:02 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/04 00:27:10 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <iostream>
#include "PongCLI.hpp"

#include <ftxui/component/screen_interactive.hpp>

#include "colors.h"

PongCLI::PongCLI(CurlWrapper &curl, User &user) : _curl(curl), _user(user), _screen(ScreenInteractive::Fullscreen()) {
	std::cout << C_MSG("PongCLI parametric constructor called") << std::endl;
}

PongCLI::~PongCLI() {
	std::cout << C_MSG("PongCLI destructor called") << std::endl;
}

Component PongCLI::renderLoginPage() {
	// std::cout << C_MSG("LoginPage called") << std::endl;

	return (Renderer([this] {
		return (vbox(text("Login page load !")));
	}));
}

Component PongCLI::renderMainMenuPage() {
	// std::cout << C_MSG("MainMenu called") << std::endl;

	return (Renderer([this] {
		return (vbox(text("Main menu page load !")));
	}));
}

Component PongCLI::renderSettingsPage() {
	// std::cout << C_MSG("SettingsPage called") << std::endl;

	return (Renderer([this] {
		return (vbox(text("Settings page load !")));
	}));
}

Component PongCLI::renderGamePage() {
	// std::cout << C_MSG("GamePage called") << std::endl;

	return (Renderer([this] {
		return (vbox(text("Game page load !")));
	}));
}

Component PongCLI::renderDefaultPage() {
	std::cout << C_MSG("LoginPage called") << std::endl;

	return (Renderer([this] {
		return (vbox(text("Default page !")));
	}));
}

void PongCLI::appRenderer() {
	Component	mainRenderer = Renderer([&] {
		switch(_currentPage) {
			case Page::LoginPage:
				return (renderLoginPage()->Render());
			case Page::MainMenuPage:
				return (renderMainMenuPage()->Render());
			case Page::SettingsPage:
				return (renderSettingsPage()->Render());
			case Page::GamePage:
				return (renderGamePage()->Render());
			default:
				return (renderDefaultPage()->Render());
		}
	});
	_screen.Loop(mainRenderer);
}
