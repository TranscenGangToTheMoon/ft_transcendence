
async function playRanked(){
    await navigateTo('/game/ranked');
}

async function playDuel(){
    await navigateTo('/game/duel');
}

async function playClash(event) {
    event.preventDefault();
    if (userInformations.is_guest){
        document.getElementById('lobbyCodeContextError').innerText = '';
        const lobbyCodeSelectionForm = new bootstrap.Modal(document.getElementById('lobbyCodeModal'));
        lobbyCodeSelectionForm.show();
        async function handleInput(event){
            event.preventDefault();
            let code = document.getElementById('lobbyCodeInput').value;
            if (code.length != 4 || isNaN(parseInt(code)))
                return document.getElementById('lobbyCodeContextError').innerText = 'This is not a valid code.';
            bootstrap.Modal.getOrCreateInstance(document.getElementById('lobbyCodeModal')).hide();
            setTimeout(async ()=> {
                await navigateTo(`/lobby/${code}`);
            }, 100);
        }
        document.getElementById('joinLobbyByCode').addEventListener('click', handleInput);
        return;
    }
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`, 'POST', undefined, undefined, {
            'game_mode' : 'clash',
        }, undefined, true);
        if (data.code)
            await navigateTo(`/lobby/${data.code}`);
        console.log(data);
    }
    catch (error){
        console.log(error);
    }
}

async function playCustomGame(event){
    event.preventDefault();
    if (userInformations.is_guest){
        document.getElementById('lobbyCodeContextError').innerText = '';
        const lobbyCodeSelectionForm = new bootstrap.Modal(document.getElementById('lobbyCodeModal'));
        lobbyCodeSelectionForm.show();
        async function handleInput(event){
            event.preventDefault();
            let code = document.getElementById('lobbyCodeInput').value;
            if (code.length != 4 || isNaN(parseInt(code)))
                return document.getElementById('lobbyCodeContextError').innerText = 'This is not a valid code.';
            bootstrap.Modal.getOrCreateInstance(document.getElementById('lobbyCodeModal')).hide();
            setTimeout(async ()=> {
                await navigateTo(`/lobby/${code}`);
            }, 100);
        }
        document.getElementById('joinLobbyByCode').addEventListener('click', handleInput);
        return;
    }
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/lobby/`, 'POST', undefined, undefined, {
            'game_mode' : 'custom_game',
        }, undefined, true);
        if (data.code)
            navigateTo(`/lobby/${data.code}`);
    }
    catch(error){
        console.log(error);
    }
}

async function playTournament(){
    await navigateTo('/tournament');
}

async function playLocal(){
    await navigateTo('/game/local');
}

async function spectate(){
    await navigateTo('/spectate');
}

document.getElementById('chat').addEventListener('click', async e => {
	e.preventDefault();
    await displayChatsList();
});

document.getElementById('playGame').addEventListener('click', async e => {
    const gameModeFunctions = [playLocal, playDuel, playRanked, playClash, playCustomGame, playTournament, spectate];
    const selectorValue = document.getElementById('gameModeSelect').value;

    await gameModeFunctions[selectorValue](e);
})

function forPhoneChanges(){
    try {
        document.getElementById('customGame').style.display = 'none';
        document.getElementById('clash').style.display = 'none';
    }
    catch(error){
        document.getElementById('container').innerText = error;
    }
}

async function homePageInit() {
    await indexInit(false);
    if (window.matchMedia("(hover: none) and (pointer: coarse)").matches)
        forPhoneChanges();
}

homePageInit();