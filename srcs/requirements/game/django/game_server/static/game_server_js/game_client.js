import {Position} from './position.js';
import {Ball} from './ball.js';
import {Racket} from './racket.js';
import {Player} from './player.js';

let url = `ws://${window.location.host}/ws/socket-server/`
let socket = new WebSocket(url);


function draw(ball, player, opponent) {
	let ctx = canvas.getContext("2d");
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.fillStyle = "black";
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	ctx.fillStyle = "white";
	ctx.fillRect(ball.position.x, ball.position.y, ball.radius, ball.radius);
	ctx.fillRect(player.racket.position.x, player.racket.position.y, player.racket.width, player.racket.height);
	ctx.fillRect(opponent.racket.position.x, opponent.racket.position.y, opponent.racket.width, opponent.racket.height);
}

function update(ball, player, opponent) {
	ball.update_position();
	if (ball.position.y < 0 || ball.position.y > canvas.height) {
		ball.wall_bounce();
	}
	if (ball.position.x < player.racket.position.x + player.racket.width && ball.position.y > player.racket.position.y && ball.position.y < player.racket.position.y + player.racket.height) {
		ball.racket_bounce();
	}
	if (ball.position.x > opponent.racket.position.x && ball.position.y > opponent.racket.position.y && ball.position.y < opponent.racket.position.y + opponent.racket.height) {
		ball.racket_bounce();
	}
	if (player.racket.velocity != 0) {
		player.racket.update_position();
	}
	if (opponent.racket.velocity != 0) {
		opponent.racket.update_position();
	}
	if (ball.position.x < -ball.radius && (ball.position.y - ball.radius < player.racket.position.y || ball.position.y + ball.radius > player.racket.position.y + player.racket.height) && (ball.position.y > canvas.height || ball.position.y < 0)) {
		opponent.score++;
		console.log("ballposition: " + ball.position.x + " " + ball.position.y);
		return 1;
	}
	if (ball.position.x > canvas.width + ball.radius && (ball.position.y - ball.radius < opponent.racket.position.y || ball.position.y + ball.radius > opponent.racket.position.y + opponent.racket.height) && (ball.position.y > canvas.height || ball.position.y < 0)) {
		player.score++;
		console.log("ballposition: " + ball.position.x + " " + ball.position.y);
		return 1;
	}
	return 0;
}

function random_direction() {
	return Math.random() * 2 * Math.PI;
}

export let canvas = document.getElementById("gameCanvas");
let player = new Player(new Racket(new Position(0, 0), 10, canvas.height), 0);
let opponent = new Player(new Racket(new Position(canvas.width - 10, 0), 10, canvas.height), 0);
let ball = new Ball(new Position(canvas.width / 2, canvas.height / 2), 10, 5);
let isGameActive = false;

document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowUp') {
        player.racket.move_up();
    } else if (event.key === 'ArrowDown') {
        player.racket.move_down();
    }
});

document.addEventListener('keyup', (event) => {
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
        player.racket.stop();
    }
});

function reset_ball_direction(ball, player, opponent) {
	if (player.score < opponent.score) {
			console.log("ball direction: " + ball.direction);
		while (Math.cos(ball.direction) <= (Math.sqrt(2) / 2)) {
			ball.direction = random_direction();
		}
	}
	else if (player.score > opponent.score) {
		while (Math.cos(ball.direction) >= -(Math.sqrt(2) / 2)) {
			console.log("ball direction: " + ball.direction);
			ball.direction = random_direction();
		}
	}
	else {
		while (Math.cos(ball.direction) >= -(Math.sqrt(2) / 2) && Math.cos(ball.direction) <= (Math.sqrt(2) / 2)) {
			console.log("ball direction: " + ball.direction);
			ball.direction = random_direction();
		}
	}
}

console.log("ball direction: " + ball.direction);

function drawCountdown(end_time) {
    const currentTime = new Date().getTime();
    const timeLeft = Math.max(0, end_time - currentTime);
    const secondsLeft = Math.ceil(timeLeft / 1000);

    // Clear the canvas
    let ctx = document.getElementById("gameCanvas").getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw the countdown
    ctx.font = '100px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(secondsLeft, canvas.width / 2, canvas.height / 2);

    // Check if the countdown is over
    if (timeLeft > 0) {
        requestAnimationFrame(() => {
        	drawCountdown(end_time);
        });
    } else {
        isGameActive = true;
		reset_game(ball, player, opponent);
		reset_ball_direction(ball, player, opponent)
        game_loop(ball, player, opponent);
    }
}

function reset_game(ball, player, opponent) {
	console.log("reset game");
	ball.position = new Position(canvas.width / 2, canvas.height / 2);
	reset_ball_direction(ball, player, opponent);
	player.racket.position = new Position(0, 0);
	opponent.racket.position = new Position(canvas.width - 10, 0);
}

function game_loop(ball, player, opponent) {
	console.log("start game loop");
	draw(ball, player, opponent);
	if (update(ball, player, opponent) == 1) {
		isGameActive = false;
		if (player.score >= 5 || opponent.score >= 5) {
			console.log("Game over");
			return ;
		}
		reset_game(ball, player, opponent)
		console.log("Player: " + player.score + " Opponent: " + opponent.score);
		draw(ball, player, opponent);
		drawCountdown(new Date().getTime() + 3000);
	}
	else {
		if (isGameActive) {
			requestAnimationFrame(() => {
				game_loop(ball, player, opponent);
			});
		}
	}
}


window.onload = function () {
	reset_ball_direction(ball, player, opponent);
	console.log("start countdown");
	drawCountdown(new Date().getTime() + 3000);
}
