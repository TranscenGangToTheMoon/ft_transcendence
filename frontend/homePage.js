const baseAPIUrl = "http://localhost:8000/api"
const baseAPIUrlusers = "http://localhost:8005/api/users"
let guestLogin = undefined;

function apiRequest(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined){ 
    let options = {
        method: method,
        headers: {
            "content-type": contentType
        }
    }
    if (token)
        options.headers["Authorization"] = `${authType} ${token}`;
    if (body)
        options.body = JSON.stringify(body);
    console.log(endpoint, options)
    return fetch(endpoint, options)
        .then(response => {
            return response.json();
        })
        .catch(error =>{
            throw error;
        })
}

function removeTokens(temp=false) {
    if (temp)
    {
        localStorage.removeItem('temp_token');
        localStorage.removeItem('temp_refresh');
    }
    else{
        localStorage.removeItem('token');
        localStorage.removeItem('refresh');
    }
}

function untemporizeTokens() {
    localStorage.setItem('token') = localStorage.getItem('temp_token');
    localStorage.setItem('refresh') = localStorage.getItem('temp_refresh');
    removeTokens(true);
}

function changePlayFieldValue(login){
    const playLoginField = document.getElementById("playLoginField");
    playLoginField.value = login;
}

async function getDataFromApi(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined){
    try {
        let data = await apiRequest(token, endpoint, method, authType, contentType, body);
        return data;
    }
    catch (error) {
        console.log(error);
        throw error;
    }
}

function loadGuest() {
    if (localStorage.getItem('token')){
        document.getElementById('not-logged').classList.add('hidden');
        document.getElementById('logged').classList.remove('hidden');
        return;
    }
    document.getElementById('logged').classList.add('hidden');
    if (localStorage.getItem('temp_token'))
        return fillGuestPlaceHolder();
    getDataFromApi(undefined, `${baseAPIUrl}/auth/guest/`, "POST")
        .then(data => {
            if (data.access) {
                localStorage.setItem('temp_refresh', data.refresh);
                localStorage.setItem('temp_token', data.access);
                fillGuestPlaceHolder();
            }
            else
                console.log('error a gerer', data);
        })
        .catch(error => {
            console.log('error a gerer1', error);
        })
}

function fillGuestPlaceHolder(){
    const guestLoginField = document.getElementById('playLoginField');
    getDataFromApi(localStorage.getItem('temp_token'), `${baseAPIUrlusers}/me/`)
        .then(data => {
            console.log(data);
            if (data.username)
                guestLoginField.placeholder = data.username;
            else if (data.detail)
                console.log('Error: ', data.detail);
        })
        .catch(error => {
            console.log('error a gerer1', error);
        })
}

document.getElementById('playDuel').addEventListener('click', async event => {
    event.preventDefault(); //todo modify guest login
    guestUsername = document.getElementById('playLoginField').value;
    if (guestUsername) {
        try {
            let data = await apiRequest(localStorage.getItem('temp_token'), `${baseAPIUrlusers}/me/`, "PATCH",
            undefined, undefined, {'username' : guestUsername});
            console.log(data);
            untemporizeTokens();
        }
        catch (error){
            console.log('error on guest change', error);
        }
    } 
})

document.getElementById('playClash').addEventListener('click', event => {
    event.preventDefault(); //todo modify guest login 
})

document.getElementById('logoutButton').addEventListener('click', event => {
    document.getElementById('not-logged').classList.remove('hidden');
    document.getElementById('logged').classList.add('hidden');
    getDataFromApi(undefined, `${baseAPIUrl}/auth/guest/`, "POST")
        .then(data => {
            if (data.access) {
                removeTokens();
                localStorage.setItem('temp_refresh', data.refresh);
                localStorage.setItem('temp_token', data.access);
                fillGuestPlaceHolder();
            }
            else
                console.log('error a gerer', data);
        })
        .catch(error => {
            console.log('error a gerer1', error);
        })
})

document.getElementById('switchButton').addEventListener('click', event => {
    event.preventDefault();
    const loginButton = document.getElementById("loginButton");
    if (loginButton.innerText === "Register"){
        loginButton.innerText = "Login";
        event.target.innerText = "New? Create an account"
        navigateTo("/", false);
    }
    else{
        loginButton.innerText = "Register";
        event.target.innerText = "Already have an account? log in"
        navigateTo("#", false);
    }
})

function loginSuccess() {
    removeTokens(true);
    document.getElementById('not-logged').classList.add('hidden');
    document.getElementById('logged').classList.remove('hidden');
    getDataFromApi(localStorage.getItem('token'), `${baseAPIUrlusers}/me/`)
        .then(data => {
            console.log('data received : ', data);
            var username = data.username;
            document.getElementById('debugLoggedInfo').innerText = `<h1>page de jeu</h1> (logged as: ${username})`;
        })
        .catch(error => console.log('error a gerer', error));
}

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
    getDataFromApi(localStorage.getItem('token'), endpoint, method, undefined, undefined, userInfo)
        .then(data => {
            if (data.access){
                localStorage.setItem('token', data.access);
                localStorage.setItem('refresh', data.refresh);
                return loginSuccess();
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
        .catch(error => console.log('error a gerer1', error));
})

loadGuest();