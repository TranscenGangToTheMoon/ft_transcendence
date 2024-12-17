
document.getElementById('ranked').addEventListener('click', async event => {
    await navigateTo('/game/ranked');
})

document.getElementById('duel').addEventListener('click', async event => {
    await navigateTo('/game/duel');
})

document.getElementById('chat').addEventListener('click', async event => {
    await navigateTo('/chat');
})

async function homePageInit() {
    await indexInit(false);
}

homePageInit();