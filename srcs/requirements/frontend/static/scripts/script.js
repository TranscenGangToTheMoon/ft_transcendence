// ========================== GLOBAL VALUES ==========================

const MAX_DISPLAYED_NOTIFICATIONS = 3;
const baseAPIUrl = "https://localhost:4443/api"
let userInformations = undefined;
var notificationIdentifier = 0;
var displayedNotifications = 0;
window.baseAPIUrl = baseAPIUrl;
window.userInformations = userInformations;

// ========================== API REQUESTS ==========================

async function apiRequest(token, endpoint, method="GET", authType="Bearer",
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
    console.log(endpoint, options);
    return fetch(endpoint, options)
        .then(async response => {
            if (!response.ok && (response.status > 499 || response.status === 404)){
                throw {code: response.status};
            }
            if (response.status === 204){
                return;
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

async function relog() {
    removeTokens();
    await navigateTo('/login');   
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

async function loadContent(url, container='content', append=false) {
    const contentDiv = document.getElementById(container);
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Page non trouvée');
        }
        const html = await response.text();
        if(!append)
            contentDiv.innerHTML = html;
        else
            contentDiv.innerHTML += html;
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

async function navigateTo(url, doNavigate=true){
    history.pushState({}, '', url);
    console.table(history)
    if (doNavigate)
        await handleRoute();
}

window.navigateTo = navigateTo;

async function handleRoute() {
    const path = window.location.pathname;

    const routes = {
        '/login': '/authentication.html',
        '/': '/homePage.html',
        '/profile' : 'profile.html',
        '/lobby' : '/lobby.html',
        '/chat' : '/testChat.html'
    };

    const page = routes[path] || '/404.html';
    await loadContent(page);
}

// UNCOMMENT FOR LINKS TO WORK WITHOUT CUSTOM JS
// document.addEventListener('click', event => {
//     if (event.target.matches('[data-link]')) {
//         event.preventDefault();
//         await navigateTo(event.target.href);
//     }
// });

window.addEventListener('popstate', async event => {
    event.preventDefault();
    document.querySelectorAll('.modal.show').forEach(modal => {
        bootstrap.Modal.getInstance(modal).hide();
    })
    if (userInformations.is_guest !== (document.getElementById('trophies') === '')){
        await loadUserProfile();
    }
    handleRoute();
})

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
    document.getElementById('errorModal').addEventListener('shown.bs.modal', function() {
        document.getElementById('errorModalClose').focus();
    })
    errorModal.show();
}

window.displayMainError = displayMainError;

// ========================== INDEX SCRIPT ==========================

async function loadFriendListModal() {
    await loadContent('/friendList.html', 'modals', true);
}

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

document.getElementById('home').addEventListener('click', async event => {
    event.preventDefault();
    await navigateTo('/');
})

function initSSE(){
    console.log('SERVER SENT EVENT INITIALIZATION HERE');
}

async function  indexInit(auto=true) {
    if (!auto){
        await fetchUserInfos();
        if (window.location.pathname === '/login'){
            document.getElementById('profileMenu').innerHTML = "";
        }
        else{
            await loadUserProfile();
        }
        if (userInformations.code === 'user_not_found'){
            console.log('user was deleted from database, switching to guest mode');
            displayMainError("Unable to retrieve your account/guest profile","We're sorry your account has been permanently deleted and cannot be recovered.");
            await generateToken();
            await fetchUserInfos(true);
            await loadUserProfile();
        }
    }
    else{
        loadCSS('/css/styles.css', false);
        await loadFriendListModal();
        initSSE();
        handleRoute();
    }
}

document.getElementById('notifTrigger').addEventListener('click', async event => {
    event.preventDefault();
    if (displayedNotifications >= MAX_DISPLAYED_NOTIFICATIONS) {
        return ;
    }
    const toastContainer = document.getElementById('toastContainer');

    if (document.querySelector('hide'))
        console.log('la');
    await loadContent('/notification.html', 'toastContainer', true);
    const notification = document.getElementById('notification');
    notification.id = `notification${notificationIdentifier}`;
    const toastInstance = new bootstrap.Toast(notification);
    toastInstance.show();
    notificationIdentifier++;
    displayedNotifications++;
    setTimeout(() => {
        toastInstance.hide();
        setTimeout (() => {
            displayedNotifications--;
            toastContainer.removeChild(document.getElementById(notification.id));
        }, 500);
    }, 5000);
})

window.indexInit = indexInit;
window.loadUserProfile = loadUserProfile;

indexInit();