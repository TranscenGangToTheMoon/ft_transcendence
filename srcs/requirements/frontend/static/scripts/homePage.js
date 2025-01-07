
document.getElementById('ranked').addEventListener('click', async event => {
    await navigateTo('/game/ranked');
})

document.getElementById('duel').addEventListener('click', async event => {
    await navigateTo('/game/duel');
})

document.getElementById('clash').addEventListener('click', async event => {
    event.preventDefault();
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

document.getElementById('chat').addEventListener('click', async ()=> {
    if (!userInformations.is_guest)
        await navigateTo('/chat');
    // console.log('chat');
    // await loadChatsListModal();
})

async function homePageInit() {
    await indexInit(false);
}

homePageInit();