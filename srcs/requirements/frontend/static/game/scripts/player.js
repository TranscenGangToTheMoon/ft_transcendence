export class Player {
	constructor(racket, score) {
		this.racket = racket;
		this.score = score;
	}
	reset_position() {
		this.racket.position = 0;
	}
}
