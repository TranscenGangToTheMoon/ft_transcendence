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

    function startGame() {
        console.log('game start');
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

    function stopGame(animate=false, reason=undefined) {
        console.log('game stop');
        state.isGameActive = false;
        // ctx.fillText('Game over', config.canvasWidth / 2, config.canvasHeight / 2);
        // if (reason)
        //     ctx.fillText(reason, config.canvasWidth / 2, config.canvasHeight / 2 + 96);
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
        // ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
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
                if (typeof gameSocket !== 'undefined'){
                    // console.log('emitting stop_moving');
                    gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
                }
                state.paddles.right.speed = 0;
            }
        }
        else if (state.keys["ArrowUp"] && state.paddles.right.speed != -1){
            if (typeof gameSocket !== 'undefined'){
                if (state.paddles.right.speed === 1){
                		gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
                  	// console.log('emitting stop_moving');
                }
                gameSocket.emit('move_up');
                // console.log('emitting move_up')
            }
            state.paddles.right.speed = -1;
        }
        else if (state.keys["ArrowDown"] && state.paddles.right.speed != 1){
            if (typeof gameSocket !== 'undefined'){
                if (state.paddles.right.speed === -1){
                    gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
                    // console.log('emitting move_stop');
                }
                gameSocket.emit('move_down');
                // console.log('emitting move_down')
            }
            state.paddles.right.speed = 1;
        }
        else if (!state.keys["ArrowDown"] && !state.keys['ArrowUp'] && state.paddles.right.speed != 0){
            state.paddles.right.speed = 0;
            if (typeof gameSocket !== 'undefined'){
                gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
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
        // ctx.clearRect(state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        stopGame(true, reason);
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
		}
		if (state.ball.y + config.ballSize > config.canvasHeight) {
			state.ball.y -= (state.ball.y + config.ballSize) - config.canvasHeight;
			state.ball.speedY = -state.ball.speedY;
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
            ctx.fillText(`${state.playerScore}`, config.playerScore.x, config.playerScore.y);
            ctx.fillText(`${state.enemyScore}`, config.enemyScore.x, config.enemyScore.y);
            ctx.drawImage(ballImage, state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        }
    }

    window.PongGame = {startGame, startCountdown, drawGame, stopGame, state, config, moveUp, moveDown, handleGameOver, resetGame, info, animatePaddlesToMiddle};
})();

function fillTeamDetail(enemyTeamDetail, playerTeamDetail){
    enemyTeamDetail.title += window.PongGame.info.enemyTeam.name;
    playerTeamDetail.title += window.PongGame.info.myTeam.name;
    for (let player in window.PongGame.info.myTeam.players){
        player = window.PongGame.info.myTeam.players[player];
        const oldContent = playerTeamDetail.getAttribute('data-bs-content');
        playerTeamDetail.setAttribute('data-bs-content', oldContent || '' + `
            <div id=TD-username>${player.username}</div>
        `);
    }
    for (let player in window.PongGame.info.enemyTeam.players){
        player = window.PongGame.info.enemyTeam.players[player];
        const oldContent = enemyTeamDetail.getAttribute('data-bs-content');
        enemyTeamDetail.setAttribute('data-bs-content', oldContent || '' + `
            <div id=TD-username>${player.username}</div>
        `);
    }
}

function initSocket(){
	const host = window.location.origin;
	const token = getAccessToken();
	let gameSocket = io(host, {
      transports: ["websocket"],
      path: "/ws/game/",
      auth : {
          "id": userInformations.id,
          "token": token,
      },
	});
    window.gameSocket = gameSocket;
    // console.log(socket)
	gameSocket.on('connect', () => {
        // console.log('Connected to socketIO server!');
    });
    gameSocket.on('disconnect', () => {
        gameSocket.close();
        console.log('disconnected from gameSocket');
    })
    gameSocket.on('start_game', event => {
        // console.log('received start_game');
        if (!window.PongGame.state.isGameActive)
            window.PongGame.startGame();
    })
    gameSocket.on('start_countdown', event => {
        // console.log('received start_countdown');
        window.PongGame.startCountdown();
    })
    gameSocket.on('game_state', event => {
		console.log('received game State');
		window.PongGame.state.ball.y = event.position_y;
		window.PongGame.state.ball.x = event.position_x;
		window.PongGame.state.ball.speedX = event.speed_x;
		window.PongGame.state.ball.speedY = event.speed_y;
		window.PongGame.state.ball.speed = event.speed;
    })
    gameSocket.on('connect_error', (error)=> {
        console.log('error', error);
    })
    gameSocket.on('move_up', event => {
        console.log('move_up received', event.player);
        if (event.player !== userInformations.id)
            window.PongGame.state.paddles.left.speed = -1;
    })
    gameSocket.on('move_down', event => {
        console.log('move_down received', event.player);
        if (event.player !== userInformations.id)
            window.PongGame.state.paddles.left.speed = 1;
    })
    gameSocket.on('stop_moving', event => {
		console.log('received stop_moving', event.player);
        if (event.player == userInformations.id)
	        window.PongGame.state.paddles.right.y = event.position;
		else {
        	window.PongGame.state.paddles.left.speed = 0;
	        window.PongGame.state.paddles.left.y = event.position;
    	}
    })
    gameSocket.on('score', event => {
        window.PongGame.state.ball.speed = 0;
		// for (paddle in window.PongGame.state.paddles) {
            // 	window.PongGame.state.paddles[paddle].y = (window.PongGame.config.canvasHeight - window.PongGame.config.paddleHeight) / 2;
            // }
            // window.PongGame.animatePaddlesToMiddle()
            if (window.PongGame.info.myTeam.name == 'A') {
                window.PongGame.state.playerScore = event.team_a;
                window.PongGame.state.enemyScore = event.team_b;
            }
            else {
                window.PongGame.state.playerScore = event.team_b;
                window.PongGame.state.enemyScore = event.team_a;
            }
            window.PongGame.drawGame();
        })
    gameSocket.on('game_over', async event => {
        console.log('game_over received', event);
        gameSocket.close();
		window.PongGame.handleGameOver(event.reason);
        if (typeof fromTournament !== 'undefined' && fromTournament)
            await navigateTo('/tournament');
        else if (typeof fromLobby !== 'undefined' && fromLobby)
            await navigateTo('/lobby', true, true);
        else {
            document.getElementById('enemyScore').innerText = window.PongGame.state.enemyScore;
            const enemyTeamDetail = document.getElementById('enemyScoreLabel').querySelector('.teamDetail');
            enemyTeamDetail.innerText = enemyTeamDetail.innerText.replace('{team-id}', window.PongGame.info.enemyTeam.name);
            const playerTeamDetail = document.getElementById('playerScoreLabel').querySelector('.teamDetail');
            playerTeamDetail.innerText = playerTeamDetail.innerText.replace('{team-id}', window.PongGame.info.myTeam.name);
            document.getElementById('playerScore').innerText = window.PongGame.state.playerScore;
            const gameOverModal = new bootstrap.Modal(document.getElementById('gameOverModal'));
            gameOverModal.show();
            document.getElementById('gameOverModal').addEventListener('hidden.bs.modal', async () => {
                await handleRoute();
            });
            fillTeamDetail(enemyTeamDetail, playerTeamDetail);
            console.log(enemyTeamDetail);
            const popovers = document.querySelectorAll('.teamDetail');
            popovers.forEach(element => {
                new bootstrap.Popover(element, {
                html: true
                });
            });
        }
    })
}

document.getElementById('gameOverModalPlayAgain').addEventListener('click', async () => {
    // await handleRoute();
})

document.getElementById('gameOverModalQuit').addEventListener('click', async () => {
    await navigateTo('/');
})

function initData(data){
    try {
        console.log(data);
		if (data.teams.a.players.some(player => player.id == userInformations.id)) {
			window.PongGame.info.myTeam.name = 'A';
			window.PongGame.info.myTeam.players = data.teams.a;
			window.PongGame.info.enemyTeam.name = 'B';
			window.PongGame.info.enemyTeam.players = data.teams.b;
		}
		else if (data.teams.b.players.some(player => player.id == userInformations.id)) {
			window.PongGame.info.myTeam.name = 'B';
			window.PongGame.info.myTeam.players = data.teams.b;
			window.PongGame.info.enemyTeam.name = 'A';
			window.PongGame.info.enemyTeam.players = data.teams.a;
		}
	}
	catch(error) {
		console.log(error);
		console.log('Invalid game data from SSE, cannot launch game');
		return;
	}
    document.getElementById('gameArea').classList.replace('d-none', 'd-flex');
    document.getElementById('opponentWait').style.display = "none";
	initSocket();
}

document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
    window.PongGame.resumeGame();
})

function checkGameAuthorization(){
    console.log(window.location.pathname);
    if (userInformations.is_guest && window.location.pathname === '/game/ranked')
        throw `${window.location.pathname}`;
    if (window.location.pathname === '/game/tournament' && typeof tournamentData === 'undefined')
        throw `${window.location.pathname}`;
    if (window.location.pathname === '/game/1v1' && (typeof fromLobby === 'undefined' || !fromLobby))
        throw `${window.location.pathname}`;
}

function gameStart(event){
    data = JSON.parse(event.data);
    data = data.data;
    console.log('game-start received (game)');
    initData(data);
}

async function initGame(){
    await indexInit(false);
    if (window.location.pathname === '/') return;
    document.getElementById('gameArea').classList.replace('d-flex', 'd-none');
    document.getElementById('opponentWait').style.display = "block";
    try {
        checkGameAuthorization();
        if (window.location.pathname === '/game/tournament')
            initData(tournamentData);
        else if (window.location.pathname === '/game/1v1')
            initData(userInformations.lobbyData);
        else {
            if (SSEListeners.has('game-start')){
                sse.removeEventListener('game-start', SSEListeners.get('game-start'));
                SSEListeners.delete('game-start');
            }
            SSEListeners.set('game-start', gameStart);
            sse.addEventListener('game-start', gameStart);
            try {
                let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/${window.location.pathname.split('/')[2]}/`, 'POST');
                console.log(data);
                if (data.detail)
                    document.getElementById('opponentWait').innerText = data.detail;
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
