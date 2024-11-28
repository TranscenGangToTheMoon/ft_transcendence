(function PongGame() {
    let isGameActive = false;
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = 800;
    canvas.height = 600;
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const paddleWidth = 20;
    const paddleHeight = 200;
    const paddleImage = new Image();
    paddleImage.src = "/assets/paddle.png";
    let leftPaddleY = (canvasHeight - paddleHeight) / 2; // Centre gauche
    let rightPaddleY = (canvasHeight - paddleHeight) / 2;
    const ballImage = new Image();
    ballImage.src = "/assets/ball.png"; // Chemin de l'image de la balle
    ballImage.onload = () => (console.log('ouais ouais oauis'))
    const ballSize = 30; 
    let ballX = canvasWidth / 2;
    let ballY = canvasHeight / 2;
    let ballSpeedX = 4;
    let ballSpeedY = 4;
    let gameState = {};
    const playerScoreDiv = document.getElementById('playerScore');
    const enemyScoreDiv = document.getElementById('enemyScore');
    let playerScore = 0;
    let enemyScore = 0;

    //TEXT STYLE
    ctx.font = "48px Arial";
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    
    let keys = {};

    document.addEventListener("keydown", (e) => {
      keys[e.key] = true;
    });

    document.addEventListener("keyup", (e) => {
      keys[e.key] = false;
    });

    function startGame() {
        enemyScoreDiv.innerText = '0';
        playerScoreDiv.innerText = '0';
        isGameActive = true;
        console.log('game started');
        
        function gameLoop() {
            if (!isGameActive) return;
            
            updateGameState();
            drawGame();
            
            requestAnimationFrame(gameLoop);
        }
        gameLoop();
    }
    
    function stopGame() {
        console.log('game ended');
        isGameActive = false;
    }
    
    function updateGameState() {
        if (keys["ArrowUp"] && rightPaddleY > 0) rightPaddleY -= 10;
        if (keys["ArrowDown"] && rightPaddleY < canvasHeight - paddleHeight) rightPaddleY += 10;

        if (keys["w"] && leftPaddleY > 0) leftPaddleY -= 10;
        if (keys["s"] && leftPaddleY < canvasHeight - paddleHeight) leftPaddleY += 10;
        // if (keys['q']) ballY += ballSpeedY;
        // ballX += ballSpeedX;
        // ballY += ballSpeedY;

        console.log(ballY + ballSize, canvas.height);

        if (ballY <= 0 || ballY + ballSize >= canvas.height)
            ballSpeedY = -ballSpeedY;

        if (ballX <= 0 || ballX + ballSize >= canvas.width){
			if (ballX <= 0){
				playerScore++;
				playerScoreDiv.innerText = `${playerScore}`;
			}
			else {
				enemyScore++;
				enemyScoreDiv.innerText = `${enemyScore}`;
			}
			ballX = canvasWidth / 2;
			ballY = canvasHeight / 2;
			ballSpeedX = -ballSpeedX;
        }

        if (
            ballX < paddleWidth &&
            ballY + ballSize > leftPaddleY &&
            ballY < leftPaddleY + paddleHeight
          ) {
            ballSpeedX = -ballSpeedX;
          }
          if (
            ballX + ballSize > canvasWidth - paddleWidth &&
            ballY + ballSize > rightPaddleY &&
            ballY < rightPaddleY + paddleHeight
          ) {
            ballSpeedX = -ballSpeedX;
          }
          if (playerScore > 0 || enemyScore > 2){
            ctx.fillText('Game over', canvasWidth / 2, canvasHeight / 2);
            // stopGame();
          }
    }
    
    function drawGame() {
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);

        ctx.drawImage(ballImage, ballX, ballY, 30, 30);

        ctx.drawImage(paddleImage, 0, leftPaddleY, paddleWidth, paddleHeight);

        ctx.drawImage(
            paddleImage,
            canvasWidth - paddleWidth,
            rightPaddleY,
            paddleWidth,
            paddleHeight
        );
    }
    
    window.PongGame = { startGame, stopGame , isGameActive};
})();

document.getElementById('playGame').addEventListener('click', async event => {
	try {
		let data = apiRequest(getAccessToken(), `${baseAPIUrl}/play/duel/`, 'POST');
	}
	catch(error) {
		console.log(error);
	}
})

async function initGame(){
    await indexInit(false);
    window.PongGame.startGame();
}

initGame();