/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/04 18:33:21 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <cstring>
#include <iostream>
#include <random>
#include <csignal>

#include "ftxui/component/screen_interactive.hpp"
#include "ftxui/dom/elements.hpp"
#include "ftxui/screen/screen.hpp"
#include "ftxui/component/component.hpp"

#include "pong-cli.h"
#include "CurlWrapper.hpp"
#include "PongCLI.hpp"
#include "User.hpp"

using namespace ftxui;

std::shared_ptr<Node> banner() {
	return (vbox(
		text(BANNER1),
		text(BANNER2),
		text(BANNER3),
		text(BANNER4),
		text(BANNER5),
		text(BANNER6),
		text("")
	));
}
enum Page {
	LoginPage,
	MainMenuPage,
	SettingsPage,
	GamePage,
};

CurlWrapper						curl("https://localhost:4443");
User							user;
ScreenInteractive				screen = ScreenInteractive::Fullscreen();
std::string						server = "https://localhost:4443";
std::string						username;
std::string						password;
std::shared_ptr<Node>			info = text("");
bool							tokenGet = false;
Page							currentPage = Page::LoginPage;
std::shared_ptr<ComponentBase>	render = Container::Vertical({});
std::shared_ptr<ComponentBase>	pageComponent = Container::Vertical({});

void	signInAction() {
	if (!username.empty() && !password.empty()) {
		try {
			user.setUsername(username);
			user.setPassword(password);
			user.signInUser(curl);
			user.setAccessToken(jsonParser(curl.getResponse(), "access"));
			user.setRefreshToken(jsonParser(curl.getResponse(), "refresh"));
			info = text("(" + std::to_string(curl.getHTTPCode()) + ") Connexion success !") | color(Color::Green);
		}
		catch (std::exception &error) {
			if (curl.getHTTPCode() == 401)
				info = text("(" + std::to_string(curl.getHTTPCode()) + "): " + "Unknown user, please sign up") | color(Color::Red);
		}
//		screen.ExitLoopClosure()();
//		std::cout << "Sign In" << std::endl;
	}
	else
		info = text("Incomplete fields") | color(Color::Red);
}

void	signUpAction() {
	if (!username.empty() && !password.empty()) {
		try {
			user.setGuestTokens(curl);	//signup ok but not before fguirma push register modification for may register without token
			user.setUsername(username);
			user.setPassword(password);
			user.signUpUser(curl);
			user.setAccessToken(jsonParser(curl.getResponse(), "access"));
			user.setRefreshToken(jsonParser(curl.getResponse(), "refresh"));
			info = text("(" + std::to_string(curl.getHTTPCode()) + ") Connexion success !") | color(Color::Green);
		}
		catch (std::exception &error) {
			if (curl.getHTTPCode() >= 301)
				info = text("(" + std::to_string(curl.getHTTPCode()) + "): " + curl.getResponse()) | color(Color::Red);
		}
//		screen.ExitLoopClosure()();
//		std::cout << "Sign In" << std::endl;
	}
	else
		info = text("Incomplete fields") | color(Color::Red);
}

void	getTokenAction() {
	if (!server.empty()) {
		try {
			curl.setServer(server);
			user.setGuestTokens(curl);
			info = text("(" + std::to_string(curl.getHTTPCode()) + ") Guest up success !") | color(Color::Green);
			tokenGet = true;
		}
		catch (std::exception &error) {
			info = text("(" + std::to_string(curl.getHTTPCode()) + ") " + error.what()) | color(Color::Red);
			return ;
		}
	}
	else
		info = text("Empty server field !") | color(Color::Red);
};
void switchPage(Page newPage);


std::shared_ptr<ComponentBase> renderLoginPage() {
	{
//		Component serverInput = Button(std::string("Songs menu"), [&] { switchPage(Page::GamePage); });
//		pageComponent->Add(serverInput);
//		pageComponent->Add(ftxui::Button(std::string("Create song"), [&] { switchPage(Page::LoginPage); }));
//
//		return ftxui::Renderer([&] {
//			return ftxui::vbox({ftxui::hbox({ftxui::filler(),
//				ftxui::vbox({
//					ftxui::text(R"(  _____ ____  _   _  _____ _    _)"),
//					ftxui::text(R"( / ____/ __ \| \ | |/ ____| |  | |)"),
//					ftxui::text(R"(| |   | |  | |  \| | (___ | |  | |)"),
//					ftxui::text(R"(| |   | |  | | . ` |\___ \| |  | |)"),
//					ftxui::text(R"(| |___| |__| | |\  |____) | |__| |)"),
//					ftxui::text(R"( \_____\____/|_| \_|_____/ \____/)")
//				}),
//				ftxui::filler()}),
//				ftxui::text(" "),
//				ftxui::hbox({ftxui::filler(), ftxui::vbox({pageComponent->Render()}), ftxui::filler()})});
//		});
	}
	InputOption	serverOption;
	InputOption	usernameOption;
	InputOption	passwordOption;

	serverOption.multiline = false;
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

	Component	serverInput = Input(&server, serverOption);
	Component	usernameInput = Input(&username, usernameOption);
	Component	passwordInput = Input(&password, passwordOption);


	Component	signInButton = Button("Sign In", signInAction, ButtonOption::Animated(Color::Red));
	Component	signUpButton = Button("Sign Up", signUpAction, ButtonOption::Animated(Color::Green));
	Component	getTokenButton = Button("Guest", getTokenAction, ButtonOption::Animated(Color::Blue));

	pageComponent->Add(serverInput);
	pageComponent->Add(usernameInput);
	pageComponent->Add(passwordInput);
	pageComponent->Add(getTokenButton);
	pageComponent->Add(signInButton);
	pageComponent->Add(signUpButton);

	return (Renderer([&] {
		return (
			vbox({
				banner() | hcenter | border,
				vbox({ // this vbox must be vertically centered
					filler(),
					window(
						text("Login"),
						vbox({
							window(
								text("Server: "),
								pageComponent->Render()
							),
							window(
								text("Username: "),
								pageComponent->Render()
							),
							window(
								text("Password: "),
								pageComponent->Render()
							),
							vbox({
								pageComponent->Render() | flex,
								hbox({
									pageComponent->Render() | flex,
									pageComponent->Render() | flex,
								}),
							})
						})
					) | size(WIDTH, GREATER_THAN, 30) | hcenter,
					info | hcenter,
					filler()
				}) | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
			//			| yframe | vscroll_indicator // use that for add scroll bar
		);
	}));
}

std::shared_ptr<ComponentBase> pageRenderer() {
	switch(currentPage) {
		case Page::LoginPage:
			return (renderLoginPage());
		case Page::MainMenuPage:
			return (Container::Vertical({}));
		case Page::SettingsPage:
			return (Container::Vertical({}));
		case Page::GamePage:
			return (Container::Vertical({}));
	}
	return (Container::Vertical({}));
}

void switchPage(Page newPage) {
	if (currentPage != newPage) {
		currentPage = newPage;
		pageComponent->DetachAllChildren();
		render = pageRenderer();
	}
}

int main(void)
{
	// {
	// 	CurlWrapper curl("https://localhost:4443");
	// 	User user;
	// 	user.setUsername("test");
	// 	user.setPassword("pass");
	//
	//
	// 	PongCLI app(curl, user);
	// 	app.appRenderer();
	// }
	{
		curl.addHeader("Content-Type: application/json");

//		std::cout << "Page: " << currentPage << std::endl;
//		sleep(1);

		render = pageRenderer();
		auto	r = Renderer(pageComponent, [&] {
			return (render->Render());
		});


		auto finalRenderer = CatchEvent(r, [&](Event event) {
			if (event == Event::Escape) {
				screen.ExitLoopClosure()();
				return (true);
			}
			return (false);
		});

		screen.Loop(finalRenderer);

		std::cout << "server: " << server << std::endl;
		std::cout << "username: " << username << std::endl;
		std::cout << "password: " << password << std::endl;
	}
	{
	// 	CurlWrapper	curl("https://localhost:4443");
	// 	User		user;
	//
	// 	auto		screen = ScreenInteractive::Fullscreen();
	//
	// 	std::string	server;
	// 	InputOption	serverOption;
	// 	std::string	username;
	// 	InputOption	usernameOption;
	// 	std::string	password;
	// 	InputOption	passwordOption;
	//
	// 	//	serverOption.multiline = false;
	// 	usernameOption.multiline = false;
	// 	passwordOption.multiline = false;
	// 	passwordOption.password = true;
	// 	//maybe creat checkbox to reveal password
	//
	// 	auto stateTransformer = [](InputState state) {
	// 		if (state.hovered)
	// 			state.element |= bgcolor(Color::GrayLight);
	// 		else if (state.focused) {
	// 			state.element |= bgcolor(Color::GrayDark);
	// 		}
	// 		return (state.element);
	// 	};
	//
	// 	serverOption.transform = stateTransformer;
	// 	usernameOption.transform = stateTransformer;
	// 	passwordOption.transform = stateTransformer;
	//
	// 	auto	warning = text("");
	//
	// 	Component	serverInput = Input(&server, serverOption);
	// 	Component	usernameInput = Input(&username, usernameOption);
	// 	Component	passwordInput = Input(&password, passwordOption);
	//
	// 	auto	signInAction = [&] {
	// 		if (!username.empty() && !password.empty()) {
	// 			screen.ExitLoopClosure()();
	// 			std::cout << "Sign In" << std::endl;
	// 		}
	// 		else
	// 			warning = text("Empty fields") | color(Color::Red);
	// 	};
	// 	auto	signUpAction = [&] {
	// 		if (!username.empty() && !password.empty()) {
	// 			screen.ExitLoopClosure()();
	// 			std::cout << "Sign Up" << std::endl;
	// 		}
	// 		else
	// 			warning = text("Empty fields !") | color(Color::Red);
	// 	};
	// 	auto	testAction = [&] {
	// 		if (!server.empty()) {
	// 			try {
	// 				curl.setServer(server);
	// 				user.initializeConnection(curl);
	// 				warning = text("Connexion test success !") | color(Color::Green);
	// 			}
	// 			catch (std::exception &error) {
	// 				warning = text(error.what()) | color(Color::Red);
	// 			}
	// 		}
	// 		else
	// 			warning = text("Empty server field !") | color(Color::Red);
	// 	};
	// 	Component	signInButton = Button("Sign In", signInAction, ButtonOption::Animated(Color::Red));
	// 	Component	signUpButton = Button("Sign Up", signUpAction, ButtonOption::Animated(Color::Green));
	// 	Component	testButton = Button("Test", testAction, ButtonOption::Animated(Color::Blue));
	//
	// 	auto	userFields = Container::Vertical({
	// 		serverInput,
	// 		usernameInput,
	// 		passwordInput,
	// 		testButton,
	// 		signInButton,
	// 		signUpButton,
	// 	});
	//
	// 	auto banner = vbox(
	// 		text(BANNER1),
	// 		text(BANNER2),
	// 		text(BANNER3),
	// 		text(BANNER4),
	// 		text(BANNER5),
	// 		text(BANNER6),
	// 		text("")
	// 	);
	//
	// 	auto	renderer = Renderer(userFields, [&] {
	// 		return (
	// 			vbox({
	// 				banner | hcenter | border,
	// 				vbox({ // this vbox must be vertically centered
	// 					filler(),
	// 					window(
	// 						text("Login"),
	// 						vbox({
	// 							window(
	// 								text("Server: "),
	// 								serverInput->Render()
	// 							),
	// 							window(
	// 								text("Username: "),
	// 								usernameInput->Render()
	// 							),
	// 							window(
	// 								text("Password: "),
	// 								passwordInput->Render()
	// 							),
	// 							vbox({
	// 								testButton->Render() | flex,
	// 								hbox({
	// 									signInButton->Render() | flex,
	// 									signUpButton->Render() | flex,
	// 								}),
	// 							})
	// 						})) | size(WIDTH, GREATER_THAN, 30)| hcenter,
	// 					warning | hcenter,
	// 					filler()
	// 				}) | flex,
	// 			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
	// //			| yframe | vscroll_indicator // use that for add scroll bar
	// 		);
	// 	});
	//
	// 	auto	event = CatchEvent(renderer, [&](Event event) {
	// 		if (event == Event::Escape) {
	// 			screen.ExitLoopClosure()();
	// 			return (true);
	// 		}
	// //		else if (event == Event::Character('\n')) {
	// //			if (!server.empty()) {
	// //				warning = text("Testing !") | color(Color::Blue);
	// //				testAction(); //dont' work
	// //			}
	// //			if (username.empty() || pass.empty())
	// //				warning = text("Empty fields !") | color(Color::Red);
	// //			else {
	// //				// try connection
	// //				screen.ExitLoopClosure()();
	// //			}
	// //			return (true);
	// //		}
	// 		return (false);
	// 	});
	//
	// 	screen.Loop(event);
	//
	// 	std::cout << "server: " << server << std::endl;
	// 	std::cout << "username: " << username << std::endl;
	// 	std::cout << "password: " << password << std::endl;
	}
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
