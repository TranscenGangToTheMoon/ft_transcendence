async function checkAuthentication(){
    if (!getAccessToken())
        await generateGuestToken();
}

document.getElementById('logoutButton').addEventListener('click', () => {
    relog();
})

document.getElementById('testRefresh').addEventListener('click', event => {
    event.preventDefault();
    getDataFromApi(localStorage.getItem('token'), `${baseAPIUrl}/users/me/`)
    .then (data => {
        console.log(data);
    })
    .catch (error => {
        console.log( error);
    })
})

function printDebug(){
    document.getElementById('debugLoggedInfo').innerText = `(logged as ${userInformations.username})`;
}

document.getElementById('delete').addEventListener('click', event => {
    event.preventDefault();
    console.log('delete');
    removeTokens();
})

// NAVIGAtORS

// document.getElementById('duel').addEventListener('click', event => {
//     navigateTo
// })

async function atStart() {
    await fetchUserInfos();
    checkAuthentication();
    printDebug();
}

atStart();