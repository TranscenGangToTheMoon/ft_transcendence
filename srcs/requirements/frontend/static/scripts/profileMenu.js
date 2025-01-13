document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    clearCSS();
    await closeGameConnection(window.location.pathname);
    clearFriendRequests();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    handleRoute();
    sse.close();
    initSSE();
})

function clearFriendRequests(){
    document.getElementById('friendRequests').innerHTML = '';
    document.getElementById('sentFriendRequests').innerHTML = '';
    document.getElementById('friendSearched').value = '';
}

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