(function PongGame() {

    const config = {
        canvasWidth: 800,
        canvasHeight: 600,
        paddleWidth: 30,
        paddleHeight: 200,
        ballSize: 20,
        maxBallSpeed: 1500,
        maxPaddleSpeed: 500,
        animationDuration: 800,
        font: "48px Arial",
        fontColor: "white",
        defaultBallSpeed : 240,
        ballSpeedIncrement: 30,
        winningScore: 3,
        enemyScore : {},
        playerScore : {},
        countDown : {
            steps : 3,
            delay : 2000,
        },
        maxBounceAngle : 2 * (Math.PI / 5),
        displayDemo: false,
        team: '',
    };

    config.enemyScore = {
        y : config.canvasHeight / 2,
        x : config.canvasWidth / 4
    }

    config.playerScore = {
        y : config.enemyScore.y,
        x : config.enemyScore.x * 3
    }

    const info = {
		myTeam: {
			name: '',
			players: [],
		},
		enemyTeam: {
			name: '',
			players: [],
		},
    }


    const state = {
        isGameActive: false,
        isCountDownActive: false,
        isGamePaused: false,
        lastFrame: 0,
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
        deltaTime: 0,
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
        // console.log('game started');
		state.isCountDownActive = false;
		state.lastFrame = 0;
		// state.ball.speedX = config.defaultBallSpeed;
		// state.ball.speedY = config.defaultBallSpeed;
		state.ball.speed = config.defaultBallSpeed;

        function gameLoop(timestamp) {
            if (state.isGameActive) {
	            updateGameState(timestamp);
	            drawGame();
				requestAnimationFrame(gameLoop);
            }
        }
        requestAnimationFrame(gameLoop);
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

    function stopGame(animate=false) {
        state.isGameActive = false;
        ctx.fillText('Game over', config.canvasWidth / 2, config.canvasHeight / 2);
        if (animate){
            animatePaddlesToMiddle();
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
	    state.isGameActive = false;
	    state.cancelAnimation = false;
        state.isCountDownActive = true;

        // for (racket in state.paddles) {
        // 	racket.y = (config.canvasHeight + config.paddleHeight) / 2
        // }
        ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
        animatePaddlesToMiddle();
        function step() {
            state.countDown.currentStep--;
            if (state.isGameActive){
                state.countDown.currentStep = config.countDown.steps;
                ctx.clearRect(config.canvasWidth / 2 - 50 , 0, 100, config.canvasHeight);
                return;
            }
            if (state.countDown.currentStep >= 0) {
	            ctx.clearRect(config.canvasWidth / 2 - 50 , 0, 100, config.canvasHeight);
                drawCountdown();
                setTimeout(step, config.countDown.delay / (config.countDown.steps + 1));
            }
            else{
                state.countDown.currentStep = config.countDown.steps;
            }
        }

        step();
    }

    function animatePaddlesToMiddle(){
        // state.isCountDownActive = true;
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
        
        for (paddle in state.paddles){
            paddle = state.paddles[paddle];
            ctx.clearRect(paddle.x, 0, config.paddleWidth, config.canvasHeight);
        }

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
            
    }

    function moveUp(paddle){
    	delta = state.deltaTime * config.maxPaddleSpeed
        if (!paddle.blockGlide || paddle.y - delta > config.ballSize)
            paddle.y -= delta;
        else if (paddle.y - delta <= config.ballSize)
            paddle.y = config.ballSize;
    }

    function moveDown(paddle){
    	delta = state.deltaTime * config.maxPaddleSpeed
        if (!paddle.blockGlide || paddle.y + config.paddleHeight + delta < config.canvasHeight - config.ballSize)
            paddle.y += delta;
        else if (paddle.y + config.paddleHeight + delta >= config.canvasHeight - config.ballSize)
            paddle.y = config.canvasHeight - config.ballSize - config.paddleHeight;
    }

    function handlePaddleInput(){
        if (state.keys['ArrowUp'] && state.keys['ArrowDown']){
            if (state.paddles.right.speed != 0){
                if (typeof socket !== 'undefined'){
                    // console.log('emitting stop_moving');
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
                  	// console.log('emitting stop_moving');
                }
                socket.emit('move_up');
                // console.log('emitting move_up')
            }
            state.paddles.right.speed = -1;
        }
        if (state.keys["ArrowDown"] && state.paddles.right.speed != 1){
            if (typeof window.socket !== 'undefined'){
                if (state.paddles.right.speed === -1){
                    socket.emit('stop_moving', {'position': state.paddles.right.y});
                    // console.log('emitting move_stop');
                }
                socket.emit('move_down');
                // console.log('emitting move_down')
            }
            state.paddles.right.speed = 1;
        }
        if (!state.keys["ArrowDown"] && !state.keys['ArrowUp'] && state.paddles.right.speed != 0){
            state.paddles.right.speed = 0;
            if (typeof socket !== 'undefined'){
                socket.emit('stop_moving', {'position': state.paddles.right.y});
                // console.log('emitting stop_moving');
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
        // console.log(impactPosition);
        const bounceAngle = impactPosition * config.maxBounceAngle;

        const speed = state.ball.speed;
        // console.log(bounceAngle);
        const xNewSpeed = speed * Math.cos(bounceAngle);
        const yNewSpeed = speed * -Math.sin(bounceAngle);
        // console.log(xNewSpeed, yNewSpeed);
        state.ball.speedX = state.ball.speedX < 0 ? xNewSpeed * -1 : xNewSpeed;
        state.ball.speedY = yNewSpeed;
        // console.log(state.ball.speedX, state.ball.speedY);
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

    function handleGameOver(reason){
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
            // animatePaddlesToMiddle(true);
            stopGame(true);
        }
    }

    function updateGameState(timestamp) {
    	if (state.lastFrame == 0)
    		state.lastFrame = timestamp;
    	state.deltaTime = (timestamp - state.lastFrame) / 1000;  // Convert to seconds
    	state.lastFrame = timestamp;

     	// setTimeout(() => {
      		handlePaddleInput();
     	// }, 0)

        if (!state.isCountDownActive){
            state.ball.x += state.ball.speedX * state.deltaTime;
            state.ball.y += state.ball.speedY * state.deltaTime;
        }

		if (state.ball.y < 0) {
			state.ball.y = -state.ball.y;
			state.ball.speedY = -state.ball.speedY;
			console.log('bouncing up', Date.now());
		}
		if (state.ball.y + config.ballSize > config.canvasHeight) {
			state.ball.y -= (state.ball.y + config.ballSize) - config.canvasHeight;
			state.ball.speedY = -state.ball.speedY;
			console.log('bouncing down', Date.now());
		}

        for (let paddle in state.paddles){
            handlePaddleCollision(state.paddles[paddle]);
        }
    }

    function drawPaddles(){
        for (let paddle in state.paddles){
            paddle = state.paddles[paddle];
            ctx.drawImage(paddleImage, paddle.x, paddle.y, config.paddleWidth, config.paddleHeight);
        }
    }

    function drawGame() {
        
        if (!state.isCountDownActive) {
            ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
            drawPaddles();
            // ctx.fillText(`${state.playerScore}`, config.playerScore.x, config.playerScore.y);
            // ctx.fillText(`${state.enemyScore}`, config.enemyScore.x, config.enemyScore.y);
            ctx.drawImage(ballImage, state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        }
    }

    window.PongGame = {startGame, startCountdown, stopGame, state, config, moveUp, moveDown, handleGameOver, resetGame, info, animatePaddlesToMiddle};
})();


function initSocket(){
	const host = window.location.origin;
	const token = getAccessToken();
	let socket = io(host, {
      transports: ["websocket"],
      path: "/ws/game/",
      auth : {
          "id": userInformations.id,
          "token": token,
      },
	});
    window.socket = socket;
    // console.log(socket)
	socket.on('connect', () => {
        // console.log('Connected to socketIO server!');
    });
    socket.on('start_game', event => {
        // console.log('received start_game');
        if (!window.PongGame.state.isGameActive)
            window.PongGame.startGame();
    })
    socket.on('start_countdown', event => {
        // console.log('received start_countdown');
        window.PongGame.startCountdown();
    })
    socket.on('game_state', event => {
		// console.log('front : ', window.PongGame.state.ball.speedX);
		// console.log('front : ', window.PongGame.state.ball.speedY);
		// console.log('front : ', window.PongGame.state.ball.speed);
		// console.log('back : ', event.direction_x);
		// console.log('back : ', event.direction_y);
		// console.log('back : ', event.speed);
		window.PongGame.state.ball.y = event.position_y;
		window.PongGame.state.ball.x = event.position_x;
		window.PongGame.state.ball.speedX = event.direction_x;
		window.PongGame.state.ball.speedY = event.direction_y;
		window.PongGame.state.ball.speed = event.speed;
		// console.log(Date.now());
		// console.log('front apres : ', window.PongGame.state.ball.speedX);
		// console.log('front apres : ', window.PongGame.state.ball.speedY);
		// console.log('front apres : ', window.PongGame.state.ball.speed);
    })
    socket.on('connect_error', (error)=> {
        console.log('error', error);
    })
    socket.on('move_up', event => {
        console.log('move_up received', event.player);
		setTimeout(() => {
			window.PongGame.state.paddles.left.speed = -1;
		}, 0);
    })
    socket.on('move_down', event => {
		setTimeout(() => {
			window.PongGame.state.paddles.left.speed = 1;
		}, 0);
        console.log('move_down received', event.player);
    })
    socket.on('stop_moving', event => {
		console.log('received stop_moving', event.player);
        if (event.player == userInformations.id)
	        window.PongGame.state.paddles.right.y = event.position;
		else {
        	window.PongGame.state.paddles.left.speed = 0;
	        window.PongGame.state.paddles.left.y = event.position;
    	}
    })
    socket.on('score', event => {
        window.PongGame.state.ball.speed = 0;
		// for (paddle in window.PongGame.state.paddles) {
		// 	window.PongGame.state.paddles[paddle].y = (window.PongGame.config.canvasHeight - window.PongGame.config.paddleHeight) / 2;
		// }
        // window.PongGame.animatePaddlesToMiddle()
    	if (window.PongGame.info.myTeam.name == 'team_a') {
			window.PongGame.state.playerScore = event.team_a;
			window.PongGame.state.enemyScore = event.team_b;
     	}
     	else {
			window.PongGame.state.playerScore = event.team_b;
			window.PongGame.state.enemyScore = event.team_a;
      	}
    })
    socket.on('game_over', event => {
        console.log('game_over received', event);
		window.PongGame.handleGameOver(event.reason);
        if (fromTournament)
            setTimeout(async ()=> {
                await navigateTo('/tournament')
            }, 500)
    })
}

function initData(data){
    try {
		if (data.teams.a.some(player => player.id == userInformations.id)) {
			window.PongGame.info.myTeam.name = 'team_a';
			window.PongGame.info.myTeam.players = data.teams.team_a;
			window.PongGame.info.enemyTeam.name = 'team_b';
			window.PongGame.info.enemyTeam.players = data.teams.team_b;
		}
		else if (data.teams.b.some(player => player.id == userInformations.id)) {
			window.PongGame.info.myTeam.name = 'team_b';
			window.PongGame.info.myTeam.players = data.teams.team_b;
			window.PongGame.info.enemyTeam.name = 'team_a';
			window.PongGame.info.enemyTeam.players = data.teams.team_a;
		}
	}
	catch(error) {
		console.log(error);
		console.log('Invalid game data from SSE, cannot launch game');
		return;
	}
    document.getElementById('gameArea').style.display = "block";
    document.getElementById('opponentWait').style.display = "none";
	initSocket();
}

sse.addEventListener('game-start', event => {
    data = JSON.parse(event.data);
	data = data.data;
	initData(data);
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

function checkGameAuthorization(){
    console.log(window.location.pathname);
    if (userInformations.is_guest && window.location.pathname === '/game/ranked')
        throw `${window.location.pathname}`;
    if (window.location.pathname === '/game/tournament' && typeof tournamentData === 'undefined')
        throw `${window.location.pathname}`;
}

async function initGame(){
    await indexInit(false);
    if (window.location.pathname === '/') return;
    document.getElementById('gameArea').style.display = "none";
    document.getElementById('opponentWait').style.display = "block";
    try {
        checkGameAuthorization();
        if (window.location.pathname === '/game/tournament')
            initData(tournamentData);
        else {
            try {
                let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/${window.location.pathname.split('/')[2]}/`, 'POST');
                console.log(data);
            }
            catch(error) {
                console.log(error);
            }
        }
    }
    catch (unauthorized){
        if (!document.getElementById('alertModal').classList.contains('show'))
            displayMainAlert("Error", `You don't have permission to play in ${unauthorized}`);
        await navigateTo('/');
    }
}

initGame();
