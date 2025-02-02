(function PongGame() {

    const config = {
        canvasWidth: 1400,
        canvasHeight: 700,
        paddleWidth: 30,
        paddleHeight: 200,
        ballSize: 20,
        maxBallSpeed: 20,
        animationDuration: 800,
        font: "48px Arial",
        fontColor: "white",
        defaultBallSpeed : 6,
        ballSpeedIncrement: 1,
        winningScore: 3,
        enemyScore : {},
        playerScore : {},
        countDown : {
            steps : 3,
            delay : 2000,
        },
        maxBounceAngle : 2 * (Math.PI / 5),
        displayDemo: {
            right : true,
            left : true,
        }
    };

    function setScoreCoords(){
        config.enemyScore = {
            y : config.canvasHeight / 2,
            x : config.canvasWidth / 4
        }
    
        config.playerScore = {
            y : config.enemyScore.y,
            x : config.canvasWidth - config.enemyScore.x
        } 
    }
    setScoreCoords();

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
    const rightPaddleImage = new Image();
    rightPaddleImage.src = "/assets/paddle_right.png";
    const leftPaddleImage = new Image();
    leftPaddleImage.src = "/assets/paddle_left.png";
    const ballImage = new Image();
    ballImage.src = "/assets/ball.png";

    function setFont(){
        ctx.font = config.font;
        ctx.fillStyle = config.fontColor;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
    }
    setFont();
    state.keys[' '] = false;

    document.addEventListener("keydown", (e) => {
        if (e.key === ' ' && state.keys[e.key] !== undefined && state.isGamePaused)
            return;
        else
            state.keys[e.key] = true;
    });
    document.addEventListener("keyup", (e) => (state.keys[e.key] = undefined));
    
    function startGame() {
        state.isGameActive = true;
        state.cancelAnimation = false;
        
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
        if (fromPause)
            state.keys[' '] = false;
        state.isGamePaused = false;
    }
    
    function stopGame(animate=false) {
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
            leftPaddleImage, state.paddles.left.x, state.paddles.left.y,
            config.paddleWidth, config.paddleHeight
        );

        ctx.drawImage(
            rightPaddleImage,
            state.paddles.right.x,
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
        if (!config.displayDemo.right) {
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
        }
        if (!config.displayDemo.left){
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
    }

    function handleGoal(){
        if (state.ball.x + config.ballSize <= 0 || state.ball.x >= canvas.width){
			if (state.ball.x + config.ballSize <= 0) state.playerScore++;
			else state.enemyScore++;
            state.ball.x = config.canvasWidth / 2 - config.ballSize / 2;
            state.ball.y = config.canvasHeight / 2 - config.ballSize / 2;
            state.ball.speed = config.defaultBallSpeed;
            const randomAngle = Math.random() * config.maxBounceAngle;
            state.ball.speedX = state.ball.speed * Math.cos(randomAngle);
            state.ball.speedY = state.ball.speed * -Math.sin(randomAngle);
            animatePaddlesToMiddle();
            startCountdown();
        }
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

        const speed = state.ball.speed;
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
                )
                    state.ball.x = paddle.x - config.ballSize;
                else
                    state.ball.x = paddle.x + config.paddleWidth;
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
        if (state.isCountDownActive) return;
        if (state.ball.x < config.canvasWidth/2 && config.displayDemo.left){
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
        else if (config.displayDemo.right){
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
            if (config.displayDemo.left && config.displayDemo.right){
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
            config.displayDemo.left = true;
            config.displayDemo.right = true;
            startGame();
            const gameModeModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('gameModeModal'));
            gameModeModal.show();
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

        displayDemo();

		handleGameOver();
    }

    function drawPaddles(){
        for (let paddle in state.paddles){
            paddle = state.paddles[paddle];
            if (paddle === state.paddles.left)
				ctx.drawImage(leftPaddleImage, paddle.x, paddle.y, config.paddleWidth, config.paddleHeight);
			else
	            ctx.drawImage(rightPaddleImage, paddle.x, paddle.y, config.paddleWidth, config.paddleHeight);
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
    
    window.PongGame = {startGame, stopGame, pauseGame, resumeGame, config, resetGame, state, setScoreCoords, setFont};
})();

document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
    window.PongGame.resumeGame();
})

async function initGameConstants(){
    await fetch('/gameConfig.json')
        .then(response => response.json())
        .then(data => {
            PongGame.config.canvasHeight = data.canvas.local.height;
            PongGame.config.canvasWidth = data.canvas.local.width;
            let canvas = document.getElementById('gameCanvas');
            PongGame.ctx = canvas.getContext("2d");
            canvas.width = PongGame.config.canvasWidth;
            canvas.height = PongGame.config.canvasHeight;
            PongGame.setFont();
            PongGame.config.paddleHeight = data.paddle.local.height;
            PongGame.config.paddleWidth = data.paddle.local.width;
            PongGame.config.maxBounceAngle = data.ball.maxBounceAngle;
            PongGame.config.winningScore = data.score.max;
            PongGame.setScoreCoords();
        })
}

function setGameMode(){
	const options = document.querySelectorAll('.option');
	selectedValue = 'friend';

	options.forEach(option => {
  		if (option.dataset.value == selectedValue) {
    		option.classList.add('selected');
  		}
  
  		option.addEventListener('click', async () => {
            options.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            selectedValue = option.dataset.value;
	    });
    });

    function startLocalGame() {
        const playWithFriend = selectedValue === 'friend';
        window.PongGame.config.displayDemo.right = false;
        if (playWithFriend) {
            window.PongGame.config.displayDemo.left = false;
        }
        window.PongGame.stopGame(true);
        window.PongGame.resetGame();
        setTimeout(()=>{
            window.PongGame.startGame();
        }, 500);
    }

    document.getElementById('gameModeModal').addEventListener('hidden.bs.modal', startLocalGame);
    document.getElementById('quitLocalGame').addEventListener('click', async () => {
        await navigateTo('/');
        setTimeout(()=>{
            window.PongGame.stopGame();
        }, 800);
    })
}

function forPhoneChanges(){
    try {
        
        function simulateKey(type, keyCode) {
            const event = new KeyboardEvent(type, {
                key: keyCode === 38 ? 'ArrowUp' : 'ArrowDown',
                keyCode: keyCode,
                code: keyCode === 38 ? 'ArrowUp' : 'ArrowDown',
                which: keyCode,
                bubbles: true,
                cancelable: true
            });
            
            document.dispatchEvent(event);
        }
        
    // Handle touch start
    let lastTouchY = undefined;
    function handleTouchStart(event) {
        const touch = event.touches[0];
        const screenHeight = window.innerHeight;
        const touchY = touch.clientY;
        const threshold = 0.20; // 20% of screen height
        
        if (touchY < screenHeight / 2) {
            if (lastTouchY && lastTouchY >= screenHeight / 2)
                simulateKey('keyup', 40)
            // Top touch - simulate arrow up press
            simulateKey('keydown', 38);
        } else {
            if (lastTouchY && lastTouchY < screenHeight / 2)
                simulateKey('keyup', 38)
            // Bottom touch - simulate arrow down press
            simulateKey('keydown', 40);
        }
        lastTouchY = touchY;
    }
    
    // Handle touch end - simulates keyup
    function handleTouchEnd(event) {
        // When the last touch point is removed, we need to check
        // what was the last position to know which key to release
        if (event.changedTouches.length > 0) {
            const touch = event.changedTouches[0];
            const screenHeight = window.innerHeight;
            const touchY = touch.clientY;
            const threshold = 0.20;
            
            if (touchY < screenHeight / 2) {
                // Release arrow up
                simulateKey('keyup', 38);
            } else {
                // Release arrow down
                simulateKey('keyup', 40);
            }
        }
    }
    
        document.addEventListener('touchstart', handleTouchStart);
        document.addEventListener('touchmove', handleTouchStart);
        document.addEventListener('touchend', handleTouchEnd);
        document.addEventListener('touchmove', event => {event.preventDefault()}, { passive: false });
    }
    catch (error){
        document.getElementById('salut').innerText = error;
    }
}

async function initGame(){
    await indexInit(false);
    try {
        initGameConstants();
    }
    catch (error){
        return displayMainAlert('Error', 'Erroneous game config file.\n');
    }
    if (window.matchMedia("(hover: none) and (pointer: coarse)").matches)
        forPhoneChanges();
    window.PongGame.startGame();
    setGameMode();
    const gameModeModal = new bootstrap.Modal(document.getElementById('gameModeModal'));
    gameModeModal.show();
}

initGame();