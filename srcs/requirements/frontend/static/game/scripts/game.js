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
        defaultBallSpeed : 4,
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
                speed:0
            },
            right: {
                x: config.canvasWidth - config.paddleWidth - 100,
                y: (config.canvasHeight - config.paddleHeight) / 2,
                blockGlide: false,
                speed : 0
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

    function moveUp(paddle){
        if (!paddle.blockGlide || paddle.y - 10 > config.ballSize)
            paddle.y -= 10;
        else if (paddle.y - 10 <= config.ballSize)
            paddle.y = config.ballSize;
    }

    function moveDown(paddle){
        if (!paddle.blockGlide || paddle.y + config.paddleHeight + 10 < config.canvasHeight - config.ballSize)
            paddle.y += 10;
        else if (paddle.y + config.paddleHeight + 10 >= config.canvasHeight - config.ballSize)
            paddle.y = config.canvasHeight - config.ballSize - config.paddleHeight;
    }

    function handlePaddleInput(){
        if (state.keys['ArrowUp'] && state.keys['ArrowDown']){
            if (state.paddles.right.speed != 0){
                if (typeof socket !== 'undefined'){
                    console.log('emitting stop_moving');
                    socket.emit('stop_moving', {'position': state.paddles.right.y});
                }
                state.paddles.right.speed = 0;
            }
            return;
        }
        if (state.keys["ArrowUp"] && state.paddles.right.speed != -1){
            if (typeof socket !== 'undefined'){
                if (state.paddles.right.speed === 1){
                		socket.emit('stop_moving', {'position': state.paddles.right.y});
                  	console.log('emitting stop_moving');
                }
                socket.emit('move_up');
                console.log('emitting move_up')
            }
            state.paddles.right.speed = -1;
        }
        if (state.keys["ArrowDown"] && state.paddles.right.speed != 1){
            if (typeof window.socket !== 'undefined'){
                if (state.paddles.right.speed === -1){
                    socket.emit('stop_moving');console.log('emitting move_stop');
                }
                socket.emit('move_down'); console.log('emitting move_down')
            }
            state.paddles.right.speed = 1;
        }
        if (!state.keys["ArrowDown"] && !state.keys['ArrowUp'] && state.paddles.right.speed != 0){
            state.paddles.right.speed = 0;
            if (typeof socket !== 'undefined'){
                socket.emit('stop_moving', {'position': state.paddles.right.y}); console.log('emitting stop_moving');
            }
        }

        for (let paddle in state.paddles){
            paddle = state.paddles[paddle];
            if (paddle.speed === 1 && paddle.y + config.paddleHeight < config.canvasHeight)
                  moveDown(paddle);
            else if (paddle.speed === -1 && paddle.y > 0)
                moveUp(paddle);
        }
    }

    function handleUserInput(){
        if (state.keys['d']) config.displayDemo ? config.displayDemo = false : config.displayDemo = true;
        if (state.keys[' '])
            pauseGame(false);
        if (state.isGamePaused) return;
        // console.log(state.paddles.right.speed);
        handlePaddleInput();
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
			if (state.ball.x + config.ballSize <= 0){
                state.playerScore++;
            }
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
        if (typeof socket !=='undefined'){
            state.ball.speed = 0;
            state.ball.speedX = 0;
            state.ball.speedY = 0;
        }
    }

    function incrementBallSpeed(){
        state.ball.speed += config.ballSpeedIncrement;
        if (state.ball.speed > config.maxBallSpeed)
            state.ball.speed = config.maxBallSpeed;
    }

    function calculateImpactPosition(ballY, paddleY, paddleHeight) {
        const relativeY = (paddleY + paddleHeight / 2) - ballY;
        return relativeY / (paddleHeight / 2);
    }

    function calculateNewBallDirection(paddleY, paddleSpeed=0) {
        const impactPosition = calculateImpactPosition(state.ball.y + config.ballSize/2, paddleY, config.paddleHeight);
        console.log(impactPosition);
        const bounceAngle = impactPosition * config.maxBounceAngle;

        const speed = state.ball.speed;
        console.log(bounceAngle);
        const xNewSpeed = speed * Math.cos(bounceAngle);
        const yNewSpeed = speed * -Math.sin(bounceAngle);
        console.log(xNewSpeed, yNewSpeed);
        state.ball.speedX = state.ball.speedX < 0 ? xNewSpeed * -1 : xNewSpeed;
        state.ball.speedY = yNewSpeed;
        console.log(state.ball.speedX, state.ball.speedY);
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
            incrementBallSpeed();
            calculateNewBallDirection(paddle.y);
        }
        if (paddle == state.paddles.right) {
            if (typeof socket !== 'undefined')
                window.socket.emit('bounce', {'dir_x': state.ball.speedX, 'dir_y': state.ball.speedY})
        }
    }

    function handlePaddleCollision(paddle){
        var ball_is_right_from_racket = state.ball.x < paddle.x + config.paddleWidth && state.ball.x > paddle.x;
        var ball_is_left_from_racket = state.ball.x + config.ballSize > paddle.x && state.ball.x + config.ballSize < paddle.x + config.paddleWidth;
        var is_ball_y_in_paddle_range = state.ball.y + config.ballSize > paddle.y && state.ball.y < paddle.y + config.paddleHeight;

        if ((ball_is_left_from_racket || ball_is_right_from_racket) && is_ball_y_in_paddle_range){
            handlePaddleBounce(paddle);
            if (!paddle.blockGlide){
                if (state.ball.x + config.ballSize > paddle.x &&
                    state.ball.x + config.ballSize < paddle.x + config.paddleWidth
                ){
                    state.ball.x = paddle.x - config.ballSize;
                }
                else{
                    state.ball.x = paddle.x + config.paddleWidth;
                }
            }
        }
        else {
            let is_ball_x_in_paddle_range = state.ball.x < paddle.x + config.paddleWidth && state.ball.x + config.ballSize > paddle.x
            if (is_ball_x_in_paddle_range)
                paddle.blockGlide = true;
            else
                paddle.blockGlide = false;
        }
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

        if (!state.isCountDownActive) {
            ctx.fillText(`${state.playerScore}`, config.playerScore.x, config.playerScore.y);
            ctx.fillText(`${state.enemyScore}`, config.enemyScore.x, config.enemyScore.y);
            ctx.drawImage(ballImage, state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        }
    }

    window.PongGame = {startGame, stopGame, pauseGame, resumeGame, state, config, moveUp, moveDown};
})();


function initSocket(){
	const host = window.location.origin;
  let socket = io(host, {
      transports: ["websocket"],
      path: "/ws/game/",
      auth : {
          "id": userInformations.id,
          "token": 'kk',
      },
	});
    window.socket = socket;
    console.log(socket)
	socket.on('connect', () => {
        console.log('Connected to socketIO server!');
    });
    socket.on('start_game', event => {
        console.log('received start_game');
        window.PongGame.startGame();
    })
    socket.on('game_state', event => {
	   	console.log(event);
	    window.PongGame.state.ball.y = event.position_y;
	    window.PongGame.state.ball.x = event.position_x;
		window.PongGame.state.ball.speed = event.speed / 2;
	    window.PongGame.state.ball.speedX = event.direction_x;
	    window.PongGame.state.ball.speedY = event.direction_y;
	    console.log(window.PongGame.state.ball.speedX);
	    console.log(window.PongGame.state.ball.speedY);
    })
    socket.on('connect_error', (error)=> {
        console.log('error', error);
    })
    socket.on('move_up', event => {
        console.log('move_up received');
        window.PongGame.state.paddles.left.speed = -1;
    })
    socket.on('move_down', event => {
        console.log('move_down received');
        window.PongGame.state.paddles.left.speed = 1;
    })
    socket.on('stop_moving', event => {
        console.log(event);
        console.log('received stop_moving')
        window.PongGame.state.paddles.left.speed = 0;
        window.PongGame.state.paddles.left.y = event.position;
    })
    socket.on('you_scored', event => {
        console.log('received goal');
        window.PongGame.state.playerScore = event.score
    })
    socket.on('enemy_scored', event => {
        console.log('received goal');
        window.PongGame.state.enemyScore = event.score
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

function checkGameAuthorization(){
    console.log(window.location.pathname);
    if (userInformations.is_guest && window.location.pathname === '/game/ranked')
        throw `${window.location.pathname}`
}

async function initGame(){
    await indexInit(false);
    if (window.location.pathname === '/') return;
    try {
        checkGameAuthorization();
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/duel/`, 'POST');
            console.log(data);
        }
        catch(error) {
            console.log(error);
        }
        // window.PongGame.startGame();
    }
    catch (unauthorized){
        if (!document.getElementById('alertModal').classList.contains('show'))
            displayMainAlert("Error", `You don't have permission to play in ${unauthorized}`);
        await navigateTo('/');
    }
}

initGame();
