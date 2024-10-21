function checkAuthentication(){
    if (getAccessToken(true) !== 'token'){
        navigateTo("/login");
        removeTokens();
        return false;
    }
    return true;
}

document.getElementById('logoutButton').addEventListener('click', () => {
    relog();
})

document.getElementById('testRefresh').addEventListener('click', event => {
    event.preventDefault();
    getDataFromApi(localStorage.getItem('token'), `${baseAPIUrlusers}/me/`)
        .then (data => {
            console.log(data);
        })
        .catch (error => {
            console.log( error);
        })
})

function printDebug(){
    getDataFromApi(getAccessToken(), `${baseAPIUrlusers}/me/`)
        .then(data => {
            if (data.username)
                document.getElementById('debugLoggedInfo').innerText = `(logged as ${data.username})`;
            else console.log('error a gerer', data);
        })
        .catch(error => console.log('error a gerer', error));
}

if (checkAuthentication())
    printDebug();