// ========================== GLOBAL VALUES ==========================

const baseAPIUrl = "https://localhost:4443/api"
let userInformations = undefined;
window.baseAPIUrl = baseAPIUrl;
window.userInformations = userInformations;

// ========================== API REQUESTS ==========================

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
    console.log(endpoint, options)
    return fetch(endpoint, options)
        .then(async response => {
            if (!response.ok && (response.status > 499 || response.status === 404)){
                throw {code: response.status};
            }
            let data = await response.json();
            console.log(data);
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
            if (error.code || error.message === 'Failed to fetch')
                document.getElementById('container').innerText = `alala pas bien ${error.code? `: ${error.code}` : ''} (jcrois c'est pas bon)`;
            throw error;
        })
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

window.apiRequest = apiRequest;
window.getDataFromApi = getDataFromApi;
    
// ========================== TOKEN UTILS ==========================
async function forceReloadGuestToken() {
    try {
        let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST')
        if (data.access){
            localStorage.setItem('token', data.access);
            return data.access;
        }
        else
            console.log('error a gerer', data);
    }
    catch (error) {
        console.log('error a gerer', error);
    }
}

async function generateToken() {
    try {
        let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, "POST");
        if (data.access) {
            localStorage.setItem('token', data.access);
            localStorage.setItem('refresh', data.refresh);
        }
        else
            console.log('error a gerer', data);
    }
    catch(error){
        console.log('error a gerer', error)
    }
}

async function refreshToken(token) {
    var refresh = getRefreshToken();
    try {
        console.log('token expired. refreshing.')
        let data = await apiRequest(token, `${baseAPIUrl}/auth/refresh/`, 'POST', undefined, undefined, {'refresh':refresh}, true)
        if (data.access) {
            token = data.access;
            localStorage.setItem('token', token);
            // localStorage.setItem('refresh', token);
            return token;
        }
        else {
            if (userInformations.is_guest === true){
                return forceReloadGuestToken();
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

function getAccessToken() {
    return localStorage.getItem('token');
}

function getRefreshToken(name = false) {
    return localStorage.getItem('refresh');
}

function removeTokens() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
}

function relog() {
    removeTokens();
    navigateTo('/login');   
}
window.removeTokens = removeTokens;
window.refreshToken = refreshToken;
window.getAccessToken = getAccessToken;
window.getRefreshToken = getRefreshToken;
window.generateToken = generateToken;

// ========================== SPA SCRIPTS ==========================

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

function loadCSS(cssHref, toUpdate=true) {
    const existingLink = document.querySelector('link[dynamic-css]');
    if (existingLink) {
        existingLink.remove();
    }
    // console.log('will update =', toUpdate);
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = cssHref;
    if (toUpdate)
        link.setAttribute('dynamic-css', 'true');
    document.head.appendChild(link);
    console.log(`Style ${cssHref} loaded.`)
}

async function loadContent(url, container='content') {
    const contentDiv = document.getElementById(container);
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
        let style;
        if (!userInformations || !userInformations.is_guest)
            style = '_style'
        else if (userInformations.is_guest)
            style = 'guestStyle'
        css = contentDiv.querySelector(`[${style}]`);
        if (css)
            loadCSS(css.getAttribute(style), !css.getAttribute(style).includes('Guest'));
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
        '/': '/homePage.html',
        '/profile' : 'profile.html'
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

window.loadContent = loadContent;

// ========================== OTHER UTILS ==========================

async function fetchUserInfos(forced=false) {
    if (!getAccessToken())
        await generateToken();
    if (!userInformations || forced) {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me`);
            userInformations = data;
        }
        catch (error) {
            console.log(error);
        }
    }
}

function displayMainError(errorTitle, errorContent) {
    const errorContentDiv = document.getElementById('errorContent');
    const errorTitleDiv = document.getElementById('errorModalLabel');
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));

    errorContentDiv.innerText = errorContent;
    errorTitleDiv.innerText = errorTitle;
    errorModal.show();
}

// ========================== INDEX SCRIPT ==========================

async function loadUserProfile(){
    let profileMenu = 'profileMenu.html';

    document.getElementById('username').innerText = userInformations.username;
    if (userInformations.is_guest){
        profileMenu = 'guestProfileMenu.html'
        document.getElementById('trophies').innerText = "";
        document.getElementById('balance').innerText = "";
    }
    else {
        document.getElementById('trophies').innerText = userInformations.trophies;
        document.getElementById('balance').innerText = userInformations.coins;
    }
    await loadContent(`/${profileMenu}`, 'profileMenu');
    // document.getElementById('title').innerText = userInformations.title;
}

async function atStart() {
    loadCSS('/css/styles.css', false);
    await fetchUserInfos();
    if (userInformations.code === 'user_not_found'){
        console.log('user was deleted from database, switching to guest mode');
        displayMainError("Unable to retrieve your account/guest profile","We're sorry your account has been permanently deleted and cannot be recovered.");
        await generateToken();
        await fetchUserInfos(true);
    }
    handleRoute();
}

window.loadUserProfile = loadUserProfile;

atStart();