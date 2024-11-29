/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.cpp                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:19 by xcharra           #+#    #+#             */
/*   Updated: 2024/11/29 13:37:18 by xcharra          ###   ########.fr       */
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

	InputOption password_option;
	password_option.password = true;
	Component	username_input = Input(&username, "Username");
	Component	password_input = Input(&password, "Password", password_option);

	username_input |= CatchEvent([&](Event event) {
		bool ret = (ftxui::Event::Character('\n') == event);
		return ret;
	});
	password_input |= CatchEvent([&](Event event) {
		bool ret = (ftxui::Event::Character('\n') == event);
		return ret;
	});

	auto	component = Container::Vertical({
		username_input,
		password_input,
	});

	auto	renderer = Renderer(component, [&] {
		return vbox({
			hbox(username_input->Render()),
			hbox(password_input->Render())
		}) | border;
	});

	screen.Loop(renderer);
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
