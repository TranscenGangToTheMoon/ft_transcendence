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
        method = 'POST';
    }
    getDataFromApi(getAccessToken(), endpoint, method, undefined, undefined, userInfo)
        .then (async data => {
            if (data.access){
                removeTokens();
                localStorage.setItem('token', data.access);
                localStorage.setItem('refresh', data.refresh);
                await fetchUserInfos(true);
                loadUserProfile();
                if (window.location.pathname.includes('login'))
                    await navigateTo('/');
                else
                    handleRoute();
                return;//todo redirect to uri
            }
            if (data.username) {
                document.getElementById('container').innerText = data.username[0];
                usernameField.style = "background-color:red;"
            }
            if (data.password) {
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
