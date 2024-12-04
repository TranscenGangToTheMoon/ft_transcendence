document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    handleRoute();
})

document.getElementById('chats').addEventListener('click', async event => {
    event.preventDefault();
    if (pathName === '/game')
        return cancelNavigation(undefined, '/chat');
    await navigateTo('/chat');
})

document.getElementById('settings').addEventListener('click', async event => {
    event.preventDefault();
    if (pathName === '/game')
        return cancelNavigation(undefined, '/profile');
    await navigateTo('/profile');
})