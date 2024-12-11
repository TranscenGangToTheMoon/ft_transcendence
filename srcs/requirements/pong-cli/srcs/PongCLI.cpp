/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   PongCLI.cpp                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/12/03 17:35:02 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/11 16:04:51 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <iostream>
#include <future>
#include "PongCLI.hpp"


#include "colors.h"
#include "pong-cli.h"

using namespace nlohmann;

PongCLI::PongCLI(CurlWrapper &curl, User &user) : _curl(curl), _info(text("")), _currentPage(Page::LoginPage),
	_user(user), _password(), _server("https://localhost:4443"), _username() {
	std::cout << C_MSG("PongCLI parametric constructor called") << std::endl;
}

PongCLI::~PongCLI() {
	std::cout << C_MSG("PongCLI destructor called") << std::endl;
}

void PongCLI::run() {
	pageRenderer();
}

void PongCLI::pageRenderer() {
	switch(_currentPage) {
		case LoginPage:
			return (renderLoginPage());
		case Page::MainMenuPage:
			return (renderMainMenuPage());
		case Page::SettingsPage:
			return (renderSettingsPage());
		case Page::GamePage:
			return (renderGamePage());
	}
	return (renderDefaultPage());
}

void PongCLI::changePage(Page newPage) {
	if (_currentPage != newPage) {
		_currentPage = newPage;
		pageRenderer();
	}
}

void	PongCLI::loginAction(std::string &server, std::string &username, std::string &password) {
	if (!server.empty() && !username.empty() && !password.empty()) {
		_server = server;
		_username = username;
		_password = password;
		try {
			_curl.setServer(_server);
			_user.setUsername(_username);
			_user.setPassword(_password);
			_user.loginUser(_curl);
			_user.setAccessToken(jsonParser(_curl.getResponse(), "access"));
			_user.setRefreshToken(jsonParser(_curl.getResponse(), "refresh"));
			_curl.addHeader("Authorization: Bearer " + _user.getAccessToken());
			_info = text("(" + std::to_string(_curl.getHTTPCode()) + ") Connexion success !") | color(Color::Green);
			changePage(Page::MainMenuPage);
			_screen.ExitLoopClosure()();
		}
		catch (std::exception &error) {
			if (_curl.getHTTPCode() == 401)
				_info = text("(" + std::to_string(_curl.getHTTPCode()) + "): " + "Unknown user, please sign up") | color(Color::Red);
			else if (_curl.getHTTPCode() >= 301)
				_info = text("(" + std::to_string(_curl.getHTTPCode()) + "): " + _curl.getResponse()) | color(Color::Red);
		}
	}
	else if (server.empty() || username.empty() || password.empty()) {
		_info = text("Incomplete field(s)" + server + " " + username + " " + password) | color(Color::Red);
		return;
	}
}

void	PongCLI::registerAction(std::string &server, std::string &username, std::string &password) {
	if (!server.empty() && !username.empty() && !password.empty()) {
		_server = server;
		_username = username;
		_password = password;
		try {
			_curl.setServer(_server);
			_user.setUsername(_username);
			_user.setPassword(_password);
			_user.registerUser(_curl);
			_user.setAccessToken(jsonParser(_curl.getResponse(), "access"));
			_user.setRefreshToken(jsonParser(_curl.getResponse(), "refresh"));
			_info = text("(" + std::to_string(_curl.getHTTPCode()) + ") Connexion success !") | color(Color::Green);
			changePage(Page::MainMenuPage);
			_screen.ExitLoopClosure()();
		}
		catch (std::exception &error) {
			if (_curl.getHTTPCode() >= 301)
				_info = text("(" + std::to_string(_curl.getHTTPCode()) + "): " + _curl.getResponse()) | color(Color::Red);
		}
	}
	else if (server.empty() || username.empty() || password.empty()) {
		_info = text("Incomplete field(s)" + server + " " + username + " " + password) | color(Color::Red);
		return;
	}
}

void	PongCLI::guestUpAction(std::string &server) {
	if (!server.empty()) {
		_server = server;
		try {
			_curl.setServer(_server);
			_user.setGuestTokens(_curl);
			_info = text("(" + std::to_string(_curl.getHTTPCode()) + ") Guest up success !") | color(Color::Green);
			changePage(Page::MainMenuPage);
			_screen.ExitLoopClosure()();
		}
		catch (std::exception &error) {
			_info = text("(" + std::to_string(_curl.getHTTPCode()) + ") " + error.what()) | color(Color::Red);
		}
	}
	else if (server.empty()) {
		_info = text("Incomplete field(s)" + server) | color(Color::Red);
		return;
	}
};


void PongCLI::renderLoginPage() {
	// std::cout << C_MSG("LoginPage called") << std::endl;
	std::string	server = "https://localhost:4443";
	std::string	username;
	std::string	password;
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

	Component	loginButton = Button("Login", [this, &server, &username, &password] {
		loginAction(server, username, password);
	}, ButtonOption::Animated(Color::Red));
	Component	registerButton = Button("Register", [this, &server, &username, &password] {
		registerAction(server, username, password);
	},ButtonOption::Animated(Color::Green));
	Component	guestUpButton = Button("Guest up", [this, &server] {
		guestUpAction(server);
	}, ButtonOption::Animated(Color::Blue));

	Component	pageComponents = Container::Vertical({
		serverInput,
		usernameInput,
		passwordInput,
		guestUpButton,
		loginButton,
		registerButton
	});

	Component	render =  Renderer(pageComponents, [&] {
		return (
			vbox({
				getBanner() | hcenter | border,
				vbox({
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
								guestUpButton->Render() | flex,
								hbox({
									loginButton->Render() | flex,
									registerButton->Render() | flex,
								}),
							})
						})
					) | size(WIDTH, GREATER_THAN, 30) | hcenter,
					_info | hcenter,
					filler()
				}) | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
		);
	});

	Component	finalRender = CatchEvent(render, [&](const Event &event) {
		if (event == Event::Escape) {
			_screen.ExitLoopClosure()();
			return (true);
		}
		return (false);
	});

	_screen.Loop(finalRender);
}

void PongCLI::renderMainMenuPage() {
	int			id = 9;
	std::string	username;
	bool		guest;
//	profile_picture: None, // not handle yet
//	status: None, // not handle yet
	int			stardust = 12996;
	int			aura = 1200;
//	current_rank: None, // not handle yes
//	friends: None,
	bool		accept_friend_request;
	std::string	accept_chat_from;

	std::atomic<bool>	reloading = true;

	auto		searchMatchDuel = Button("Launch async task", [this, &reloading] {
		reloading = true;
		_info = text("Async task running...") | color(Color::Yellow);
		_screen.RequestAnimationFrame();
		auto res = std::async(std::launch::async, [this] {
			// search match, request to an API, take time
			// response from sse
			std::this_thread::sleep_for(std::chrono::seconds(5));

//			_info = text("Match found !") | color(Color::Green);
			(void)this;
		});

		// loading animation
		for (int i = 0; i < 10; i++) {
			std::this_thread::sleep_for(std::chrono::seconds(1));
			_info = text("Search match..." + std::to_string(i)) | color(Color::Yellow);
			_screen.RequestAnimationFrame();
		}

		// wait for async task to finish
		res.get();
		// make socket connection to game server
//		changePage(Page::GamePage)
	}, ButtonOption::Animated(Color::Red));

	Component	pageComponents = Container::Vertical({
		searchMatchDuel,
	});
	std::string	json;
	std::string info;
	try {
		_curl.GET("/api/users/me/", "");
		auto json = json::parse(_curl.getResponse());

		username = json["username"];
		guest = json["is_guest"];
		stardust = json["coins"];
		aura = json["trophies"];
		accept_friend_request = json["accept_friend_request"];
		accept_chat_from = json["accept_chat_from"];
		//request to /api/user/me >> get user information
	}
	catch (std::exception &error) {
		_info = text("(" + std::to_string(_curl.getHTTPCode()) + ") " + error.what() + info) | color(Color::Red);
	}

	auto render = Renderer(pageComponents, [&] {
		return (
			vbox({
				getBanner() | hcenter | border,
				vbox({
					gridbox({{
						window(
							text("Profile: "),
							hbox({ // Profile
								vbox({ // left
									text("id: ") | vcenter | yflex_grow,
									text("username: ") | vcenter | yflex_grow,
									text("guest: ") | vcenter | yflex_grow,
									text("stardust: ") | vcenter | yflex_grow,
									text("aura: ") | vcenter | yflex_grow,
									text("accept_friend_request: ") | vcenter | yflex_grow,
									text("accept_chat_from: ") | vcenter | yflex_grow,
								}),
								separator(),
								vbox({ // right
									text(std::to_string(id)) | vcenter | yflex_grow,
									text(username) | vcenter | yflex_grow,
									text(guest ? "true" : "false") | vcenter | yflex_grow,
									text(std::to_string(stardust)) | vcenter | yflex_grow,
									text(std::to_string(aura)) | vcenter | yflex_grow,
									text(accept_friend_request ? "true" : "false") | vcenter | yflex_grow,
									text(accept_chat_from) | vcenter | yflex_grow,
								}) | flex,
							}) | flex
						),
						vbox({ //game
							vbox({
								text("Normal Game") | center | border | flex,
								searchMatchDuel->Render(),
							}) | yflex_grow,
							vbox({
								text("Ranked Game") | center | border | flex
							}) | yflex_grow
						}) | flex
					}}) | flex,
					_info | hcenter,
				}) | xflex_grow | yflex_grow | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
		);
	});

	auto	finalRenderer = CatchEvent(render, [&](Event event) {
		if (event == Event::Escape) {
			reloading = false;
			_screen.ExitLoopClosure()();
			return (true);
		}
		return (false);
	});

	auto	screenRedraw = std::thread([&] {
		int	i = 0;
		while (reloading) {
			_screen.PostEvent(Event::Custom);
			std::this_thread::sleep_for(std::chrono::seconds(1));
//			_info = text("Redraw " + std::to_string(i)) | color(Color::Red);
			i++;
		}
	});

	_screen.Loop(finalRenderer);
	reloading = false;
	screenRedraw.join();
}

void PongCLI::renderSettingsPage() {
	Component	pageComponents = Container::Vertical({
	});

	auto render = Renderer(pageComponents, [&] {
		return (
			vbox({
				getBanner() | hcenter | border,
				vbox({
					text("Settings page") | hcenter | border | flex,
					_info | hcenter,
				}) | xflex_grow | yflex_grow | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
		);
	});

	auto finalRenderer = CatchEvent(render, [&](Event event) {
		if (event == Event::Escape) {
			_screen.ExitLoopClosure()();
			return (true);
		}
		return (false);
	});

	_screen.Loop(finalRenderer);
}

void PongCLI::renderGamePage() {
	Component	pageComponents = Container::Vertical({
	});

	auto render = Renderer(pageComponents, [&] {
		return (
			vbox({
				getBanner() | hcenter | border,
				vbox({
					text("Game page") | hcenter | border | flex,
					_info | hcenter,
				}) | xflex_grow | yflex_grow | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
		);
	});

	auto finalRenderer = CatchEvent(render, [&](Event event) {
		if (event == Event::Escape) {
			_screen.ExitLoopClosure()();
			return (true);
		}
		return (false);
	});

	_screen.Loop(finalRenderer);
}

void PongCLI::renderDefaultPage() {
	Component	pageComponents = Container::Vertical({
	});

	auto render = Renderer(pageComponents, [&] {
		return (
			vbox({
				getBanner() | hcenter | border,
				vbox({
					text("Default page") | hcenter | border | flex,
					_info | hcenter,
				}) | xflex_grow | yflex_grow | flex,
			}) | border | size(WIDTH, GREATER_THAN, 150) | size(HEIGHT, GREATER_THAN, 40)
		);
	});

	auto finalRenderer = CatchEvent(render, [&](Event event) {
		if (event == Event::Escape) {
			_screen.ExitLoopClosure()();
			return (true);
		}
		return (false);
	});

	_screen.Loop(finalRenderer);
}

Element PongCLI::getBanner() {
	return (vbox( text(BANNER1), text(BANNER2), text(BANNER3),
		text(BANNER4), text(BANNER5), text(BANNER6), text("")));
}

void PongCLI::setPassword(const std::string &password) { _password = password; }
void PongCLI::setServer(const std::string &server) { _server = server; }
void PongCLI::setUsername(const std::string &username) { _username = username; }

const std::string &PongCLI::getPassword() const { return (_password); }
const std::string &PongCLI::getServer() const { return (_server); }
const std::string &PongCLI::getUsername() const { return (_username); }

