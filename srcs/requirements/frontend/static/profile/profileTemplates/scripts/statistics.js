async function loadStatistics(){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/stats/`);
        for (gameMode in data){
            let gameStats = data[gameMode];
            let gameStatsDiv = document.createElement('div');
            gameStatsDiv.id = `s${gameStats.game_mode}`;
            gameStatsDiv.className = 'col-4 justify-content-center';
            let gameModeDiv = document.createElement('div');
            gameModeDiv.className = 'stats-game-mode';
            gameStatsDiv.appendChild(gameModeDiv);
            const html = `
                <div class='d-flex justify-content-between'>
                <h2 class=''>${gameStats.game_mode}</h2>
                <div class='small text-center align-middle' style='color: white'>scored: ${gameStats.scored}</div></div>
                <canvas class='statChart'></canvas>
            `
            gameStatsDiv.insertAdjacentHTML("beforeend", html);
            document.getElementById('statisticsContainer').appendChild(gameStatsDiv);
            
            const chartData = {
                labels: [
                    'Win Streak',
                    'Games Played',
                    'Longest Win Streak',
                    'Wins',
                ],
                datasets: [{
                    label: 'Game Statistics',
                    data: [
                        gameStats.current_win_streak,
                        gameStats.game_played,
                        gameStats.longest_win_streak,
                        gameStats.wins,
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(153, 102, 255, 1)',
                    ],
                    borderWidth: 1,
                }],
            };
    
            const options = {
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.raw}`;
                            },
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                if (Number.isInteger(value)) {
                                    return value;
                                }
                                return null;
                            },
                        },
                        
                    },
                },
            };
    
            const ctx = gameStatsDiv.querySelector('.statChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: chartData,
                options: options,
            });
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