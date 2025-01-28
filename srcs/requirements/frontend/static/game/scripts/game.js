if (typeof fromLobby === 'undefined')
    var fromLobby;
if (typeof fromTournament === 'undefined')
    var fromTournament;

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
    let ctx = canvas.getContext("2d");
    canvas.width = config.canvasWidth;
    canvas.height = config.canvasHeight;

    function resizeCanvas() {
        const container = document.getElementById('canvas-container');
        if (!container) return;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight - document.querySelector('header').offsetHeight;
  
        const baseWidth = config.canvasWidth;
        const baseHeight = config.canvasHeight + document.getElementById('gameInfo').offsetHeight;
  
        let scale = Math.min(windowWidth / baseWidth, windowHeight / baseHeight);
        
        if (scale > 1)
            scale = 1;
        container.style.transform = `scale(${scale})`;
        container.style.width = `${baseWidth}px`;
        container.style.height = `${baseHeight}px`;
        container.style.marginLeft = `${(windowWidth - baseWidth * scale) / 2}px`;
        container.style.marginTop = `${(windowHeight - baseHeight * scale) / 2}px`;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const rightPaddleImage = new Image();
    rightPaddleImage.src = "/assets/paddle_right.png";
    const leftPaddleImage = new Image();
    leftPaddleImage.src = "/assets/paddle_left.png";
    const ballImage = new Image();
    ballImage.src = "/assets/ball2.png";

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
		state.isCountDownActive = false;
		state.lastFrame = 0;
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
        state.isGameActive = false;
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
                    gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
                }
                state.paddles.right.speed = 0;
            }
        }
        else if (state.keys["ArrowUp"] && state.paddles.right.speed != -1){
            if (typeof gameSocket !== 'undefined'){
                if (state.paddles.right.speed === 1){
                		gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
                }
                gameSocket.emit('move_up');
            }
            state.paddles.right.speed = -1;
        }
        else if (state.keys["ArrowDown"] && state.paddles.right.speed != 1){
            if (typeof gameSocket !== 'undefined'){
                if (state.paddles.right.speed === -1){
                    gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
                }
                gameSocket.emit('move_down');
            }
            state.paddles.right.speed = 1;
        }
        else if (!state.keys["ArrowDown"] && !state.keys['ArrowUp'] && state.paddles.right.speed != 0){
            state.paddles.right.speed = 0;
            if (typeof gameSocket !== 'undefined'){
                gameSocket.emit('stop_moving', {'position': state.paddles.right.y});
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
        const bounceAngle = impactPosition * config.maxBounceAngle;

        const speed = state.ball.speed;
        const xNewSpeed = speed * Math.cos(bounceAngle);
        const yNewSpeed = speed * -Math.sin(bounceAngle);
        state.ball.speedX = state.ball.speedX < 0 ? xNewSpeed * -1 : xNewSpeed;
        state.ball.speedY = yNewSpeed;
    }

    function applyRacketSpeed(paddle){
        const isOnBottom = state.ball.y > paddle.y;
        if ((isOnBottom && state.ball.speedY < 0) || (!isOnBottom && state.ball.speedY > 0))
            state.ball.speedY = -state.ball.speedY;
    }

    function handlePaddleBounce(paddle){
        if (paddle.blockGlide){
            applyRacketSpeed(paddle);
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
            if (paddle.x < config.canvasWidth / 2)
	            ctx.drawImage(leftPaddleImage, paddle.x, paddle.y, config.paddleWidth, config.paddleHeight);
			else
	            ctx.drawImage(rightPaddleImage, paddle.x, paddle.y, config.paddleWidth, config.paddleHeight);
        }
    }

    function drawGame() {
        if (!state.isCountDownActive) {
            ctx.clearRect(0, 0, config.canvasWidth, config.canvasHeight);
            drawPaddles();
            ctx.drawImage(ballImage, state.ball.x, state.ball.y, config.ballSize, config.ballSize);
        }
    }

    window.PongGame = {startGame, startCountdown, drawGame, stopGame, state, config, moveUp, moveDown,
        handleGameOver, resetGame, info, animatePaddlesToMiddle, canvas, ctx, setFont, setScoreCoords,
        resizeCanvas};
})();

function fillTeamDetail(enemyTeamDetail, playerTeamDetail){
    enemyTeamDetail.title += PongGame.info.enemyTeam.name;
    playerTeamDetail.title += PongGame.info.myTeam.name;
    for (let player in PongGame.info.myTeam.players.players){
        player = PongGame.info.myTeam.players.players[player];
        const oldContent = playerTeamDetail.getAttribute('data-bs-content');
        playerTeamDetail.setAttribute('data-bs-content', oldContent || '' + `
            <div id=TD-username>${player.username}</div>
        `);
    }
    for (let player in PongGame.info.enemyTeam.players.players){
        player = PongGame.info.enemyTeam.players.players[player];
        const oldContent = enemyTeamDetail.getAttribute('data-bs-content');
        enemyTeamDetail.setAttribute('data-bs-content', oldContent || '' + `
            <div id=TD-username>${player.username}</div>
        `);
    }
}

async function updateTrophies(){
    if (window.location.pathname !== '/game/ranked') return;
    await fetchUserInfos(true);
    await loadUserProfile();
}

if (typeof cancelTimeout === 'undefined')
    var cancelTimeout;

function initSocket(match_code, socketPath, socketMode){
	const host = window.location.origin;
	const token = getAccessToken();
	let gameSocket = io(host, {
        transports: [socketMode],
        path: socketPath,
        auth : {
            "id": userInformations.id,
            "token": token,
            },
	});
    window.gameSocket = gameSocket;
	gameSocket.on('connect', () => {
        cancelTimeout = true;
        console.log('Connected to socketIO server!');
        document.getElementById('matchCode').innerText = ' ' + match_code;
        window.PongGame.resizeCanvas();
    });
    gameSocket.on('connect_error', (error)=> {
        localStorage.removeItem('game-event');
        handleRoute();
    })
    gameSocket.on('disconnect', async () => {
        gameSocket.close();
        gameSocket = undefined;
        console.log('disconnected from gameSocket');
        if (fromTournament)
            await navigateTo('/tournament', true, true);
        if (typeof fromLobby !== 'undefined' && fromLobby)
            await navigateTo('/lobby', true, true);
    })
    gameSocket.on('start_game', event => {
        if (!PongGame.state.isGameActive)
            PongGame.startGame();
    })
    gameSocket.on('call_spectate', event => {
        console.log('received call_spectate');
        navigateTo('/spectate/' + event.code, true, true);
        setTimeout(() => {
            if (typeof fromTournament !== 'undefined' && fromTournament) {
                localStorage.setItem('tournament-code-reconnect', localStorage.getItem('tournament-code'));
                fromTournament = true;
            }
            else if (typeof fromLobby !== 'undefined' && fromLobby) {
                fromLobby = true;
            }
            if (gameSocket !== undefined) {
                gameSocket.close();
                gameSocket = undefined;
            }
            localStorage.removeItem('game-event');
        }, 500);
    })
    gameSocket.on('start_countdown', event => {
        PongGame.startCountdown();
    })
    gameSocket.on('game_state', event => {
		PongGame.state.ball.y = event.position_y;
		PongGame.state.ball.x = event.position_x;
		PongGame.state.ball.speedX = event.speed_x;
		PongGame.state.ball.speedY = event.speed_y;
		PongGame.state.ball.speed = event.speed;
    })
    gameSocket.on('move_up', event => {
        if (event.player !== userInformations.id)
            PongGame.state.paddles.left.speed = -1;
    })
    gameSocket.on('move_down', event => {
        if (event.player !== userInformations.id)
            PongGame.state.paddles.left.speed = 1;
    })
    gameSocket.on('stop_moving', event => {
        if (event.player == userInformations.id)
	        PongGame.state.paddles.right.y = event.position;
		else {
        	PongGame.state.paddles.left.speed = 0;
	        PongGame.state.paddles.left.y = event.position;
    	}
    })
    gameSocket.on('score', event => {
        PongGame.state.ball.speed = 0;
        if (PongGame.info.myTeam.name == 'A') {
            PongGame.state.playerScore = event.team_a;
            PongGame.state.enemyScore = event.team_b;
        }
        else {
            PongGame.state.playerScore = event.team_b;
            PongGame.state.enemyScore = event.team_a;
        }
        const playerScoreDiv = document.getElementById('playerScore');
        if (playerScoreDiv)
            playerScoreDiv.innerText = '' + PongGame.state.playerScore;
        const enemyScoreDiv = document.getElementById('enemyScore');
        if (enemyScoreDiv)
            enemyScoreDiv.innerText = '' + PongGame.state.enemyScore;
        PongGame.drawGame();
    })
    gameSocket.on('game_over', async event => {
        gameSocket.close();
        gameSocket = undefined;
        localStorage.removeItem('game-event');
        updateTrophies();
		PongGame.handleGameOver(event.reason);
        if (typeof fromTournament !== 'undefined' && fromTournament){
            await navigateTo('/tournament', true, true);
            return;
        }
        else if (typeof fromLobby !== 'undefined' && fromLobby){
            document.getElementById('gameOverModal').querySelector('.modal-footer').classList.add('d-none');
            await navigateTo('/lobby', true, true);
        }
        else{
            document.getElementById('gameOverModal').querySelector('.modal-footer').classList.remove('d-none');
            document.getElementById('gameOverModal').addEventListener('hidden.bs.modal', async () => {
                await handleRoute();
            });
        }
        if (event.reason === 'normal-end'){
            addScore();
        }
        else
            document.getElementById('gameOverContent').innerHTML = `${event.reason}`;
        const gameOverModal = new bootstrap.Modal(document.getElementById('gameOverModal'));
        gameOverModal.show();
        
        const popovers = document.querySelectorAll('.teamDetail');
        popovers.forEach(element => {
            new bootstrap.Popover(element, {
                html: true
            });
        });
    })
}

function addScore(){
    document.getElementById('enemyScoreInModal').innerText = PongGame.state.enemyScore;
    const enemyTeamDetail = document.getElementById('enemyScoreLabel').querySelector('.teamDetail');
    enemyTeamDetail.innerText = enemyTeamDetail.innerText.replace('{team-id}', PongGame.info.enemyTeam.name);
    const playerTeamDetail = document.getElementById('playerScoreLabel').querySelector('.teamDetail');
    playerTeamDetail.innerText = playerTeamDetail.innerText.replace('{team-id}', PongGame.info.myTeam.name);
    document.getElementById('playerScoreInModal').innerText = PongGame.state.playerScore;
    fillTeamDetail(enemyTeamDetail, playerTeamDetail);
}

document.getElementById('gameOverModalQuit').addEventListener('click', async () => {
    await navigateTo('/');
})

async function initGameConstants(){
    await fetch('/gameConfig.json')
        .then(response => response.json())
        .then(data => {
            PongGame.config.canvasHeight = data.canvas.normal.height;
            PongGame.config.canvasWidth = data.canvas.normal.width;
            let canvas = document.getElementById('gameCanvas');
            PongGame.ctx = canvas.getContext("2d");
            canvas.width = PongGame.config.canvasWidth;
            canvas.height = PongGame.config.canvasHeight;
            PongGame.resizeCanvas();
            PongGame.setFont();
            PongGame.config.paddleHeight = data.paddle.normal.height;
            PongGame.config.paddleWidth = data.paddle.normal.width;
            PongGame.config.maxPaddleSpeed = data.paddle.normal.speed;
            PongGame.state.paddles.left.x = data.paddle.normal.ledgeOffset;
            PongGame.state.paddles.right.x = PongGame.config.canvasWidth
                                - data.paddle.normal.ledgeOffset
                                - PongGame.config.paddleWidth;
            PongGame.config.defaultBallSpeed = data.ball.speed;
            PongGame.config.ballSpeedIncrement = data.ball.speedIncrement;
            PongGame.config.maxBallSpeed = data.ball.maxSpeed;
            PongGame.config.maxBounceAngle = data.ball.maxBounceAngle;
            PongGame.config.winningScore = data.score.max;
            PongGame.setScoreCoords();
        })
}

async function initData(data, socketPath, socketMode){
    await initGameConstants();
    try {
		if (data.teams.a.players.some(player => player.id == userInformations.id)) {
			PongGame.info.myTeam.name = 'A';
			PongGame.info.myTeam.players = data.teams.a;
			PongGame.info.enemyTeam.name = 'B';
			PongGame.info.enemyTeam.players = data.teams.b;
		}
		else if (data.teams.b.players.some(player => player.id == userInformations.id)) {
			PongGame.info.myTeam.name = 'B';
			PongGame.info.myTeam.players = data.teams.b;
			PongGame.info.enemyTeam.name = 'A';
			PongGame.info.enemyTeam.players = data.teams.a;
		}
	}
	catch(error) {
		console.log(error);
		console.log('Invalid game data from SSE, cannot launch game');
		return;
	}
	initSocket(data.code, socketPath, socketMode);
    setTimeout(async () => {
        if (!cancelTimeout && gameSocket && !isModalOpen()){
            displayMainAlert('Error', 'Unable to establish connection with socket server');
            history.go(-1);
        }
    }, GAME_CONNECTION_TIMEOUT);
    document.getElementById('gameArea').classList.replace('d-none', 'd-flex');
    document.getElementById('opponentWait').classList.replace('d-flex', 'd-none');
    document.getElementById('playerUsername').innerText = userInformations.username;
    document.getElementById('enemyUsername').innerText = PongGame.info.enemyTeam.players.players[0].username;
}

document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
    PongGame.resumeGame();
})

function checkGameAuthorization(){
    if (reconnect()) return;
    if (userInformations.is_guest && window.location.pathname === '/game/ranked')
        throw `${window.location.pathname}`;
    if (window.location.pathname === '/game/tournament' && typeof tournamentData === 'undefined')
        throw `${window.location.pathname}`;
    if (window.location.pathname === '/game/1v1' && (typeof fromLobby === 'undefined' || !fromLobby))
        throw `${window.location.pathname}`;
}

async function gameStart(event){
    cancelTimeout = false;

    data = JSON.parse(event.data);
    try {
        localStorage.setItem('game-event', JSON.stringify(data));
        await initData(data.data, data.target[0].url, data.target[0].type);
    }
    catch (error){
        wrongConfigFileError(error);
    }
}

function forPhoneChanges(){
    try {
        document.getElementById('gameCanvas').style.backgroundColor = 'blue';


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
        
    let lastTouchY = undefined;
    function handleTouchStart(event) {
        const touch = event.touches[0];
        const screenHeight = window.innerHeight;
        const touchY = touch.clientY;
        
        if (touchY < screenHeight / 2) {
            if (lastTouchY && lastTouchY >= screenHeight / 2)
                simulateKey('keyup', 40)
            simulateKey('keydown', 38);
        } else {
            if (lastTouchY && lastTouchY < screenHeight / 2)
                simulateKey('keyup', 38)
            simulateKey('keydown', 40);
        }
        lastTouchY = touchY;
    }
    
    function handleTouchEnd(event) {
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

function wrongConfigFileError(error){
    displayMainAlert('Error', 'Erroneous game config file.\n');
    console.log(error);
}

function reconnect(){
    let event = localStorage.getItem('game-event');
    if (event){
        event = JSON.parse(event);
        let gameMode = window.location.pathname.split('/')[2]
        if (event.data.game_mode === gameMode || 
            (event.data.game_mode === 'custom_game' && gameMode === '1v1') ||
            (event.data.game_mode === 'custom_game' && gameMode === '3v3')){
            initData(event.data, event.target[0].url, event.target[0].type);
            if (gameMode === 'tournament'){
                if (!fromTournament)
                    localStorage.setItem('tournament-code-reconnect', localStorage.getItem('tournament-code'));
                fromTournament = true;
            }
            else if (event.data.game_mode === 'custom_game'){
                fromLobby = true;
            }
            return 1;
        }
    }
    return 0;
}
 
async function initGame(){
    await indexInit(false);
    if (window.matchMedia("(hover: none) and (pointer: coarse)").matches)
        forPhoneChanges();
    if (window.location.pathname === '/') return;
    document.getElementById('gameArea').classList.replace('d-flex', 'd-none');
    document.getElementById('opponentWait').classList.replace('d-none', 'd-flex');
    try {
        checkGameAuthorization();
        if (window.location.pathname === '/game/tournament'){
            async function tournamentFinished(event){
                event = JSON.parse(event.data);
                await navigateTo('/', true, true); //todo replace by tournament history
                displayNotification(undefined, 'tournament finished', event.message, undefined, undefined); //todo add target 
            }
            if (!SSEListeners.has('tournament-finish')){
                SSEListeners.set('tournament-finish', tournamentFinished);
                sse.addEventListener('tournament-finish', tournamentFinished);
            }
            // await initData(...tournamentData);
        }
        else if (window.location.pathname === '/game/1v1')
            return;
            // await initData(...(userInformations.lobbyData));
        else {
            if (SSEListeners.has('game-start')){
                sse.removeEventListener('game-start', SSEListeners.get('game-start'));
                SSEListeners.delete('game-start');
            }
            SSEListeners.set('game-start', gameStart);
            sse.addEventListener('game-start', gameStart);
            try {
                let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/${window.location.pathname.split('/')[2]}/`, 'POST');
                if (data.detail){
                    if (reconnect()) return;
                    document.getElementById('opponentWait').innerText = data.detail;
                }
            }
            catch(error) {
                console.log(error);
            }
        }
    }
    catch (unauthorized){
        if (unauthorized === window.location.pathname){
            if (!document.getElementById('alertModal').classList.contains('show'))
                displayMainAlert("Error", `You don't have permission to play in ${unauthorized}`);
            history.go(-1);
        }
        else{
            wrongConfigFileError(unauthorized);
        }
    }
}

initGame();
