const loginForm = document.getElementById('login-form');
const container = document.getElementById('container');
const baseEndpoint = "http://localhost:8000/api";
console.log(baseEndpoint);

if (loginForm) {
    console.log("add listener");
    loginForm.addEventListener('submit', handleLogin);
}

function handleLogin(event) {
    console.log('login event: ', event);
    event.preventDefault();

    const loginEndpoint = `${baseEndpoint}/token/`;
    let loginFormData = new FormData(loginForm);
    let loginObjectData = Object.fromEntries(loginFormData);
    console.log(loginObjectData);
    const options = {
        method: "POST",
        headers: {
            "content-type": "application/json",
        },
        body: JSON.stringify(loginObjectData)
    }

    fetch(loginEndpoint, options)
        .then(response => response.json())
        .then(data => {
            handleAuthData(data, getMe)
        })
        .catch(error => console.log(error))
}

function handleAuthData(authData, callback) {
    localStorage.setItem('access', authData.access);
    localStorage.setItem('refresh', authData.refresh);
    callback()
}

function getMe() {
    const meEndpoint = `${baseEndpoint}/users/me/`;
    const options = {
        method: "GET",
        headers: {
            "content-type": "application/json",
            "authorization": `Bearer ${localStorage.getItem('access')}`
        }
    }
    fetch(meEndpoint, options)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            writeToContainer(data);
        })
}

function writeToContainer(data) {
    if (container) {
        container.innerHTML = "<pre>" + JSON.stringify(data, null, 4) + "</pre>";
    }
}
