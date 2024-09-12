//has to take coords as parameters
function draw(x_coord, y_coord) {
	const canvas = document.getElementById("canvas");
	if (canvas.getContext) {
		const ctx = canvas.getContext("2d");

		ctx.beginPath();
		const x = x_coord;
		const y = y_coord;
		const radius = 20; // Arc radius
		const startAngle = 0; // Starting point on circle
		const endAngle = Math.PI + (Math.PI * 2) / 2; // End point on circle
		const counterclockwise = 3 % 2 !== 0; // clockwise or counterclockwise

		ctx.arc(x, y, radius, startAngle, endAngle, counterclockwise);
    	ctx.fill();
	}
}

//JavaScript game code here
draw(50, 50);
