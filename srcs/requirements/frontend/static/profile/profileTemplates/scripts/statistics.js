async function loadStatistics(){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/stats/`);
        console.log(data);
        for (gameMode in data){
            let gameStats = data[gameMode];
            let gameStatsDiv = document.createElement('div');
            gameStatsDiv.id = `s${gameStats.game_mode}`;
            let gameModeDiv = document.createElement('div');
            gameModeDiv.className = 'stats-game-mode';
            gameModeDiv.innerText = gameStats.game_mode;
            gameStatsDiv.appendChild(gameModeDiv);
            const html = `
                <div class='stat-win-streak'>win streak: ${gameStats.current_win_streak}</div>
                <div class='stat-game-played'>game played: ${gameStats.game_played}</div>
                <div class='stat-longest-win-streak'>longest win streak: ${gameStats.longest_win_streak}</div>
                <div class='scored'>scored: ${gameStats.scored}</div>
                <div class='wins'>wins: ${gameStats.wins}</div>
            `
            gameStatsDiv.insertAdjacentHTML("beforeend", html);
            document.getElementById('statisticsContainer').appendChild(gameStatsDiv);
        }
    }
    catch (error){
        console.log(error);
    }
}

async function initStatistics(){
    await loadStatistics();
}

initStatistics();