/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   PongCLI.cpp                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/12/03 17:35:02 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/03 19:10:04 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include <iostream>
#include "PongCLI.hpp"
#include "colors.h"

PongCLI::PongCLI(CurlWrapper &curl, User &user) : _curl(curl), _user(user) {
	std::cout << C_MSG("PongCLI parametric constructor called") << std::endl;
}

//PongCLI::PongCLI(void) {
//	std::cout << C_MSG("PongCLI default constructor called") << std::endl;
//}
//
//PongCLI::PongCLI(PongCLI const &src) {
//	std::cout << C_MSG("PongCLI default copy constructor called") << std::endl;
//
//	*this = src;
//}

PongCLI::~PongCLI() {
	std::cout << C_MSG("PongCLI destructor called") << std::endl;
}

PongCLI &PongCLI::operator=(PongCLI const &rhs) {
	std::cout << C_MSG("PongCLI assignment operator called") << std::endl;

	if (this != &rhs)
		(void) rhs;
	return (*this);
}
