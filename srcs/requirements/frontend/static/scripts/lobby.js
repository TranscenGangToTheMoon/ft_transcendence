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
if (typeof lobby === 'undefined')
    var lobby;

document.getElementById('leaveLobby').addEventListener('click', async () => {
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'DELETE');
    }
    catch(error){
        console.log(error);
    }
    await navigateTo('/');
})


document.getElementById("copyLink").addEventListener("click", event => {
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

document.getElementById('inviteFriends').addEventListener('click', async event => {
    const onlineFriendsDiv = document.getElementById('iOnlineFriends');
    const fullFriendsDiv = document.getElementById('iFriends');
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friends/?online=true`);
        console.log(data);
        if (!data.count)
            fullFriendsDiv.style.display = 'none';
        else{
            onlineFriendsDiv.innerHTML += '<li><button class="dropdown-item">loading...</butto></li>';
            fullFriendsDiv.style.display = 'block';
            const tempDiv = document.createElement('div');
            for (i in data.results){
                let friend = data.results[i].friend;
                let friendDiv = document.createElement('li');
                let button = document.createElement('button');
                button.classList.add('dropdown-item');
                tempDiv.appendChild(friendDiv);
                friendDiv.appendChild(button);
                button.innerText = friend.username;
                button.id = `oFriend${friend.id}`
                button.addEventListener('click', async event => {
                    event.preventDefault();
                    try {
                        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/invite/${friend.id}/`, 'POST');
                        console.log(data);
                    }
                    catch (error) {
                        if (error.code === 404){
                            const feedback = document.getElementById("feedback");
                            feedback.innerText = 'user disconnected';
                            feedback.style.display = "block";
                            setTimeout(() => {
                                feedback.style.display = "none";
                                feedback.innerText = "Link copied to clipboard";
                            }, 1000);
                        }
                    }
                })
            }
            setTimeout(()=> {
                onlineFriendsDiv.innerHTML = tempDiv.innerHTML;
            }, 700);
        }

    }
    catch(error){
        console.log(error);
    }
})

document.getElementById('joinLobby').addEventListener('click', async event => {
    event.preventDefault();
    const joinErrorDiv = document.getElementById('joinLobbyError');
    const joinCode = document.getElementById('joinCode').value;
    if (isNaN(parseInt(joinCode)))
        return joinErrorDiv.innerText = 'please enter a valid code';
    try {
        lobby = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${joinCode}/`, 'POST');
        if (lobby.detail)
            return joinErrorDiv.innerText = lobby.detail;
        code = lobby.code;
        matchType = lobby.match_type;
        document.getElementById('settingsButton').innerText = matchType;
        gameMode = lobby.game_mode === 'clash' ? '3v3': 'Custom Game';
        if (gameMode === '3v3'){
            document.getElementById('teamSelector').style.display = 'none';
        }
        else{
            document.getElementById('teamSelector').style.removeProperty('display');
            getTeam(lobby);
        }
        document.getElementById('gameId').innerText = lobby.code;
        document.getElementById('gameType').innerText = lobby.game_mode === 'clash' ? '3v3' : 'Custom Game';
        navigateTo(`/lobby/${lobby.code}`, false);
        // document.getElementById('settingsButton').style.display = 'none';
        await fillPlayerList();
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

async function fillBench(player, benchDiv){
    const playerDiv = document.createElement('div');
    playerDiv.id = `teamPlayer${player.id}`;
    if (player.id === userInformations.id){
        playerDiv.draggable = 'true';
        playerDiv.classList.add('draggable');
    }
    benchDiv.querySelector('#benchPlayerList').appendChild(playerDiv);
    await loadContent('/lobby/player.html', undefined, false, playerDiv);
    playerDiv.querySelector('.playerUsername').innerText = player.username;
    playerDiv.querySelector('.playerIsReady').style.display = 'none';
    playerDiv.querySelector('.playerId').innerText = player.id;
}

async function fillTeamDisplay(player, teamSelectorDiv){
    if (player.team === 'Spectator') return;
    const teamDisplayDiv = teamSelectorDiv.querySelector((player.team === 'Team A' ? '#teamA' : '#teamB') + 'Display');
    const playerDiv = document.createElement('div');
    if (player.id === userInformations.id){
        playerDiv.classList.add('draggable');
        playerDiv.draggable = true;
    }
    playerDiv.id = `teamPlayer${player.id}`;
    // teamDisplayDiv.appendChild(playerDiv);
    // let placeholders = teamDisplayDiv.querySelectorAll('.no-player');
    // teamDisplayDiv.insertBefore(playerDiv, placeholders[0]);
    // if (placeholders.length)
    //     placeholders[0].remove();
    teamDisplayDiv.appendChild(playerDiv);
    await loadContent('/lobby/player.html', undefined, false, playerDiv);
    playerDiv.querySelector('.playerUsername').innerText = player.username;
    playerDiv.querySelector('.playerIsReady').style.display = 'none';
    playerDiv.querySelector('.playerId').innerText = player.id;

}

async function makeRequest(dropzone){
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
    if (dropTeam === team) return undefined;
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'PATCH',undefined, undefined, {
            'team' : dropTeam,
        })
        if (data.detail)
            return undefined;
        team = dropTeam;
        return dropTeam;
    }
    catch(error){
        console.log(error);
        return undefined;
    }
}

async function reloadPlayerList(){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`);
        await fillPlayerList(true);
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

            const dropTeam = await makeRequest(dropzone);
            if (draggable && dropTeam) {
                let playerId = draggable.querySelector('.playerId').innerText
                for (participant in lobby.participants){
                    if (lobby.participants[participant].id == playerId)
                        lobby.participants[participant].team = dropTeam;
                }
                await fillPlayerList();
            }
        });
    });
}

function removeIds(playerListDiv){
    const playerDivs = playerListDiv.querySelectorAll('.player');
    for (let player of playerDivs){
        player.parentElement.removeAttribute('id');
    }
}

if (typeof clickedUserDiv === 'undefined')
    var clickedUserDiv;

function addContextMenus(){ 
    const playerDivs = document.querySelectorAll('.player');
    const banButton = document.getElementById('cBan');
    if (!creator)
        banButton.classList.add('disabled');
    else{
        if (banButton.classList.contains('disabled'))
            banButton.classList.remove('disabled');
    }
    for (let playerDiv of playerDivs){
        if (playerDiv.querySelector('.playerUsername').innerText === userInformations.username)
            continue;
        playerDiv.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            clickedUserDiv = this;
            const contextMenu = document.getElementById('contextMenu');
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.display = 'block';
        });
    }
}

document.getElementById('cBan').addEventListener('click', async ()=> {
    const kickedUserId = clickedUserDiv.querySelector('.playerId').innerText;
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/banned/${kickedUserId}/`, 'DELETE');
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

async function completeTeams(lobbyOptionsDiv){
    const teamsDivs = lobbyOptionsDiv.querySelectorAll('.teamDisplay');
    for (let teamDiv of teamsDivs){
        let playerInTeam = teamDiv.querySelectorAll('.player').length;
        for (; playerInTeam < (matchType === '1v1' ? 1 : 3); playerInTeam++){
            playerPlaceholder = document.createElement('div');
            playerPlaceholder.id = 'tempPl';
            teamDiv.appendChild(playerPlaceholder);
            await loadContent('/lobby/no_player.html', playerPlaceholder.id);
            playerPlaceholder.removeAttribute('id');
            playerPlaceholder.classList.add('no-player');
        }
    }
    const benchPlaceholder = lobbyOptionsDiv.querySelector('#benchPlayerList').querySelector('.no-player');
    if (!benchPlaceholder){
        playerPlaceholder = document.createElement('div');
        playerPlaceholder.id = 'tempPl';
        lobbyOptionsDiv.querySelector('#benchPlayerList').appendChild(playerPlaceholder);
        await loadContent('/lobby/no_player.html', playerPlaceholder.id ,true);
        playerPlaceholder.removeAttribute('id');
        playerPlaceholder.classList.add('no-player');
    }
}

async function updateOwnTeam(player, teamDisplayDiv, teamSelectorDiv, benchDiv, noTeam=false){
    if (gameMode === 'Custom Game' && !noTeam)
        await fillTeamDisplay(player, teamSelectorDiv);
    if (player.id === userInformations.id){
        isReady = player.is_ready;
        creator = player.creator;
    }
    if (gameMode === 'Custom Game' && player.team === 'Spectator'){
        if (!noTeam)
            await fillBench(player, benchDiv);
        return;
    }
    if (gameMode === 'Custom Game' && player.team != team)
        return;
    const playerDiv = document.createElement('div');
    playerDiv.id = `player${player.id}`;
    teamDisplayDiv.appendChild(playerDiv);
    await loadContent('/lobby/player.html', undefined, false, playerDiv);
    playerDiv.querySelector('.playerUsername').innerText = player.username;
    playerDiv.querySelector('.playerId').innerText = player.id;
    playerDiv.querySelector('.playerTrophies').innerText = player.trophies;
    playerDiv.querySelector('.playerIsReady').innerText = player.is_ready ? 'Ready' : 'Not ready';
}

async function fillPlayerList(noTeam=false){
    const lobbyOptionsDiv = document.getElementById('lobbyOptions');
    const tempDiv = document.createElement('div');
    tempDiv.style.display = 'none';
    tempDiv.innerHTML = lobbyOptionsDiv.innerHTML;
    removeIds(lobbyOptionsDiv);
    
    let dropzones = tempDiv.querySelectorAll('.dropzone');
    for (let dropzone of dropzones)
        dropzone.innerHTML = '';
    tempDiv.querySelector('#teamDisplay').innerHTML = '';
    document.body.appendChild(tempDiv);
    const teamDisplayDiv = tempDiv.querySelector('#teamDisplay');
    const teamSelectorDiv = tempDiv.querySelector('#teamSelector');
    const benchDiv = tempDiv.querySelector('#bench');
    for (let player in lobby.participants){
        player = lobby.participants[player];
        await updateOwnTeam(player, teamDisplayDiv, teamSelectorDiv, benchDiv, noTeam);
    }
    if (!noTeam)
        await completeTeams(tempDiv);
    lobbyOptionsDiv.innerHTML = tempDiv.innerHTML;
    
    document.getElementById('settingsButton').addEventListener('click', async function() {
        if (!creator || gameMode != 'Custom Game') return;
        try {
            const newMatchType = matchType === '1v1' ? '3v3' : '1v1';
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`, 'PATCH', undefined, undefined, {
                'match_type' : newMatchType,
            })
            if (!data.detail){
                matchType = newMatchType;
                this.innerText = newMatchType;
                lobby = data;
                await fillPlayerList();
            }
        }
        catch (error){
            console.log(error);
        }
    })
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

async function lobbyJoined(event){
    event = JSON.parse(event.data);
    console.log(event);
    if (!checkEventDuplication(event)) return;
    lobby.participants[lobby.participants.length] = event.data;
    await fillPlayerList();
}

async function lobbyLeaved(event){
    event = JSON.parse(event.data);
    console.log(event);
    if (!checkEventDuplication(event)) return;
    for (let participant in lobby.participants){
        if (lobby.participants[participant].id === event.data.id)
            lobby.participants.splice(participant, 1);
    }
    await fillPlayerList();
}

async function participantUpdated(event){
    event = JSON.parse(event.data);
    console.log(event);
    if (!checkEventDuplication(event)) return;
    const data = event.data;
    for (let participant in lobby.participants){
        if (lobby.participants[participant].id === data.id){
            if (data.team !== undefined){
                lobby.participants[participant].team = data.team;
                if (data.id === userInformations.id)
                    team = data.team;
            }
            if (data.is_ready !== undefined)
                lobby.participants[participant].is_ready = data.is_ready;
            if (data.creator !== undefined){
                lobby.participants[participant].creator = data.creator;
                if (data.id === userInformations.id)
                    creator = data.creator;
            }
        }
    }
    await fillPlayerList();
}

async function lobbyUpdated(event){
    event = JSON.parse(event.data);
    if (!checkEventDuplication(event)) return;
    console.log(event.data);
    if (event.data.match_type){
        matchType = event.data.match_type;
        document.getElementById('settingsButton').innerText = event.data.match_type;
        console.log(lobby);
        await fillPlayerList();
    }
}

async function lobbyBanned(event){
    event = JSON.parse(event.data);
    console.log(event);
    if (!checkEventDuplication(event)) return;
    await navigateTo('/');
    displayMainAlert('Banned from Lobby', event.message);
}

async function lobbyDestroyed(event){
    await navigateTo('/');
    console.log(JSON.parse(event.data));
    displayMainAlert('Lobby destroyed', "The lobby has been destroyed.")
}

function initLobbySSEListeners(){
    if (!SSEListeners.has('lobby-join')){
        SSEListeners.set('lobby-join', lobbyJoined);
        sse.addEventListener('lobby-join', lobbyJoined);
    }

    if (!SSEListeners.has('lobby-leave')){
        SSEListeners.set('lobby-leave', lobbyLeaved);
        sse.addEventListener('lobby-leave', lobbyLeaved);
    }

    if (!SSEListeners.has('lobby-banned')){
        SSEListeners.set('lobby-banned', lobbyBanned);
        sse.addEventListener('lobby-banned', lobbyBanned);
    }

    if (!SSEListeners.has('lobby-update')){
        SSEListeners.set('lobby-update', lobbyUpdated);
        sse.addEventListener('lobby-update', lobbyUpdated);
    }

    if (!SSEListeners.has('lobby-update-participant')){
        SSEListeners.set('lobby-update-participant', participantUpdated);
        sse.addEventListener('lobby-update-participant', participantUpdated);
    }

    if (!SSEListeners.has('lobby-destroy')){
        SSEListeners.set('lobby-destroy', lobbyDestroyed);
        sse.addEventListener('lobby-destroy', lobbyDestroyed);
    }
}


async function lobbyInit() {
    await indexInit(false);
    code = window.location.pathname.split('/')[2];
    if (window.location.pathname === '/') return;
    initLobbySSEListeners();
    loadCSS('/css/lobby.css', false);
    try {
        lobby = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`, 'GET');
        if (lobby.code && lobby.code != code && code !== undefined)
            throw {code:404};
        if (lobby.code && code === undefined)
            await navigateTo(`/lobby/${lobby.code}`, false);
        if (lobby.code) {
            code = lobby.code;
            matchType = lobby.match_type;
            document.getElementById('settingsButton').innerText = matchType;
            gameMode = lobby.game_mode === 'clash' ? '3v3': 'Custom Game';
            if (gameMode === '3v3'){
                // document.getElementById('settingsButton').style.display = 'none';
                document.getElementById('teamSelector').style.display = 'none';
            }
            else
                getTeam(lobby);
            document.getElementById('gameType').innerText = gameMode;
            document.getElementById('gameId').innerText = lobby.code;
            await fillPlayerList();
        }
    }
    catch(error){
        try {
            console.log(error);
            if (code === undefined)
                throw {code:404};
            lobby = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/${code}/`, 'POST');
            if (lobby.code) {
                code = lobby.code;
                matchType = lobby.match_type;
                document.getElementById('settingsButton').innerText = matchType;
                // document.getElementById('settingsButton').style.display = 'none';
                gameMode = lobby.game_mode === 'clash' ? '3v3': 'Custom Game';
                if (gameMode === '3v3'){
                    // document.getElementById('settingsButton').style.display = 'none';
                    document.getElementById('teamSelector').style.display = 'none';
                }
                else{
                    getTeam(lobby);
                }
                document.getElementById('gameType').innerText = gameMode;
                document.getElementById('gameId').innerText = lobby.code;
                await fillPlayerList();
            }
            if (lobby.detail === 'Lobby is full.')
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