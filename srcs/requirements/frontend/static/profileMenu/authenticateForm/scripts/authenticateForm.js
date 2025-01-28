document.getElementById('switchButton').addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
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
    event.stopPropagation();
    event.stopImmediatePropagation();
    const loginButton = document.getElementById("loginButton");
    const usernameField = document.getElementById('usernameLogin');
    const passwordField = document.getElementById('passwordLogin');
    const contextErrorDiv = document.getElementById('loginFormContextError');
    contextErrorDiv.classList.add('d-none');
    usernameField.classList.remove('is-invalid');
    passwordField.classList.remove('is-invalid');
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
        endpoint = `${baseAPIUrl}/auth/register/guest/`;
        method = 'PUT';
    }
    getDataFromApi(getAccessToken(), endpoint, method, undefined, undefined, userInfo)
        .then (async data => {
            if (data.access){
                await closeGameConnection(window.location.pathname);
                clearCSS();
                removeTokens();
                if (typeof sse !== 'undefined')
                    sse.close();
                localStorage.setItem('token', data.access);
                localStorage.setItem('refresh', data.refresh);
                initSSE();
                await fetchUserInfos(true);
                loadUserProfile();
                handleRoute();
                if (document.getElementById('friendListModal').clicked)
                    addFriendListListener();
                return;
            }
            if (data.username) {
                const feedbackDiv = usernameField.parentElement.querySelector('.invalid-feedback');
                feedbackDiv.innerText = data.username[0];
                usernameField.classList.add('is-invalid');
            }
            if (data.password) {
                const feedbackDiv = passwordField.parentElement.querySelector('.invalid-feedback');
                feedbackDiv.innerText = data.password[0];
                passwordField.classList.add('is-invalid');
            }
            if (data.detail) {
                const feedbackDiv = passwordField.parentElement.querySelector('.invalid-feedback');
                feedbackDiv.innerText = data.detail;
                usernameFeedback = usernameField.parentElement.querySelector('.invalid-feedback');
                usernameFeedback.innerText = '';
                usernameField.classList.add('is-invalid');
                passwordField.classList.add('is-invalid');
            }
            else
                console.log('error', data);
        })
        .catch(error => console.log('error', error))
})
