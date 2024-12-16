if (typeof gameMode === 'undefined')
    var gameMode;
if (typeof code === 'undefined')
    var code;
if (typeof isReady === 'undefined')
    var isReady;

document.getElementById('leaveLobby').addEventListener('click', async () => {
    await navigateTo('/');
})

document.getElementById('settingsButton').addEventListener('click', event => {
    event.preventDefault();
    const settingsModal = new bootstrap.Modal(document.getElementById('lobbySettingsModal'));
    settingsModal.show();
})

document.getElementById("inviteFriends").addEventListener("click", event => {
    event.preventDefault();
    const currentURL = window.location.href;

    navigator.clipboard.writeText(currentURL)
        .then(() => {
            const feedback = document.getElementById("feedback");
            feedback.style.display = "block";
            setTimeout(() => feedback.style.display = "none", 1000);
        })
        .catch(err => {
            console.error("Failed to copy URL: ", err);
        });
});

document.getElementById('joinLobby').addEventListener('click', async event => {
    event.preventDefault();
    const joinErrorDiv = document.getElementById('joinLobbyError');
    const joinCode = document.getElementById('joinCode').value;
    if (isNaN(parseInt(joinCode)))
        return joinErrorDiv.innerText = 'please enter a valid code';
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${joinCode}/`, 'POST');
        console.log(data);
        if (data.detail)
            return joinErrorDiv.innerText = data.detail;
        code = data.code;
        gameMode = data.game_mode === 'clash' ? '3v3': 'Custom Game';
        if (gameMode === '3v3'){
            document.getElementById('teamSelector').style.display = 'none';
        }
        document.getElementById('gameId').innerText = data.code;
        document.getElementById('gameType').innerText = data.game_mode === 'clash' ? '3v3' : 'Custom Game';
        navigateTo(`/lobby/${data.code}`, false);
        document.getElementById('settingsButton').style.display = 'none';
        await fillPlayerList(data);
    }
    catch (error){
        if (error.code === 404){
            return joinErrorDiv.innerText = 'this lobby does not exists';
        }
        return console.log(error);
    }
})

async function fillPlayerList(data){
    const playerListDiv = document.getElementById('teamDisplay');
    playerListDiv.innerHTML = "";
    console.log(data);
    for (let player in data.participants){
        player = data.participants[player];
        if (player.id === userInformations.id)
            isReady = player.is_ready;
        const playerDiv = document.createElement('div');
        playerDiv.id = `player${player.id}`;
        playerListDiv.appendChild(playerDiv);
        await loadContent('/lobby/player.html', `${playerDiv.id}`);
        playerDiv.querySelector('.playerUsername').innerText = player.username;
        playerDiv.querySelector('.playerTrophies').innerText = player.trophies;
        playerDiv.querySelector('.playerIsReady').innerText = player.is_ready ? 'Ready' : 'Not ready';
    }

    document.getElementById(`player${userInformations.id}`).querySelector('.playerIsReady').addEventListener('click', async function(){
        isReady = !isReady;
        try {
            await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'PATCH', undefined, undefined, {
                'is_ready' : isReady,
            })
            this.innerText = isReady ? 'Ready' : 'Not Ready';
        }
        catch (error) {
            console.log('error');
        }
    })
}

async function lobbyInit() {
    await indexInit(false);
    code = window.location.pathname.split('/')[2];
    if (window.location.pathname === '/') return;
    loadCSS('/css/lobby.css', false);
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`, 'GET');
        if (data.code && data.code != code && code !== undefined)
            throw {code:404};
        if (data.code && code === undefined)
            await navigateTo(`/lobby/${data.code}`, false);
        if (data.code) {
            code = data.code;
            gameMode = data.game_mode === 'clash' ? '3v3': 'Custom Game';
            if (gameMode === '3v3'){
                document.getElementById('settingsButton').style.display = 'none';
                document.getElementById('teamSelector').style.display = 'none';
            }
            document.getElementById('gameType').innerText = gameMode;
            document.getElementById('gameId').innerText = data.code;
            await fillPlayerList(data);
        }
        console.log(data);
    }
    catch(error){
        try {
            if (code === undefined)
                throw {code:404};
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'POST');
            if (data.code) {
                code = data.code;
                document.getElementById('settingsButton').style.display = 'none';
                gameMode = data.game_mode === 'clash' ? '3v3': 'Custom Game';
                if (gameMode === '3v3'){
                    document.getElementById('settingsButton').style.display = 'none';
                    document.getElementById('teamSelector').style.display = 'none';
                }
                document.getElementById('gameType').innerText = gameMode;
                document.getElementById('gameId').innerText = data.code;
                await fillPlayerList(data);
            }
            if (data.detail === 'Lobby is full.')
                throw {code:404}
        }
        catch (subError){
            if (subError.code === 404){
                displayMainAlert('Unable to join the lobby', 'It may not exist, has been deleted, or is already full.');
                await navigateTo('/');
            }
            console.log(subError);
        }
    }
}

lobbyInit();