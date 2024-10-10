const baseAPIUrl = "http://localhost:8000/api"
let guestLogin = undefined;

function apiRequest(token, endpoint, callback, method="GET", authType="Bearer", contentType="applications/json"){ 
    let options = {
        method: method,
        headers: {
            "content-type": contentType
        }
    }
    if (token)
        options.headers["Authorization"] = `${authType} ${token}`;
    fetch(endpoint, options)
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => console.log(error))
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
    apiRequest(localStorage.getItem('token'), `${baseAPIUrl}/auth/token/verify/`, data => {
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
    if (loginButton.innerText === "Register")
        loginButton.innerText = "Login";
    else
        loginButton.innerText = "Register";
})

document.getElementById("loginButton").addEventListener('click', event => {
    event.preventDefault();
    const loginButton = document.getElementById("loginButton");
    if (loginButton.innerText === "Login")
        console.log("bite");
    else {
        apiRequest(localStorage.getItem(token), `${baseAPIUrl}/auth/register/`, data => {
            console.log(data);
        }, "POST")
    }
})