document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    handleRoute();
})

document.getElementById('chats').addEventListener('click', async event => {
    event.preventDefault();
    await navigateTo('/chat');
})

document.getElementById('menuLeaderBoard').addEventListener('click', async event => {
    event.preventDefault();
    event.stopImmediatePropagation();
    event.stopPropagation();
})

document.getElementById('settings').addEventListener('click', async event => {
    event.preventDefault();
    await navigateTo('/profile');
})