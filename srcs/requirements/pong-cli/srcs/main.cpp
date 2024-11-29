/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/29 19:08:59 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include <random>
#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "User.hpp"
#include "ftxui/component/screen_interactive.hpp"

#include "ftxui/dom/elements.hpp"
#include "ftxui/screen/screen.hpp"
#include "ftxui/component/component.hpp"
#include <iostream>
	using namespace ftxui;

int main(void) {
	auto screen = ScreenInteractive::Fullscreen();

	std::string	username;
	std::string	password;
	InputOption	password_option;

	password_option.password = true;
	Component	username_input = Input(&username);
	Component	password_input = Input(&password, password_option);

	std::string	warning = "Login";
	auto	signInAction = [&] {
		if (!username.empty() && !password.empty()) {
			screen.ExitLoopClosure()();
			std::cout << "Sign In" << std::endl;
		}
		else
			warning = "Empty fields";
	};
	auto	signUpAction = [&] {
		if (!username.empty() && !password.empty()) {
			screen.ExitLoopClosure()();
			std::cout << "Sign Up" << std::endl;
		}
		else
			warning  = "Empty fields";
	};
	Component	signInButton = Button("Sign In", signInAction);
	Component	signUpButton = Button("Sign Un", signUpAction);

	auto	userFields = Container::Vertical({
		username_input,
		password_input,
		signInButton,
		signUpButton,
	});

//	auto	buttons = Container::Horizontal({
//	});

	auto	renderer = Renderer(userFields, [&] {
		return (
			vbox({
				text("Welcome in pong-cli") | hcenter | border,
				vbox({
					vbox({
						vbox(
							text("Username: "),
							username_input->Render() | border
						),
						vbox(
							text("Password: "),
							password_input->Render() | border
						),
						hbox({
								 signInButton->Render(),
								 signUpButton->Render()
						}),
					}) | border | hcenter | size(WIDTH, EQUAL, 30),
					text(warning) | color(Color::Red) | center,
				}) | border | hcenter
			}) | border
		);
	});
	auto	event = CatchEvent(renderer, [&](Event event) {
		if (event == Event::Character('q')) {
			//replace by escape key
			screen.ExitLoopClosure()();
			return true;
		}
		return false;
	});

	screen.Loop(event);
	std::cout << "username: " << username << std::endl;
	std::cout << "password: " << password << std::endl;
	return (0);
}



















//std::string generateCustomID(size_t length) {
//	const char charset[] = "0123456789abcdef";
//	const size_t charsetSize = sizeof(charset) - 1;
//
//	std::random_device				rd;
//	std::mt19937					gen(rd());
//	std::uniform_int_distribution<>	dist(0, charsetSize - 1);
//
//	std::string id;
//	id.reserve(length);
//	for (size_t i = 0; i < length; ++i) {
//		id += charset[dist(gen)];
//	}
//
//	return (id);
//}
//
//int main() {
//	std::cout << G_MSG("Welcome in pong-cli! |.  |") << std::endl;
//
//	CurlWrapper	curl("https://localhost:4443");
//	User		user;
//
//	user.setUsername("xavier" + generateCustomID(4));
//	user.setPassword("pass");
//
//	try { user.initializeConnection(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.signUpUser(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.signInUser(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.tokenRefresh(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	std::cout << T_MSG("=======") << std::endl;
//
//	try { user.signInUser(curl); }
//	catch (std::exception &e) { return (std::cerr << E_MSG( "(" << curl.getHTTPCode() << ") " << e.what()) << std::endl, 1); }
//
//	return 0;
//}
