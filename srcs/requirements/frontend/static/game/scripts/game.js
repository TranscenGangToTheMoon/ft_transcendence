(function PongGame() {

    const config = {
        canvasWidth: 800,
        canvasHeight: 600,
        paddleWidth: 30,
        paddleHeight: 200,
        ballSize: 20,
        maxBallSpeed: 15,
        animationDuration: 800,
        font: "48px Arial",
        fontColor: "white",
        defaultBallSpeed : 0,
        ballSpeedIncrement: 1,
        winningScore: 3,
        enemyScore : {},
        playerScore : {},
        countDown : {
            steps : 3,
            delay : 2000,
        },
        maxBounceAngle : 2 * (Math.PI / 5),
        displayDemo: false
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
            speed: config.defaultBallSpeed,
        },
        paddles: {
            left: {
                x: 100,
                y: (config.canvasHeight - config.paddleHeight) / 2,
                blockGlide: false,
            },
            right: {
                x: config.canvasWidth - config.paddleWidth - 100,
                y: (config.canvasHeight - config.paddleHeight) / 2,
                blockGlide: false,
            },
            // leftRight :{
            //     x : 100 + 100,
            //     y : (config.canvasHeight - config.paddleHeight) / 2,
            //     blockGlide: false,
            // },
        },
        countDown: {
            currentStep: config.countDown.steps,
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
        state.ball.speed = config.defaultBallSpeed;
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
            speed: config.defaultBallSpeed, 
        },
        state.paddles.left.y = (config.canvasHeight - config.paddleHeight) / 2;
        state.paddles.right.y = state.paddles.left.y;
    }

    function pauseGame(onlyPause=true) {
        if (state.isCountDownActive || !state.isGameActive) return;
        if (state.isGamePaused && !onlyPause) return resumeGame(true);
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

    function drawCountdown() {
        ctx.font = '96px Arial';
        ctx.fillText(
            state.countDown.currentStep + 1,
            config.canvasWidth / 2,
            config.canvasHeight / 2
        );
        ctx.font = config.font;
    }

    function startCountdown() {
        state.isCountDownActive = true;
    
        function step() {
            state.countDown.currentStep--;
            if (!state.isGameActive){
                state.isCountDownActive = false;
                state.countDown.currentStep = config.countDown.steps;
                return;
            }
            if (state.countDown.currentStep >= 0) {
                drawCountdown();    
                setTimeout(step, config.countDown.delay / (config.countDown.steps + 1));
            }
            else{
                state.countDown.currentStep = config.countDown.steps;
                state.isCountDownActive = false;
            }
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
            paddleImage, state.paddles.left.x, state.paddles.left.y,
            config.paddleWidth, config.paddleHeight
        );

        ctx.drawImage(
            paddleImage,
            state.paddles.right.x,
            state.paddles.right.y,
            config.paddleWidth,
            config.paddleHeight
        );

        ctx.fillText('Game over', config.canvasWidth / 2, config.canvasHeight / 2);
    }

    function handleUserInput(){
        if (state.keys['d']) config.displayDemo ? config.displayDemo = false : config.displayDemo = true;
        if (state.keys[' '])
            pauseGame(false);
        if (state.isGamePaused) return;
        if (state.keys["ArrowUp"] && state.paddles.right.y > 0){
            if (!state.paddles.right.blockGlide || state.paddles.right.y - 10 > config.ballSize){
                state.paddles.right.y -= 10;
                socket.emit('move_up');
            }
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
        if (state.keys["o"] && state.paddles.leftRight.y > 0){
            if (!state.paddles.leftRight.blockGlide || state.paddles.leftRight.y - 10 > config.ballSize)
                state.paddles.leftRight.y -= 10;
            else if (state.paddles.leftRight.y - 10 <= config.ballSize)
                state.paddles.leftRight.y = config.ballSize;
        }
        if (state.keys["l"] && state.paddles.leftRight.y < config.canvasHeight - config.paddleHeight){
            if (!state.paddles.leftRight.blockGlide || state.paddles.leftRight.y + config.paddleHeight + 10 < config.canvasHeight - config.ballSize)
                state.paddles.leftRight.y += 10;
            else if (state.paddles.leftRight.y + config.paddleHeight + 10 >= config.canvasHeight - config.ballSize)
                state.paddles.leftRight.y = config.canvasHeight - config.ballSize - config.paddleHeight;
        }
    }

    function handleGoal(){
        if (state.ball.x + config.ballSize <= 0 || state.ball.x >= canvas.width){
			if (state.ball.x + config.ballSize <= 0) state.playerScore++;
			else state.enemyScore++;
			resetBall();
            // state.ball.speedX = -state.ball.speedX;
        }
    }

    function resetBall() {
        state.ball.x = (config.canvasWidth - config.ballSize) / 2;
        state.ball.y = (config.canvasHeight - config.ballSize) / 2;
        state.ball.speed = config.defaultBallSpeed;
        state.ball.speedX = (Math.random()) < 0.5 ? config.defaultBallSpeed : -config.defaultBallSpeed;
        state.ball.speedY = (Math.random()) < 0.5 ? config.defaultBallSpeed : -config.defaultBallSpeed;
    }

    function incrementBallSpeed(){
        state.ball.speed += config.ballSpeedIncrement;
    }

    function calculateImpactPosition(ballY, paddleY, paddleHeight) {
        const relativeY = (paddleY + paddleHeight / 2) - ballY;
        return relativeY / (paddleHeight / 2);
    }

    function calculateNewBallDirection(paddleY, paddleSpeed=0) {
        const impactPosition = calculateImpactPosition(state.ball.y + config.ballSize/2, paddleY, config.paddleHeight);
        const bounceAngle = impactPosition * config.maxBounceAngle;
    
        //ADD SPEED INFLUENCE HERE

        const speed = state.ball.speed;
        console.log('speed', speed);
        const xNewSpeed = speed * Math.cos(bounceAngle);
        const yNewSpeed = speed * -Math.sin(bounceAngle);
        state.ball.speedX = state.ball.speedX < 0 ? xNewSpeed * -1 : xNewSpeed;
        state.ball.speedY = yNewSpeed;
    }

    function handlePaddleBounce(paddle){
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
            if (state.ball.speed < config.maxBallSpeed)
                incrementBallSpeed();
            calculateNewBallDirection(paddle.y);
        }
    }

    function handlePaddleCollision(paddle){
        if (((state.ball.x < paddle.x + config.paddleWidth &&
            state.ball.x > paddle.x ) ||
            (state.ball.x + config.ballSize > paddle.x && 
            state.ball.x + config.ballSize < paddle.x + config.paddleWidth))&&
			state.ball.y + config.ballSize > paddle.y &&
			state.ball.y < paddle.y + config.paddleHeight){
            handlePaddleBounce(paddle);
            if (!paddle.blockGlide){
                if (state.ball.x + config.ballSize > paddle.x &&
                    state.ball.x + config.ballSize < paddle.x + config.paddleWidth
                ){
                    console.log('derriere');
                    state.ball.x = paddle.x - config.ballSize;
                }
                else{
                    console.log('devant')
                    state.ball.x = paddle.x + config.paddleWidth;
                }
            }
        }
        else if (state.ball.x < paddle.x + config.paddleWidth &&
                 state.ball.x + config.ballSize > paddle.x
        )
            paddle.blockGlide = true;
        else
            paddle.blockGlide = false;
    }

    function displayDemo() {
        if (state.ball.x < config.canvasWidth/2){
            let newPaddleLeftY = (state.ball.y + config.ballSize / 2) - config.paddleHeight / 2;
            if (newPaddleLeftY > state.paddles.left.y && newPaddleLeftY - state.paddles.left.y < 5)
                return;
            if (newPaddleLeftY < state.paddles.left.y && state.paddles.left.y - newPaddleLeftY < 5)
                return;
            let yIncr = (newPaddleLeftY > state.paddles.left.y) ? 10 : -10;
            state.paddles.left.y += yIncr;
            if (state.paddles.left.y < 0) state.paddles.left.y = 0;
            if (state.paddles.left.y > config.canvasHeight - config.paddleHeight) state.paddles.left.y = config.canvasHeight - config.paddleHeight;
        }
        else{
            let newPaddleRight = (state.ball.y + config.ballSize / 2) - config.paddleHeight / 2;
            if (newPaddleRight > state.paddles.right.y && newPaddleRight - state.paddles.right.y < 5)
                return;
            if (newPaddleRight < state.paddles.right.y && state.paddles.right.y - newPaddleRight < 5)
                return;
            let yIncr = (newPaddleRight > state.paddles.right.y) ? 10 : -10;
            state.paddles.right.y += yIncr;
            if (state.paddles.right.y < 0) state.paddles.right.y = 0;
            if (state.paddles.right.y > config.canvasHeight - config.paddleHeight) state.paddles.right.y = config.canvasHeight - config.paddleHeight;            
        }
    }

    function handleGameOver(){
        if (state.playerScore >= config.winningScore || state.enemyScore >= config.winningScore){
            if (config.displayDemo){
                resumeGame();
                state.ball.speed = config.defaultBallSpeed;
                stopGame(true);
                setTimeout(()=>{
                    resetGame();
                    startGame();
                }, config.animationDuration + 100);
                return;
            }
            stopGame(true);
        }
    }

    function updateGameState() {
        handleUserInput();
        if (state.isGamePaused)
            return;
		
        if (!state.isCountDownActive){
            state.ball.x += state.ball.speedX;
            state.ball.y += state.ball.speedY;
        }

        if (state.ball.y < 0 || state.ball.y + config.ballSize >= config.canvasHeight){
            if (state.ball.y < 0)
                state.ball.y = 0;
            else
                state.ball.y = config.canvasHeight - config.ballSize;
            state.ball.speedY = -state.ball.speedY;
        }

        handleGoal();
        for (let paddle in state.paddles){
            handlePaddleCollision(state.paddles[paddle]);
        }

        if (config.displayDemo)
            displayDemo();

		handleGameOver();
    }

    function drawPaddles(){
        for (let paddle in state.paddles){
            paddle = state.paddles[paddle];
            ctx.drawImage(paddleImage, paddle.x, paddle.y, config.paddleWidth, config.paddleHeight);
        }
    }

    function drawGame() {

        ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
        if (state.isCountDownActive)
            drawCountdown();
        drawPaddles();
        // ctx.drawImage(paddleImage, state.paddles.left.x, state.paddles.left.y, config.paddleWidth, config.paddleHeight);
        
        // ctx.drawImage(
        //     paddleImage,
        //     state.paddles.right.x,
        //     state.paddles.right.y,
        //     config.paddleWidth,
        //     config.paddleHeight
        // );
        
        if (!state.isCountDownActive) {
            ctx.fillText(`${state.playerScore}`, config.playerScore.x, config.playerScore.y);
            ctx.fillText(`${state.enemyScore}`, config.enemyScore.x, config.enemyScore.y);
            ctx.drawImage(ballImage, state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        }
    }
    
    window.PongGame = {startGame, stopGame, pauseGame, resumeGame};
})();


function initSocket(){
    let socket = io("wss://localhost:4443/", {
        path: "/ws/",
        auth : {
            
            "id": userInformations.id,
            "token": 'kk',
        },
		// extraHeaders: {
		// }
	});
    window.socket = socket;
    console.log(socket)
	socket.on('connect', () => {
        console.log('Connecté au serveur Socket.IO !');
      
        // Envoie un message au serveur
        socket.emit('join_room');
    });
    socket.on('connect_error', (error)=> {
        console.log('error', error);
    })

    socket.on('move_up', event=> {
        console.log(event);
    })
}

document.getElementById('zizi').addEventListener('click', event => {
    event.preventDefault();
    initSocket();
})

document.getElementById('playGame').addEventListener('click', async event => {
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/duel/`, 'POST');
	}
	catch(error) {
		console.log(error);
	}
	// initSocket();
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