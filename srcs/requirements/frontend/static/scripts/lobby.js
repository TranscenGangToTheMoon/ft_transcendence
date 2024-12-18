if (typeof gameMode === 'undefined')
    var gameMode;
if (typeof code === 'undefined')
    var code;
if (typeof isReady === 'undefined')
    var isReady;
if (typeof team === 'undefined')
    var team;
if (typeof matchType === 'undefined')
    var matchType;
if (typeof creator === 'undefined')
    var creator;

document.getElementById('leaveLobby').addEventListener('click', async () => {
    await navigateTo('/');
})

document.getElementById('settingsButton').addEventListener('click', async function() {
    try {
        const newMatchType = matchType === '1v1' ? '3v3' : '1v1';
        await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`, 'PATCH', undefined, undefined, {
            'match_type' : newMatchType,
        })
        this.innerText = newMatchType;
        matchType = newMatchType;
    }
    catch (error){
        console.log(error);
    }
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
        if (data.detail)
            return joinErrorDiv.innerText = data.detail;
        code = data.code;
        matchType = data.match_type;
        document.getElementById('settingsButton').innerText = matchType;
        gameMode = data.game_mode === 'clash' ? '3v3': 'Custom Game';
        if (gameMode === '3v3'){
            document.getElementById('teamSelector').style.display = 'none';
        }
        else{
            document.getElementById('teamSelector').style.removeProperty('display');
            getTeam(data);
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

function getTeam(data){
    for (player in data.participants){
        player = data.participants[player];
        if (player.id === userInformations.id)
            team = player.team;
    }
}

async function fillBench(player){
    const benchDiv = document.getElementById('benchPlayerList');
    const playerDiv = document.createElement('div');
    playerDiv.id = `benchPlayer${player.id}`;
    if (player.id === userInformations.id || creator){
        playerDiv.draggable = 'true';
        playerDiv.classList.add('draggable');
    }
    benchDiv.appendChild(playerDiv);
    await loadContent('/lobby/player.html', `${playerDiv.id}`);
    if (player.username.length > 5)
        player.username = player.username.substring(0, 5) + '..';
    playerDiv.querySelector('.playerUsername').innerText = player.username;
    playerDiv.querySelector('.playerIsReady').style.display = 'none';
    playerDiv.querySelector('.playerId').innerText = player.id;
}

async function fillTeamDisplay(player){
    if (player.team === 'Spectator') return;
    const teamDisplayDiv = document.getElementById((player.team === 'Team A' ? 'teamA' : 'teamB') + 'Display');
    const playerDiv = document.createElement('div');
    if (player.id === userInformations.id || creator){
        playerDiv.classList.add('draggable');
        playerDiv.draggable = true;
    }
    playerDiv.id = `teamPlayer${player.id}`;
    teamDisplayDiv.appendChild(playerDiv);
    await loadContent('/lobby/player.html', `${playerDiv.id}`);
    if (player.username.length > 5)
        player.username = player.username.substring(0, 5) + '..';
    playerDiv.querySelector('.playerUsername').innerText = player.username;
    playerDiv.querySelector('.playerIsReady').style.display = 'none';
    playerDiv.querySelector('.playerId').innerText = player.id;

}

async function makeRequest(dropzone, draggable){
    let dropTeam = dropzone.id.substring(0, 5);
    switch(dropTeam){
        case 'teamA':
            dropTeam = 'Team A';
            break;
        case 'teamB':
            dropTeam = 'Team B';
            break;
        default:
            dropTeam = 'Spectator';
            break;
    }
    if (dropTeam === team) return;
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'PATCH',undefined, undefined, {
            'team' : dropTeam,
        })
        team = dropTeam;
        return data.detail ? 0 : 1;
    }
    catch(error){
        console.log(error);
        return 0;
    }
}

async function reloadPlayerList(){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`);
        fillPlayerList(data, true);
    }
    catch(error){
        console.log(error);
    }
}

function initDragAndDrop(){
    const draggables = document.querySelectorAll(".draggable");
    const dropzones = document.querySelectorAll(".dropzone");

    draggables.forEach((draggable, index) => {
        if (!draggable.id) {
            draggable.id = `draggable-${index}`;
        }
    });

    draggables.forEach(draggable => {
        draggable.addEventListener("dragstart", (e) => {
            e.dataTransfer.setData("text/plain", e.target.id);
            e.target.classList.add("dragging");
        });

        draggable.addEventListener("dragend", (e) => {
            e.target.classList.remove("dragging");
        });
    });

    dropzones.forEach(dropzone => {
        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("hovered");
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("hovered");
        });

        dropzone.addEventListener("drop", async (e) => {
            e.preventDefault();
            dropzone.classList.remove("hovered");
            const draggableId = e.dataTransfer.getData("text/plain");
            const draggable = document.getElementById(draggableId);

            if (draggable && await makeRequest(dropzone, draggable)) {
                dropzone.appendChild(draggable);
                await reloadPlayerList();
            }
        });
    });
}

document.addEventListener('click', (e) => {
    if (!contextMenu.contains(e.target))
        document.getElementById('contextMenu').style.display = 'none';
});

document.addEventListener('keyup', e => {
    if (e.key === 'Escape')
        document.getElementById('contextMenu').style.display = 'none';
})

function removeIds(playerListDiv){
    const playerDivs = playerListDiv.querySelectorAll('.player');
    for (let player of playerDivs)
        player.parentElement.removeAttribute('id');
}

if (typeof clickedUserDiv === 'undefined')
    var clickedUserDiv;

function addContextMenus(){
    const playerDivs = document.querySelectorAll('.player');
    if (!creator)
        document.getElementById('cKick').style.display = 'none';
    for (let playerDiv of playerDivs){
        if (playerDiv.querySelector('.playerUsername').innerText === userInformations.username)
            continue;
        playerDiv.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            clickedUserDiv = this;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.display = 'block';
        });
    }
}

document.getElementById('cKick').addEventListener('click', async ()=> {
    const kickedUserId = clickedUserDiv.querySelector('.playerId').innerText;
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/kick/${kickedUserId}/`, 'DELETE');
    }
    catch(error){
        console.log(error);
    }
})

document.getElementById('cFriendRequest').addEventListener('click', async () => {
    const friendRequestUsername = clickedUserDiv.querySelector('.playerUsername').innerText;
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
            'username' : friendRequestUsername,
        })
        const validator = document.getElementById('friendRequestValidator');
        validator.style.removeProperty('display');
        setTimeout(()=> validator.style.display='none', 1500);
    }
    catch (error){
        console.log(error);
    }
})

document.getElementById('cBlock').addEventListener('click', async () => {
    const blockedUserId = clickedUserDiv.querySelector('.playerId').innerText;
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
            'user_id' : blockedUserId
        })
    }
    catch (error){
        console.log(error);
    }
})

async function fillPlayerList(data, noTeam=false){
    const playerListDiv = document.getElementById('teamDisplay');
    removeIds(playerListDiv);
    const tempDiv = document.createElement('div');
    tempDiv.style.display = 'none';
    document.body.appendChild(tempDiv);
    for (let player in data.participants){
        player = data.participants[player];
        if (gameMode === 'Custom Game' && !noTeam)
            await fillTeamDisplay(player);
        if (player.id === userInformations.id){
            isReady = player.is_ready;
            creator = player.creator;
            if (gameMode === 'Custom Game' && !player.creator)
                document.getElementById('settingsButton').style.display = 'none';
        }
        if (gameMode === 'Custom Game' && player.team === 'Spectator'){
            if (!noTeam)
                await fillBench(player);
            continue;
        }
        if (gameMode === 'Custom Game' && player.team != team)
            continue;
        const playerDiv = document.createElement('div');
        playerDiv.id = `player${player.id}`;
        tempDiv.appendChild(playerDiv);
        await loadContent('/lobby/player.html', `${playerDiv.id}`);
        playerDiv.querySelector('.playerUsername').innerText = player.username;
        playerDiv.querySelector('.playerId').innerText = player.id;
        playerDiv.querySelector('.playerTrophies').innerText = player.trophies;
        playerDiv.querySelector('.playerIsReady').innerText = player.is_ready ? 'Ready' : 'Not ready';
    }
    playerListDiv.innerHTML = tempDiv.innerHTML;
    tempDiv.remove();
    addContextMenus();
    document.getElementById(`player${userInformations.id}`)?.querySelector('.playerIsReady').addEventListener('click', async function(){
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
    if (!noTeam)
        initDragAndDrop();
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
            matchType = data.match_type;
            document.getElementById('settingsButton').innerText = matchType;
            gameMode = data.game_mode === 'clash' ? '3v3': 'Custom Game';
            if (gameMode === '3v3'){
                document.getElementById('settingsButton').style.display = 'none';
                document.getElementById('teamSelector').style.display = 'none';
            }
            else
                getTeam(data);
            document.getElementById('gameType').innerText = gameMode;
            document.getElementById('gameId').innerText = data.code;
            await fillPlayerList(data);
        }
    }
    catch(error){
        try {
            console.log(error);
            if (code === undefined)
                throw {code:404};
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'POST');
            if (data.code) {
                code = data.code;
                matchType = data.match_type;
                document.getElementById('settingsButton').innerText = matchType;
                document.getElementById('settingsButton').style.display = 'none';
                gameMode = data.game_mode === 'clash' ? '3v3': 'Custom Game';
                if (gameMode === '3v3'){
                    document.getElementById('settingsButton').style.display = 'none';
                    document.getElementById('teamSelector').style.display = 'none';
                }
                else{
                    getTeam(data);
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