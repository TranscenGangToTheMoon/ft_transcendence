document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    sse.close();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    initSSE();
    clearCSS();
    clearFriendRequests();
    await closeGameConnection(window.location.pathname);
    handleRoute();
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