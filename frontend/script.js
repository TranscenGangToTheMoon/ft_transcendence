const baseAPIUrl = "http://localhost:8000/api"
let guestLogin = undefined;

function apiRequest(token, endpoint, callback, method="GET", authType="Bearer",
    contentType="application/json", errorHandling=error=>console.log(error), body=undefined){ 
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
    fetch(endpoint, options)
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => errorHandling(error))
}

document.addEventListener('DOMContentLoaded', event => {
    apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, data => {
        localStorage.setItem('token', data.access)
        localStorage.setItem('refresh', data.refresh)
    }, "POST")
    fillGuestPlaceHolder();
})

function fillGuestPlaceHolder(){
    const guestLoginField = document.getElementById('guestLoginField');
    apiRequest(localStorage.getItem('token'), `${baseAPIUrl}/auth/verify/`, data => {
        guestLoginField.placeholder = data.username;
    })
}

document.getElementById('playDuel').addEventListener('click', event => {
    event.preventDefault(); //todo modify guest login 
})

document.getElementById('playClash').addEventListener('click', event => {
    event.preventDefault(); //todo modify guest login 
})

document.getElementById('switchButton').addEventListener('click', event => {
    event.preventDefault();
    const loginButton = document.getElementById("loginButton");
    if (loginButton.innerText === "Register"){
        loginButton.innerText = "Login";
        event.target.innerText = "New? Create an account"
    }
    else{
        loginButton.innerText = "Register";
        event.target.innerText = "Already have an account? log in"
    }
})

document.getElementById("loginButton").addEventListener('click', event => {
    event.preventDefault();
    const loginButton = document.getElementById("loginButton");
    const usernameField = document.getElementById('usernameLogin');
    const passwordField = document.getElementById('passwordLogin');
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
    apiRequest(localStorage.getItem('token'), endpoint, data => {
        console.log(data);
        if (data.access){
            localStorage.setItem('token', data.access);
            localStorage.setItem('refresh', data.refresh);
            document.getElementById('container').innerText = 'sucess';
        }
        if (data.username) {
            document.getElementById('container').innerText = data.username[0];
            usernameField.style = "background-color:red;"
        }
        if (data.password) {
            document.getElementById('container').innerText = data.username[0];
            passwordField.style = "background-color:red;"
        }
        if (data.detail) {
            document.getElementById('container').innerText = data.detail;
        }
    }, method, undefined, undefined, error=>{
        document.getElementById('container').innerText = error;
    }, userInfo)
})