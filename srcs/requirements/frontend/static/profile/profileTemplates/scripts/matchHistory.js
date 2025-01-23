if (typeof loadedHistory === 'undefined')
    var loadedHistory;
if (typeof loadingHistory === 'undefined')
    var loadingHistory = false;

function sortByTimeStamp(){
    loadedHistory.results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

async function loadMatches(noRequest=false){
    const historyDiv = document.querySelector('#historyContainer');
    historyDiv.innerHTML = '';
    try {
        if (!noRequest)
            loadedHistory = await apiRequest(getAccessToken(), `${baseAPIUrl}/game/matches/${userInformations.id}/?limit=20&offset=0`);
        if (loadedHistory.count){
            sortByTimeStamp();
            loadedHistory.results.forEach(match => {
                var playerTeam;
                var playerTeamName;
                var enemyTeam;
                let matchDate = new Date(match.created_at);
                const [hours, minutes, seconds] = match.game_duration.split('.')[0].split(':');
                for (i in match.teams){
                    for (j in match.teams[i].players){
                        if (match.teams[i].players[j].id === userInformations.id){
                            playerTeam = match.teams[i];
                            playerTeamName = i;
                            if (!enemyTeam)
                                enemyTeam = match.teams[i === 'a' ? 'b' : 'a'];
                            break;
                        }
                    }
                    if (playerTeam)
                        break;
                    enemyTeam = match.teams[i];
                }
                const matchDiv = document.createElement('div');
                matchDiv.style.backgroundColor = 'red';
                matchDiv.linkedMatchId = match.id;
                matchDiv.className = 'match d-flex row m-1';
                matchDiv.innerHTML = `
                <div class="match-gamemode col d-flex align-items-center">${match.game_mode}</div>
                <div class="col d-flex align-items-center">${match.winner === playerTeamName ? 'victory' : 'defeat'}</div>
                <div class="col d-flex align-items-center">${playerTeam.score} - ${enemyTeam.score}</div>
                <div class='col'>
                    <div>${matchDate.getDate()}/${matchDate.getMonth() + 1}/${matchDate.getFullYear()}</div>
                    <div>${minutes}m ${seconds}s</div>
                </div>
                `
                historyDiv.appendChild(matchDiv);
            });
        }
    }
    catch (error){
        console.log(error);
    }
}

async function getMoreMatches(){
    if (!loadedHistory.next) return;
    loadingHistory = true;
    try {
        let data = await apiRequest(getAccessToken(), loadedHistory.next);
        loadedHistory.next = data.next;
        // console.log('addition',data);
        for (i in data.results){
            loadedHistory.results.push(data.results[i]);
            // console.log('adding', data.results[i]);
        }
        // console.log('total', loadedHistory);
        loadMatches(true);
        addMatchDetail();
    }
    catch(error){
        console.log(error);
    }
    loadingHistory = false;
}

document.addEventListener('scroll', async event => {
    if (event.target.id === 'historyContainer'){
        const history = document.getElementById('historyContainer');
        const scrollHeight = history.scrollHeight;
        const clientHeight = history.clientHeight;
        const scrollTop = history.scrollTop;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        if (scrollPercentage >= 75 && !loadingHistory) {
            loadingHistory = true;
            await getMoreMatches();
            loadingHistory = false;
        }
    }
}, true);

function addTournamentDisplayOption(detailDiv, tournamentId){
    const row = document.createElement('div');
    row.className = 'row py-2 px-5';
    detailDiv.appendChild(row);
    const button = document.createElement('button');
    button.className  = 'btn btn-secondary';
    button.innerText = 'See Tournament Bracket';
    row.appendChild(button);
    button.addEventListener('click', async event => {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/game/tournaments/${tournamentId}/`);
            createBracket(data, true);
            const bracketModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('tournamentBracket'));
            bracketModal.show();
        }
        catch (error) {
            console.log(error);
        }
    })
}

function addMatchDetail(){
    const matchDivs = document.querySelectorAll('.match');
    matchDivs.forEach(matchDiv => {
        matchDiv.addEventListener('click', event => {
            const match = loadedHistory.results.find(match => match.id === matchDiv.linkedMatchId);
            // console.log('lematch', match);
            const detailDiv = document.getElementById('matchTeamDetail');
            detailDiv.innerHTML = '';
            // console.log(match.teams);
            for (i in match.teams){
                let team = match.teams[i];
                const teamRow = document.createElement('div');
                teamRow.className = 'row py-2';
                detailDiv.appendChild(teamRow);
                const teamPlayersCol = document.createElement('div');
                teamPlayersCol.className = 'col-8';
                teamRow.appendChild(teamPlayersCol);
                const scoreCol = document.createElement('div');
                scoreCol.className = 'col m-auto';
                scoreCol.innerText = team.score;
                teamRow.appendChild(scoreCol);
                team.players.forEach(player => {
                    const playerRow = document.createElement('div');
                    playerRow.className = 'row m-auto';
                    playerRow.style.backgroundColor = 'blue';
                        playerRow.innerHTML = `
                        <img class='col-2 p-1' src='${player['profile-picture']}' onerror="this.onerror=null; this.src='/assets/imageNotFound.png'" 
                        alt="profile pic"></img>
                        <div class='col m-auto'>${player.username}</div>
                        `
                    teamPlayersCol.appendChild(playerRow);
                })
            }
            if (match.game_mode === 'tournament')
                addTournamentDisplayOption(detailDiv, match.tournament_id);
            detailDiv.parentElement.classList.remove('d-none');
        })
    })
}

async function initHistory(){
    await loadScript('/tournament/scripts/createBracket.js');
    loadCSS('/tournament/css/tournament.css');
    await loadMatches();
    addMatchDetail();
}

initHistory();