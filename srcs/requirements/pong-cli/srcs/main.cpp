/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/03 19:12:22 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include <iostream>
#include <random>

#include "ftxui/component/screen_interactive.hpp"
#include "ftxui/dom/elements.hpp"
#include "ftxui/screen/screen.hpp"
#include "ftxui/component/component.hpp"

#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "PongCLI.hpp"
#include "User.hpp"

using namespace ftxui;
//
int main(void) {
	{
		CurlWrapper curl("https://localhost:4443");
		User user;
		user.setUsername("test");
		user.setPassword("pass");


		PongCLI app(curl, user);
		app.test();
	}

	CurlWrapper	curl("https://localhost:4443");
	User		user;

	auto		screen = ScreenInteractive::Fullscreen();

	std::string	server;
	InputOption	serverOption;
	std::string	username;
	InputOption	usernameOption;
	std::string	password;
	InputOption	passwordOption;

//	serverOption.multiline = false;
	usernameOption.multiline = false;
	passwordOption.multiline = false;
	passwordOption.password = true;
	//maybe creat checkbox to reveal password

	auto stateTransformer = [](InputState state) {
		if (state.hovered)
			state.element |= bgcolor(Color::GrayLight);
		else if (state.focused) {
			state.element |= bgcolor(Color::GrayDark);
		}
		return (state.element);
	};

	serverOption.transform = stateTransformer;
	usernameOption.transform = stateTransformer;
	passwordOption.transform = stateTransformer;

	auto	warning = text("");

	Component	serverInput = Input(&server, serverOption);
	Component	usernameInput = Input(&username, usernameOption);
	Component	passwordInput = Input(&password, passwordOption);

	auto	signInAction = [&] {
		if (!username.empty() && !password.empty()) {
			screen.ExitLoopClosure()();
			std::cout << "Sign In" << std::endl;
		}
		else
			warning = text("Empty fields") | color(Color::Red);
	};
	auto	signUpAction = [&] {
		if (!username.empty() && !password.empty()) {
			screen.ExitLoopClosure()();
			std::cout << "Sign Up" << std::endl;
		}
		else
			warning = text("Empty fields !") | color(Color::Red);
	};
	auto	testAction = [&] {
		if (!server.empty()) {
			try {
				curl.setServer(server);
				user.initializeConnection(curl);
				warning = text("Connexion test success !") | color(Color::Green);
			}
			catch (std::exception &error) {
				warning = text(error.what()) | color(Color::Red);
			}
		}
		else
			warning = text("Empty server field !") | color(Color::Red);
	};
	Component	signInButton = Button("Sign In", signInAction, ButtonOption::Animated(Color::Red));
	Component	signUpButton = Button("Sign Up", signUpAction, ButtonOption::Animated(Color::Green));
	Component	testButton = Button("Test", testAction, ButtonOption::Animated(Color::Blue));

	auto	userFields = Container::Vertical({
		serverInput,
		usernameInput,
		passwordInput,
		testButton,
		signInButton,
		signUpButton,
	});

	auto banner = vbox(
		text(BANNER1),
		text(BANNER2),
		text(BANNER3),
		text(BANNER4),
		text(BANNER5),
		text(BANNER6),
		text("")
	);

	auto	renderer = Renderer(userFields, [&] {
		return (
			vbox({
				banner | hcenter | border,
				vbox({ // this vbox must be vertically centered
					filler(),
					window(
						text("Login"),
						vbox({
							window(
								text("Server: "),
								serverInput->Render()
							),
							window(
								text("Username: "),
								usernameInput->Render()
							),
							window(
								text("Password: "),
								passwordInput->Render()
							),
							vbox({
								testButton->Render() | flex,
								hbox({
									signInButton->Render() | flex,
									signUpButton->Render() | flex,
								}),
							})
						})) | size(WIDTH, GREATER_THAN, 30)| hcenter,
					warning | hcenter,
					filler()
				}) | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
//			| yframe | vscroll_indicator // use that for add scroll bar
		);
	});

	auto	event = CatchEvent(renderer, [&](Event event) {
		if (event == Event::Escape) {
			screen.ExitLoopClosure()();
			return (true);
		}
//		else if (event == Event::Character('\n')) {
//			if (!server.empty()) {
//				warning = text("Testing !") | color(Color::Blue);
//				testAction(); //dont' work
//			}
//			if (username.empty() || pass.empty())
//				warning = text("Empty fields !") | color(Color::Red);
//			else {
//				// try connection
//				screen.ExitLoopClosure()();
//			}
//			return (true);
//		}
		return (false);
	});

	screen.Loop(event);

	std::cout << "server: " << server << std::endl;
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
