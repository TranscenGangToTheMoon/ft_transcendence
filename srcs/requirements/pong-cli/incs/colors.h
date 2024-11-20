/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   colors.h                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2023/05/24 17:44:16 by xcharra           #+#    #+#             */
/*   Updated: 2024/07/17 13:51:17 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef COLORS_H
# define COLORS_H

//Good Message
# define G_MSG(x)		BLUE << x << RESET
//Error Message
# define E_MSG(x)		RED << x << RESET
//Warning Message
# define W_MSG(x)		BYELLOW UNDERLINE << x << RESET
//Constructor Message
# define C_MSG(x)		YELLOW << x << RESET
//Information Message
# define I_MSG(x)		ITALIC << x << RESET
//Title Message
# define T_MSG(x)		BBGCYAN PURPLE << x << RESET
//Debug Message
# define D_MSG(x)		UNDERLINE RED << x << RESET

# define S			"\001\033"
# define E			"\002"

# define RESET		S "[000m" E
# define BOLD		S "[001m" E
# define FAINT		S "[002m" E
# define ITALIC		S "[003m" E
# define UNDERLINE	S "[004m" E
# define SBLINK		S "[005m" E
# define FBLINK		S "[006m" E
# define REVERSE	S "[007m" E
# define HIDE		S "[008m" E
# define STRIKE		S "[009m" E

# define BLACK		S "[030m" E
# define RED		S "[031m" E
# define GREEN		S "[032m" E
# define YELLOW		S "[033m" E
# define BLUE		S "[034m" E
# define PURPLE		S "[035m" E
# define CYAN		S "[036m" E
# define GREY		S "[037m" E

# define BBLACK		S "[090m" E
# define BRED		S "[091m" E
# define BGREEN		S "[092m" E
# define BYELLOW	S "[093m" E
# define BBLUE		S "[094m" E
# define BPURPLE	S "[095m" E
# define BCYAN		S "[096m" E
# define BGREY		S "[097m" E

# define BGBLACK	S "[040m" E
# define BGRED		S "[041m" E
# define BGGREEN	S "[042m" E
# define BGYELLOW	S "[043m" E
# define BGBLUE		S "[044m" E
# define BGPURPLE	S "[045m" E
# define BGCYAN		S "[046m" E
# define BGGREY		S "[047m" E

# define BBGBLACK	S "[100m" E
# define BBGRED		S "[101m" E
# define BBGGREEN	S "[102m" E
# define BBGYELLOW	S "[103m" E
# define BBGBLUE	S "[104m" E
# define BBGPURPLE	S "[105m" E
# define BBGCYAN	S "[106m" E
# define BBGGREY	S "[107m" E

#endif