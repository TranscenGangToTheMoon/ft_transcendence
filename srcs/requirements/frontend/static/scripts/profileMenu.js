document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    await closeGameConnection(window.location.pathname());
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    handleRoute();
    sse.close();
    initSSE();
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