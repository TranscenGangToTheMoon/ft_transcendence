
document.getElementById('ranked').addEventListener('click', async event => {
    await navigateTo('/game/ranked');
})

document.getElementById('duel').addEventListener('click', async event => {
    await navigateTo('/game/duel');
})

async function homePageInit() {
    await indexInit(false);
}

homePageInit();