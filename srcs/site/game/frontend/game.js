function draw() {
	const canvas = document.getElementById("canvas");
	if (canvas.getContext) {
		const ctx = canvas.getContext("2d");

		ctx.beginPath();
		const x = 25 + 2 * 50; // x coordinate
		const y = 25 + 3 * 50; // y coordinate
		const radius = 20; // Arc radius
		const startAngle = 0; // Starting point on circle
		const endAngle = Math.PI + (Math.PI * 2) / 2; // End point on circle
		const counterclockwise = 3 % 2 !== 0; // clockwise or counterclockwise

		ctx.arc(x, y, radius, startAngle, endAngle, counterclockwise);
    	ctx.fill();
	}
}

draw();
