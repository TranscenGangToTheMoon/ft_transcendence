(function PongGame() {
    let isGameActive = false;
    let gameState = {};
    
    function startGame() {
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
        // Logique pour mettre à jour l'état du jeu
    }
    
    function drawGame() {
    }
    
    // Expose des fonctions globales si nécessaire
    window.PongGame = { startGame, stopGame , isGameActive};
})();

async function initGame(){
    await indexInit(false);
    window.PongGame.startGame();
    
}


initGame();