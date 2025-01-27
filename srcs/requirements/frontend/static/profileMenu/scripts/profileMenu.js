async function logOut(){
    sse.close();
    emptyNotificationQueue();
    removeTokens();
    await generateToken();
    await fetchUserInfos(true);
    initSSE();
    clearCSS();
    clearFriendRequests();
    await closeGameConnection(window.location.pathname);
    handleRoute();
}

document.getElementById('logOut').addEventListener('click', async event => {
    event.preventDefault();
    await logOut();
})

function clearFriendRequests(){
    document.getElementById('friendRequests').innerHTML = '';
    document.getElementById('sentFriendRequests').innerHTML = '';
    document.getElementById('friendSearched').value = '';
}

document.getElementById('pMenuChats').addEventListener('click', async event => {
    event.preventDefault();
    if (pathName === '/game'){
        console.log("Error: Can't display chat while in game")
        return cancelNavigation(undefined, '/chat');
    }
    await displayChatsList();
})

document.getElementById('settings').addEventListener('click', async event => {
    event.preventDefault();
    if (pathName === '/game')
        return cancelNavigation(undefined, '/profile');
    await navigateTo('/profile');
})