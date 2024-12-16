
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

async function homePageInit() {
    await indexInit(false);
}

homePageInit();