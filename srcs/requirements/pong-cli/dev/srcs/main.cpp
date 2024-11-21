#include <iostream>
#include "../incs/colors.h"
#include "ftxui/include/ftxui/dom/elements.hpp"
#include "ftxui/include/ftxui/screen/screen.hpp"

int main() {
	std::cout << G_MSG("Welcome in pong-cli!") << std::endl;
	const std::string hello {"Hello, World!"};
	ftxui::Element doc = ftxui::hbox(
		ftxui::text( hello ) | ftxui::border
	);
	ftxui::Screen screen = ftxui::Screen::Create(
		ftxui::Dimension::Fixed( hello.length() + 1 ),
		ftxui::Dimension::Fixed(3)
	);

	ftxui::Render(screen, doc);
	screen.Print();
	std::cout << '\n';
	return (0);
}