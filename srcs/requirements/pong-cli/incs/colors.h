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

# define START		"\001\033"
# define END		"\002"

# define RESET		START "[000m" END
# define BOLD		START "[001m" END
# define FAINT		START "[002m" END
# define ITALIC		START "[003m" END
# define UNDERLINE	START "[004m" END
# define SBLINK		START "[005m" END
# define FBLINK		START "[006m" END
# define REVERSE	START "[007m" END
# define HIDE		START "[008m" END
# define STRIKE		START "[009m" END

# define BLACK		START "[030m" END
# define RED		START "[031m" END
# define GREEN		START "[032m" END
# define YELLOW		START "[033m" END
# define BLUE		START "[034m" END
# define PURPLE		START "[035m" END
# define CYAN		START "[036m" END
# define GREY		START "[037m" END

# define BBLACK		START "[090m" END
# define BRED		START "[091m" END
# define BGREEN		START "[092m" END
# define BYELLOW	START "[093m" END
# define BBLUE		START "[094m" END
# define BPURPLE	START "[095m" END
# define BCYAN		START "[096m" END
# define BGREY		START "[097m" END

# define BGBLACK	START "[040m" END
# define BGRED		START "[041m" END
# define BGGREEN	START "[042m" END
# define BGYELLOW	START "[043m" END
# define BGBLUE		START "[044m" END
# define BGPURPLE	START "[045m" END
# define BGCYAN		START "[046m" END
# define BGGREY		START "[047m" END

# define BBGBLACK	START "[100m" END
# define BBGRED		START "[101m" END
# define BBGGREEN	START "[102m" END
# define BBGYELLOW	START "[103m" END
# define BBGBLUE	START "[104m" END
# define BBGPURPLE	START "[105m" END
# define BBGCYAN	START "[106m" END
# define BBGGREY	START "[107m" END

#endif