
// let guestLogin = undefined;

function changePlayFieldValue(login){
    const playLoginField = document.getElementById("playLoginField");
    playLoginField.value = login;
}

function loadGuest() {
    if (!getAccessToken())
        generateToken();
    fillGuestPlaceHolder();
}
    
function fillGuestPlaceHolder(){
    const guestLoginField = document.getElementById('playLoginField');
    guestLoginField.placeholder = userInformations.username;
    // getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/`)
    //     .then (data => {
    //         if (data.username)
    //             guestLoginField.placeholder = data.username;
    //         else if (data.detail)
    //             console.log('Error: ', data.detail);
    //     })
    // .catch(error => console.log('error a gerer', error))
}

document.getElementById('playDuel').addEventListener('click', async event => {
    event.preventDefault();
    guestUsername = document.getElementById('playLoginField').value;
    if (!guestUsername && getAccessToken())
        return await navigateTo('/');
    if (guestUsername) {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            if (!data.id)
                document.getElementById('container').innerText = data.username;
            else{
                await navigateTo('/');
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
    if (!guestUsername && getAccessToken())
        return await navigateTo('/');
    if (guestUsername) {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            if (!data.id)
                document.getElementById('container').innerText = data.username;
            else {
                await navigateTo('/');
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

function removeDropdown() {
    document.querySelector('.dropdown').remove();
}

async function authInit(){
    await indexInit(false);
    if (!userInformations.is_guest) {
        await navigateTo('/');
        return; //TODO replace with URI or maybe not
    }
    document.getElementById('username').innerText = userInformations.username;
    await loadContent('/authenticationForm.html', 'authentication');
    loadGuest();
}

authInit();