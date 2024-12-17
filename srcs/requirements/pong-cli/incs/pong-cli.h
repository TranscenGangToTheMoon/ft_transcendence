/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pong-cli.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: xcharra <xcharra@student.42lyon.fr>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2024/11/25 16:32:10 by xcharra           #+#    #+#             */
/*   Updated: 2024/12/16 12:45:04 by xcharra          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PONG_CLI_H
# define PONG_CLI_H

# include <iostream>
# include <string>
# include <future>

# include <cstdint>
# include <cstring>

# include <openssl/ssl.h>
# include <openssl/rsa.h>
# include <openssl/x509.h>
# include <openssl/evp.h>

# include "colors.h"

//libcurl
# include "curl/curl.h"

//ftxui
# include "ftxui/component/screen_interactive.hpp"
# include "ftxui/dom/elements.hpp"
# include "ftxui/screen/screen.hpp"
# include "ftxui/component/component.hpp"

//json
# include "nlohmann/json.hpp"

using namespace	ftxui;
using namespace	nlohmann;

typedef struct curl_slist	curl_slist_t;

// #define BANNER R"(
//                                         ___
//     ____  ____  ____  ____ _      _____/ (_)
//    / __ \/ __ \/ __ \/ __ `/_____/ ___/ / /
//   / /_/ / /_/ / / / / /_/ /_____/ /__/ / /
//  / .___/\____/_/ /_/\__, /      \___/_/_/
// /_/                /____/
// )"

#define BANNER1 R"(                                        ___ )"
#define BANNER2 R"(    ____  ____  ____  ____ _      _____/ (_))"
#define BANNER3 R"(   / __ \/ __ \/ __ \/ __ `/_____/ ___/ / / )"
#define BANNER4 R"(  / /_/ / /_/ / / / / /_/ /_____/ /__/ / /  )"
#define BANNER5 R"( / .___/\____/_/ /_/\__, /      \___/_/_/   )"
#define BANNER6 R"(/_/                /____/                   )"

#endif
