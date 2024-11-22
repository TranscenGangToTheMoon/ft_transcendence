export class Ball {
	constructor(position, radius, initialVelocity) {
		this.position = position;
		this.direction = Math.PI / 2;
		this.radius = radius;
		this.velocity = initialVelocity;
	}
	wall_bounce() {
		this.direction = -this.direction;
	}
	racket_bounce() {
		this.direction = Math.sign(Math.sin(this.direction)) * Math.acos(-Math.cos(this.direction));
		this.velocity += 0.5;
	}
	update_position() {
		this.position.x += (this.velocity * Math.cos(this.direction));
		this.position.y += (this.velocity * Math.sin(this.direction));
	}
}
