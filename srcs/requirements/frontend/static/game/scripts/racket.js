import { canvas } from "./game_client.js";
export class Racket {
	constructor(position, width, height) {
		this.position = position;
		this.width = width;
		this.height = height;
		this.velocity = 0;
		this.moving = "stop";
	}
	move_up() {
		this.velocity = -7;
		console.log("up");
		// if (this.moving !== "up")
			//send message to server
		this.moving = "up";
	}
	move_down() {
		this.velocity = 7;
		console.log("down");
		// if (this.moving !== "down")
			//send message to server
		this.moving = "down";
	}
	stop() {
		console.log("stop");
		this.velocity = 0;
		// if (this.moving !== "stop")
			//send message to server
		this.moving = "stop";
	}
	update_position() {
		this.position.y += this.velocity;
		if (this.position.y < 0)
			this.position.y = 0;
		if (this.position.y + this.height > canvas.height)
			this.position.y = canvas.height - this.height;
	}
}
