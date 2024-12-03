(function PongGame() {

    const config = {
        canvasWidth: 800,
        canvasHeight: 600,
        paddleWidth: 30,
        paddleHeight: 200,
        ballSize: 30,
        ballSpeedIncrement: 1,
        maxBallSpeed: 70,
        animationDuration: 800,
        font: "48px Arial",
        fontColor: "white",
        defaultBallSpeed : 2,
        winningScore: 3,
        enemyScore : {},
        playerScore : {},
        countDown : {
            steps : 3,
            delay : 2000,
        }
    };

    config.enemyScore = {
        y : config.canvasHeight / 2,
        x : config.canvasWidth / 4
    }

    config.playerScore = {
        y : config.enemyScore.y,
        x : config.enemyScore.x * 3
    }

    const state = {
        isGameActive: false,
        isCountDownActive: false,
        isGamePaused: false,
        playerScore: 0,
        enemyScore: 0,
        ball: {
            x: config.canvasWidth / 2 - config.ballSize / 2,
            y: config.canvasHeight / 2 - config.ballSize / 2,
            speedX: config.defaultBallSpeed,
            speedY: config.defaultBallSpeed,
        },
        paddles: {
            left: {
                y: (config.canvasHeight - config.paddleHeight) / 2,
                blockGlide: false,
            },
            right: {
                y: (config.canvasHeight - config.paddleHeight) / 2,
                blockGlide: false,
            },
        },
        keys: {},
        cancelAnimation: false,
    };

    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    canvas.width = config.canvasWidth;
    canvas.height = config.canvasHeight;

    const paddleImage = new Image();
    paddleImage.src = "/assets/paddle.png";
    const ballImage = new Image();
    ballImage.src = "/assets/ball.png";

    ctx.font = config.font;
    ctx.fillStyle = config.fontColor;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    state.keys[' '] = false;

    document.addEventListener("keydown", (e) => {
        if (e.key === ' ' && state.keys[e.key] !== undefined && state.isGamePaused)
            return;
        else
            state.keys[e.key] = true;
    });
    document.addEventListener("keyup", (e) => (state.keys[e.key] = undefined));

    document.getElementById("replayFront").addEventListener("click", event => {
        event.target.blur();
        resumeGame();
        stopGame(true);
        setTimeout(()=>{
            resetGame();
            startGame();
        }, config.animationDuration + 100);
    });

    function startGame() {
        state.isGameActive = true;
        state.cancelAnimation = false;
        console.log('game started');
        
        startCountdown();
        function gameLoop() {
            if (!state.isGameActive) return;
            
            updateGameState();
            if (!state.isGamePaused)
                drawGame();
            
            requestAnimationFrame(gameLoop);
        }
        gameLoop();
    }

    function resetGame(){
        state.playerScore = 0;
        state.enemyScore = 0;
        state.ball =  {
            x: config.canvasWidth / 2 - config.ballSize / 2,
            y: config.canvasHeight / 2 - config.ballSize / 2,
            speedX: config.defaultBallSpeed,
            speedY: config.defaultBallSpeed,
        },
        state.paddles.left.y = (config.canvasHeight - config.paddleHeight) / 2;
        state.paddles.right.y = state.paddles.left.y;
    }

    function pauseGame(onlyPause=true) {
        if (state.isCountDownActive || onlyPause) return;
        if (state.isGamePaused) return resumeGame(true);
        console.log('game paused')
        state.keys[' '] = false;
        state.isGamePaused = true;

        ctx.globalAlpha = 0.5;
        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.globalAlpha = 1.0; 

        ctx.fillStyle = "white";
        ctx.font = "72px Arial";
        ctx.fillText("Paused", canvas.width / 2, canvas.height / 2);
        ctx.font = config.font;
    }

    function resumeGame(fromPause=false){
        console.log('game resumed');
        if (fromPause)
            state.keys[' '] = false;
        state.isGamePaused = false;
    }
    
    function stopGame(animate=false) {
        console.log('game ended');
        state.isGameActive = false;
        if (animate){
            animatePaddlesToMiddle()
        }
        else{
            state.cancelAnimation = true;
        }
    }

    function startCountdown() {
        let currentStep = config.countDown.steps;
        state.isCountDownActive = true;
    
        function drawCountdown() {
            ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
            ctx.font = '96px Arial';
            ctx.fillText(
                currentStep,
                config.canvasWidth / 2,
                config.canvasHeight / 2
            );
            ctx.font = config.font;
        }
    
        function step() {
            if (!state.isGameActive){
                state.isCountDownActive = false;
                return;
            }
            if (currentStep > 0) {
                drawCountdown();
                currentStep--;

                setTimeout(step, config.countDown.delay / config.countDown.steps);
            }
            else 
                state.isCountDownActive = false;
        }
    
        step();
    }

    function animatePaddlesToMiddle(){
        const startTime = performance.now();
        const startLeft = state.paddles.left.y;
        const startRight = state.paddles.right.y;
        const target = (config.canvasHeight - config.paddleHeight) / 2;

        function updatePaddleAnimation(currentTime) {
            if (state.cancelAnimation) return;

            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / config.animationDuration, 1);

            const easeOutProgress = 1 - Math.pow(1 - progress, 3);

            state.paddles.left.y = startLeft + (target - startLeft) * easeOutProgress;
            state.paddles.right.y = startRight + (target - startRight) * easeOutProgress;

            drawPaddleReturn();

            if (progress < 1) {
                requestAnimationFrame(updatePaddleAnimation);
            } else {
                cancelAnimation = true;
            }
        }
        requestAnimationFrame(updatePaddleAnimation);
    }

    function drawPaddleReturn(){
        ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
        ctx.drawImage(
            paddleImage, 0, state.paddles.left.y,
            config.paddleWidth, config.paddleHeight
        );

        ctx.drawImage(
            paddleImage,
            config.canvasWidth - config.paddleWidth,
            state.paddles.right.y,
            config.paddleWidth,
            config.paddleHeight
        );

        ctx.fillText('Game over', config.canvasWidth / 2, config.canvasHeight / 2);
    }

    function handleUserInput(){
        if (state.keys[' '])
            pauseGame(false);
        if (state.isGamePaused) return;
        if (state.keys["ArrowUp"] && state.paddles.right.y > 0){
            if (!state.paddles.right.blockGlide || state.paddles.right.y - 10 > config.ballSize)
                state.paddles.right.y -= 10;
            else if (state.paddles.right.y - 10 <= config.ballSize)
                state.paddles.right.y = config.ballSize;
        }
        if (state.keys["ArrowDown"] && state.paddles.right.y < config.canvasHeight - config.paddleHeight){
            if (!state.paddles.right.blockGlide || state.paddles.right.y + config.paddleHeight + 10 < config.canvasHeight - config.ballSize)
                state.paddles.right.y += 10;
            else if (state.paddles.right.y + config.paddleHeight + 10 >= config.canvasHeight - config.ballSize)
                state.paddles.right.y = config.canvasHeight - config.ballSize - config.paddleHeight;
        }
        if (state.keys["w"] && state.paddles.left.y > 0){
            if (!state.paddles.left.blockGlide || state.paddles.left.y - 10 > config.ballSize)
                state.paddles.left.y -= 10;
            else if (state.paddles.left.y - 10 <= config.ballSize)
                state.paddles.left.y = config.ballSize;
        }
        if (state.keys["s"] && state.paddles.left.y < config.canvasHeight - config.paddleHeight){
            if (!state.paddles.left.blockGlide || state.paddles.left.y + config.paddleHeight + 10 < config.canvasHeight - config.ballSize)
                state.paddles.left.y += 10;
            else if (state.paddles.left.y + config.paddleHeight + 10 >= config.canvasHeight - config.ballSize)
                state.paddles.left.y = config.canvasHeight - config.ballSize - config.paddleHeight;
        }
    }

    function handleGoal(){
        if (state.ball.x + config.ballSize <= 0 || state.ball.x >= canvas.width){
			if (state.ball.x + config.ballSize <= 0) state.playerScore++;
			else state.enemyScore++;
			resetBall();
        }
    }

    function resetBall() {
        state.ball.x = (config.canvasWidth - config.ballSize) / 2;
        state.ball.y = (config.canvasHeight - config.ballSize) / 2;
        state.ball.speedX = (Math.random()) < 0.5 ? config.defaultBallSpeed : -config.defaultBallSpeed;
        state.ball.speedY = (Math.random()) < 0.5 ? config.defaultBallSpeed : -config.defaultBallSpeed;
    }

    function incrementBallSpeed(){
        (state.ball.speedX > 0) ? state.ball.speedX += config.ballSpeedIncrement : state.ball.speedX -= config.ballSpeedIncrement;
        (state.ball.speedY > 0) ? state.ball.speedY += config.ballSpeedIncrement : state.ball.speedY -= config.ballSpeedIncrement;
    }

    function handlePaddleSides(paddle){
        console.log(paddle.blockGlide);
        if (paddle.blockGlide){
            state.ball.speedY = -state.ball.speedY;
            if (Math.abs(state.ball.y - (paddle.y + config.paddleHeight)) <
                Math.abs(state.ball.y - (paddle.y)))
                state.ball.y = paddle.y + config.paddleHeight;
            else
                state.ball.y = paddle.y - config.ballSize;
        }
        else{
            state.ball.speedX = -state.ball.speedX;
            if (Math.abs(state.ball.speedX) < config.maxBallSpeed)
                incrementBallSpeed();
        }
    }

    function handlePaddleCollision(){
        //left paddle
        if (state.ball.x < config.paddleWidth &&
			state.ball.y + config.ballSize > state.paddles.left.y &&
			state.ball.y < state.paddles.left.y + config.paddleHeight){
            handlePaddleSides(state.paddles.left);
        }
        else if (state.ball.x < config.paddleWidth)
            state.paddles.left.blockGlide = true;
        else
            state.paddles.left.blockGlide = false;

        //right paddle
        if (state.ball.x + config.ballSize > config.canvasWidth - config.paddleWidth &&
            state.ball.y + config.ballSize > state.paddles.right.y &&
            state.ball.y < state.paddles.right.y + config.paddleHeight){
            handlePaddleSides(state.paddles.right);
        }
        else if (state.ball.x + config.ballSize > config.canvasWidth - config.paddleWidth)
            state.paddles.right.blockGlide = true;
        else
            state.paddles.right.blockGlide = false;
    }

    function handleGameOver(){
        if (state.playerScore >= config.winningScore || state.enemyScore >= config.winningScore)
            stopGame(true);
    }

    function updateGameState() {
        handleUserInput();
        if (state.isGamePaused)
            return;
		
        if (!state.isCountDownActive){
            state.ball.x += state.ball.speedX;
            state.ball.y += state.ball.speedY;
        }

        if (state.ball.y <= 0 || state.ball.y + config.ballSize >= config.canvasHeight)
            state.ball.speedY = -state.ball.speedY;

        handleGoal();
        handlePaddleCollision();
		handleGameOver();
    }

    function clearCanvas(){
        if (!state.isCountDownActive)
            ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
        else {
            ctx.clearRect(0, 0, config.paddleWidth, config.canvasHeight);
            ctx.clearRect(config.canvasWidth - config.paddleWidth, 0, config.paddleWidth, config.canvasHeight);
        }
    }

    function drawGame() {

        clearCanvas();
        ctx.drawImage(paddleImage, 0, state.paddles.left.y, config.paddleWidth, config.paddleHeight);
        
        ctx.drawImage(
            paddleImage,
            config.canvasWidth - config.paddleWidth,
            state.paddles.right.y,
            config.paddleWidth,
            config.paddleHeight
        );
        
        if (!state.isCountDownActive) {
            ctx.fillText(`${state.playerScore}`, config.playerScore.x, config.playerScore.y);
            ctx.fillText(`${state.enemyScore}`, config.enemyScore.x, config.enemyScore.y);
            ctx.drawImage(ballImage, state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        }
    }
    
    window.PongGame = {startGame, stopGame, pauseGame, resumeGame};
})();

// let socket;

// function initSocket(){
// 	socket = io('wss://localhost:4443/', {
// 		auth : {
// 			'token' : getAccessToken()
// 		},
// 		path: "ws"
// 	});

// 	console.log(socket);

// 	// socket.on("my message", ...args => {
// 	// 	console.log(args);
// 	// })
// }

document.getElementById('playGame').addEventListener('click', async event => {
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/duel/`, 'POST');
	}
	catch(error) {
		console.log(error);
	}
	initSocket();
})

document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
    window.PongGame.resumeGame();
})

document.getElementById('testA').addEventListener('click', event => {
    event.preventDefault();
    window.PongGame.stopGame();
})


async function initGame(){
    await indexInit(false);
    window.PongGame.startGame();
}

initGame();