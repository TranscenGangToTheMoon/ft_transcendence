
// let guestLogin = undefined;

function changePlayFieldValue(login){
    const playLoginField = document.getElementById("playLoginField");
    playLoginField.value = login;
}

function loadGuest() {
    // if (localStorage.getItem('token')){
    //     return navigateTo('/');
    // }
    if (localStorage.getItem('temp_token'))
        return fillGuestPlaceHolder();
    getDataFromApi(undefined, `${baseAPIUrl}/auth/guest/`, "POST")
        .then (data => {
            if (data.access) {
                localStorage.setItem('temp_refresh', data.refresh);
                localStorage.setItem('temp_token', data.access);
                fillGuestPlaceHolder();
            }
            else
                console.log('error a gerer', data);
        })
        .catch(error => console.log('error a gerer', error))
}

function fillGuestPlaceHolder(){
    const guestLoginField = document.getElementById('playLoginField');
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/`)
        .then (data => {
            console.log(data);
        if (data.username)
            guestLoginField.placeholder = data.username;
        else if (data.detail)
            console.log('Error: ', data.detail);
        })
    .catch(error => console.log('error a gerer', error))
}

document.getElementById('playDuel').addEventListener('click', async event => {
    event.preventDefault();
    guestUsername = document.getElementById('playLoginField').value;
    if (!guestUsername && getAccessToken)
    {
        untemporizeTokens();
        return navigateTo();
    }
    if (guestUsername) {
        try {
            let data = await apiRequest(localStorage.getItem('temp_token'), `${baseAPIUrl}/users/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            console.log(data);
            if (!data.id)
                document.getElementById('container').innerText = data.username;
            else {
                untemporizeTokens();
                navigateTo();
            }
        }
        catch (error){
            console.log('error on guest change', error);
        }
    } 
})

document.getElementById('playClash').addEventListener('click', async event => {
    event.preventDefault();
    guestUsername = document.getElementById('playLoginField').value;
    if (!guestUsername && getAccessToken)
    {
        untemporizeTokens();
        return navigateTo();
    }
    if (guestUsername) {
        try {
            let data = await apiRequest(localStorage.getItem('temp_token'), `${baseAPIUrl}/users/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            console.log(data);
            if (!data.id)
                document.getElementById('container').innerText = data.username;
            else {
                untemporizeTokens();
                navigateTo();
            }
        }
        catch (error){
            console.log('error on guest change', error);
        }
    } 
})

document.getElementById('deleteCredentials').addEventListener('click', event => {
    event.preventDefault();
    removeTokens();
    loadGuest();
})

document.getElementById('delete').addEventListener('click', event => {
    event.preventDefault();
    console.log('delete');
    removeTokens();
})

async function atStart(){
    await loadContent('/authenticationForm.html', 'authentication');
    loadGuest();
}

atStart();