const baseAPIUrl = "https://localhost:4443/api"
const baseAPIUrlusers = "https://localhost:4443/api/users"

window.baseAPIUrl = baseAPIUrl;
window.baseAPIUrlusers = baseAPIUrlusers;

function apiRequest(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined, currentlyRefreshing=false){ 
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
    // console.log(endpoint, options)
    return fetch(endpoint, options)
        .then(async response => {
            let data = await response.json();
            if (data.code === 'token_not_valid') {
                if (currentlyRefreshing)
                    return {};
                token = await refreshToken(token);
                if (token) {
                    console.log('done, reposting request');
                    return apiRequest(token, endpoint, method, authType, contentType, body);
                }
            }
            return data;
        })
        .catch(error =>{
            throw error;
        })
}

function relog() {
    removeTokens();
    navigateTo('/login');
}

async function reloadTempToken() {
    let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST')
    if (data.access){
        localStorage.setItem('temp_token', data.access);
        return data.access;
    }
    else
        console.log('error a gerer', data);
}

async function refreshToken(token) {
    var refresh = getRefreshToken();
    try {
        console.log('token expired. refreshing.')
        let data = await apiRequest(token, `${baseAPIUrl}/auth/refresh/`, 'POST', undefined, undefined, {'refresh':refresh}, true)
        if (data.access) {
            token = data.access;
            localStorage.setItem(getAccessToken(true), token);
            // localStorage.setItem(getRefreshToken(true), token);
            return token;
        }
        else {
            if (getAccessToken(true) === 'temp_token'){
                return reloadTempToken();
            }
            console.log('refresh token expired must relog')
            relog();
            return undefined;
        }
    }
    catch (error) {
        console.log("ERROR", error);
    }
}

async function getDataFromApi(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined){
    try {
        let data = await apiRequest(token, endpoint, method, authType, contentType, body);
        return data;
    }
    catch (error) {
        throw error;
    }
}

function getAccessToken(name = false) {
    let token = localStorage.getItem('token');
    if (!token){
        token = localStorage.getItem('temp_token');
        if (name && token)
            return 'temp_token';
        else if (name)
            return '';
    }
    else if (name)
        return 'token';
    return token;
}

function getRefreshToken(name = false) {
    let token = localStorage.getItem('refresh');
    if (!token){
        if (name)
            return 'temp_refresh';
        token = localStorage.getItem('temp_refresh');
    }
    else if (name)
        return 'refresh';
    return token;
}

function removeTokens() {
    localStorage.removeItem(getAccessToken(true));
    localStorage.removeItem(getRefreshToken(true));
}

function untemporizeTokens() {
    localStorage.setItem('token', localStorage.getItem('temp_token'));
    localStorage.setItem('refresh', localStorage.getItem('temp_refresh'));
    localStorage.removeItem('temp_refresh');
    localStorage.removeItem('temp_token');
}

window.apiRequest = apiRequest;
window.getDataFromApi = getDataFromApi;
window.removeTokens = removeTokens;
window.untemporizeTokens = untemporizeTokens;
window.refreshToken = refreshToken;
window.getAccessToken = getAccessToken;
window.getRefreshToken = getRefreshToken;


function loadScript(scriptSrc) {
    const script = document.createElement('script');
    script.src = scriptSrc;
    script.onload = () => {
        console.log(`Script ${scriptSrc} loaded.`);
    };
    script.onerror = () => {
        console.error(`Error while loading script ${scriptSrc}.`);
    };
    document.body.appendChild(script);
}

async function loadContent(url) {
    const contentDiv = document.getElementById('content');

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Page non trouvée');
        }
        const html = await response.text();
        contentDiv.innerHTML = html;

        const script = contentDiv.querySelector('[script]');
        if (script)
            loadScript(script.getAttribute('script'));
    } catch (error) {
        contentDiv.innerHTML = '<h1>Erreur 404 : Page non trouvée</h1>';
    }
}

function navigateTo(url, doNavigate=true){
    history.pushState(null, null, url);
    if (doNavigate)
        handleRoute();
}

window.navigateTo = navigateTo;

function handleRoute() {
    const path = window.location.pathname;

    const routes = {
        '/login': '/authentication.html',
        '/': '/homePage.html'
    };

    const page = routes[path] || '/404.html';
    loadContent(page);
}

document.addEventListener('click', event => {
    if (event.target.matches('[data-link]')) {
        event.preventDefault();
        navigateTo(event.target.href);
    }
});

// window.addEventListener('popstate', handleRoute);

handleRoute();
