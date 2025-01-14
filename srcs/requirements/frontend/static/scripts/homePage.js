
document.getElementById('ranked').addEventListener('click', async event => {
    await navigateTo('/game/ranked');
})

document.getElementById('duel').addEventListener('click', async event => {
    await navigateTo('/game/duel');
})

document.getElementById('clash').addEventListener('click', async event => {
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
        })
        if (data.code)
            await navigateTo(`/lobby/${data.code}`);
        console.log(data);
    }
    catch (error){
        console.log(error);
    }
})

document.getElementById('customGame').addEventListener('click', async event => {
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
        });
        if (data.code)
            navigateTo(`/lobby/${data.code}`);
    }
    catch(error){
        console.log(error);
    }
})

document.getElementById('tournament').addEventListener('click', async event => {
    // try {
        await navigateTo('/tournament');
    // }
    // catch(error){
    //     console.log(error);
    // }
})

document.getElementById('local').addEventListener('click', async () => {
    await navigateTo('/game/local');
})

document.getElementById('chat').addEventListener('click', async e => {
	e.preventDefault();
    await displayChatsList();
});

async function homePageInit() {
    await indexInit(false);
}

homePageInit();