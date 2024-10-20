
// let guestLogin = undefined;

function changePlayFieldValue(login){
    const playLoginField = document.getElementById("playLoginField");
    playLoginField.value = login;
}

function loadGuest() {
    if (localStorage.getItem('token')){
        return navigateTo('/');
    }
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
        .catch(error => console.log('error a gerer1', error))
}

function fillGuestPlaceHolder(){
    const guestLoginField = document.getElementById('playLoginField');
    getDataFromApi(getAccessToken(), `${baseAPIUrlusers}/me/`)
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
    event.preventDefault(); //todo modify guest login
    guestUsername = document.getElementById('playLoginField').value;
    if (!guestUsername)
    {
        untemporizeTokens();
        return navigateTo()
    }
    if (guestUsername) {
        try {
            let data = await apiRequest(localStorage.getItem('temp_token'), `${baseAPIUrlusers}/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            if (data.password)
                console.log('erreur de backend mais normalement ca marche')
            console.log(data);
            untemporizeTokens();
        }
        catch (error){
            console.log('error on guest change', error);
        }
    } 
})

document.getElementById('playClash').addEventListener('click', async event => {
    event.preventDefault(); //todo modify guest login 
    guestUsername = document.getElementById('playLoginField').value;
    if (!guestUsername)
    {
        untemporizeTokens();
        return navigateTo()
    }
    if (guestUsername) {
        try {
            let data = await apiRequest(localStorage.getItem('temp_token'), `${baseAPIUrlusers}/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            console.log(data);
            if (data.password)
                console.log('erreur de backend mais normalement ca marche')
            untemporizeTokens();
        }
        catch (error){
            console.log('error on guest change', error);
        }
    } 
})

document.getElementById('switchButton').addEventListener('click', event => {
    event.preventDefault();
    const loginButton = document.getElementById("loginButton");
    if (loginButton.innerText === "Register"){
        loginButton.innerText = "Login";
        event.target.innerText = "New? Create an account"
        navigateTo("login", false);
    }
    else{
        loginButton.innerText = "Register";
        event.target.innerText = "Already have an account? log in"
        navigateTo("#", false);
    }
})

document.getElementById("loginButton").addEventListener('click', event => {
    event.preventDefault();
    const loginButton = document.getElementById("loginButton");
    const usernameField = document.getElementById('usernameLogin');
    const passwordField = document.getElementById('passwordLogin');
    usernameField.style = 'none';
    passwordField.style = 'none';
    const userInfo = {
        'username': usernameField.value,
        'password': passwordField.value
    }
    let endpoint;
    let method;
    if (loginButton.innerText === "Login") {
        endpoint = `${baseAPIUrl}/auth/login/`;
        method = 'POST';
    }
    else {
        endpoint = `${baseAPIUrl}/auth/register/`;
        method = 'PUT';
    }
    getDataFromApi(getAccessToken(), endpoint, method, undefined, undefined, userInfo)
        .then (data => {
            console.log(data)
            if (data.access){
                removeTokens();
                localStorage.setItem('token', data.access);
                localStorage.setItem('refresh', data.refresh);
                return navigateTo('/');
            }
            if (data.username) {
                document.getElementById('container').innerText = data.username[0];
                usernameField.style = "background-color:red;"
            }
            if (data.password) {
                console.log(data)
                document.getElementById('container').innerText = data.password[0];
                passwordField.style = "background-color:red;"
            }
            if (data.detail) {
                document.getElementById('container').innerText = data.detail;
            }
            else
                console.log('error a gerer', data);
        })
        .catch(error => console.log('error a gerer1', error))
})

document.getElementById('deleteCredentials').addEventListener('click', event => {
    event.preventDefault();
    removeTokens();
    loadGuest();
})

loadGuest();