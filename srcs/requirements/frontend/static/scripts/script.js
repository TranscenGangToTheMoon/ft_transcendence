// ========================== GLOBAL VALUES ==========================

const MAX_DISPLAYED_NOTIFICATIONS = 3;
const MAX_DISPLAYED_FRIENDS = 12;
const MAX_DISPLAYED_FRIEND_REQUESTS = 5;
const MAX_DISPLAYED_BLOCKED_USERS = 10;
const baseAPIUrl = "/api"
let userInformations = undefined;
var sse;
var notificationIdentifier = 0;
var displayedNotifications = 0;
window.baseAPIUrl = baseAPIUrl;
window.userInformations = userInformations;
var pathName = window.location.pathname;
var badgesDivs = {};
var notificationQueue = [];

window.pathName = pathName;

// ========================== API REQUESTS ==========================

async function apiRequest(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined, currentlyRefreshing=false){
    let options = {
        method: method,
        headers: {
            "content-type": contentType
        }
    }
    if (token && endpoint != `${baseAPIUrl}/auth/login/`)
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
            if (error.code === 500 || error.message === 'Failed to fetch')
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

function loadScript(scriptSrc, type) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = scriptSrc;
        if (type)
            script.type = type;
        script.onload = () => {
            // console.log(`Script ${scriptSrc} loaded.`);
            resolve();
        };
        script.onerror = () => {
            console.error(`Error while loading script ${scriptSrc}.`);
            reject(new Error(`Failed to load script ${scriptSrc}`));
        };
        const scripts = document.querySelectorAll('script');
        for (let existingScript of scripts)
            if (existingScript.src === `https://localhost:4443${scriptSrc}`)
                existingScript.remove();
        document.body.appendChild(script);
    });
}

function loadCSS(cssHref, toUpdate=true) {
    const existingLink = document.querySelector('link[dynamic-css]');
    if (existingLink) {
        // console.log('deleted', existingLink);
        existingLink.remove();
    }
    // console.log('will update =', toUpdate);
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = cssHref;
    if (toUpdate)
        link.setAttribute('dynamic-css', 'true');
    document.head.appendChild(link);
    // console.log(`Style ${cssHref} loaded.`)
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
            contentDiv.insertAdjacentHTML('beforeend', `\n${html}`);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const script = tempDiv.querySelector('[script]');
        if (script)
            await loadScript(script.getAttribute('script'), script.getAttribute('type'));
        let style;
        if (!userInformations || !userInformations.is_guest)
            style = '_style'
        else if (userInformations.is_guest)
            style = 'guestStyle'
        css = contentDiv.querySelector(`[${style}]`);
        // console.log(style, css)
        if (css)
            loadCSS(css.getAttribute(style));//, !css.getAttribute(style).includes('Guest'));
    } catch (error) {
        contentDiv.innerHTML = '<h1>Erreur 404 : Page non trouvée</h1>';
    }
}

function containsCode(path){
    const regex = /^\/(game|lobby)\/\d+$/;
    return regex.test(path);
}

async function handleRoute() {
    var path = window.location.pathname;
    if (window.location.pathname !== 'game')
        window.PongGame?.stopGame();
    if (containsCode(path))
        path = "/" + path.split("/")[1];
    const routes = {
        '/login': '/authentication.html',
        '/': '/homePage.html',
        '/profile' : 'profile.html',
        '/lobby' : '/lobby.html',
        '/chat' : '/chatTemplates/chat.html',

        '/game/ranked' : '/game/game.html',
        '/game/duel' : '/game/game.html',
        '/game/custom' : '/game/game.html',
        '/tournament' : '/tournament/tournament.html'
    };

    const page = routes[path] || '/404.html';
    await loadContent(page);
}

let lastState = 0;
if (!localStorage.getItem('currentState'))
    localStorage.setItem('currentState', 0);

function incrementCurrentState(){
    let currentState = localStorage.getItem('currentState');
    currentState++;
    localStorage.setItem('currentState', currentState);
}

function getCurrentState(){
    return localStorage.getItem('currentState');
}

async function navigateTo(url, doNavigate=true){
    let currentState = getCurrentState();
    lastState = currentState;
    history.pushState({state: currentState}, '', url);
    console.log(`added ${url} to history with state : ${currentState}`);
    pathName = window.location.pathname;
    incrementCurrentState();
    if (doNavigate)
        await handleRoute();
}

window.navigateTo = navigateTo;

function confirmPopstate() {
    // const confirmModal = document.getElementById('confirmModal');
    // confirmModal.removeAttribute('style');
    pathName = "";
    if (direction > 0){
        history.forward();
    }
    else{
        history.go(direction);
    }
}

let isUserGoBack = true;
let direction = 0;

function cancelNavigation(event, url, callback=undefined){
    if (!document.querySelectorAll('#confirmModal.show').length)
        displayConfirmModal('Warning', 'You are about to leave this page. This will result in abandoning your current game. Do you want to proceed anyway?')
    if (event){
        if (event.state.state < lastState){
            history.forward();
            direction = -1;
        }
        else{
            history.go(-1);
            direction = 1;
        }
        isUserGoBack = false;
    }
    if (url){
        let currentState = getCurrentState();
        lastState = currentState;
        history.pushState({state: currentState}, '', url);
        console.log(`added ${url} to history with state : ${currentState}`);
        direction = 1;
        history.go(-1);
        incrementCurrentState();
        isUserGoBack = false;
    }
}

window.addEventListener('popstate', async event => {
    console.log(event.state, 'last state:', lastState);
    if (!isUserGoBack)
        return isUserGoBack = true;
    console.log(pathName, window.location.pathname);
    if (pathName === '/game')
        return cancelNavigation(event, undefined);
    pathName = window.location.pathname;
    if (event.state && event.state.state)
        lastState = event.state.state;
    if (userInformations.is_guest !== (document.getElementById('trophies') === '')){
        await loadUserProfile();
    }
    handleRoute();
})

window.loadContent = loadContent;
window.cancelNavigation = cancelNavigation;

// ========================== OTHER UTILS ==========================

async function fetchUserInfos(forced=false) {
    if (!getAccessToken())
        await generateToken();
    if (!userInformations || forced) {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me`);
            userInformations = data;
            console.log(userInformations);
            displayBadges();
        }
        catch (error) {
            console.log(error);
        }
    }
}

function displayBadges(){
    if (userInformations.notifications){
        setTimeout(() => {
            console.log(userInformations.notifications)
            let totalNotifications = 0;
            for (let type in userInformations.notifications){
                if (!userInformations.notifications[type] || type === 'all') continue;
                totalNotifications += userInformations.notifications[type];
                for (let badgeDiv of badgesDivs[type]){
                    addNotificationIndicator(badgeDiv, userInformations.notifications[type]);
                }
            }
            console.log(totalNotifications);
            userInformations.notifications['all'] = totalNotifications;
            if (!totalNotifications) return;
            for (let allBadgesDiv of badgesDivs['all']){
                addNotificationIndicator(allBadgesDiv, totalNotifications);
            }
        }, 70);
    }
}

function removeBadges(type){
    let toDelete = 0;
    userInformations.notifications[type] = 0;
    for (let badgeDiv of badgesDivs[type]){
        let indicator = badgeDiv.querySelector(`.indicator`);
        if (indicator){
            toDelete = parseInt(indicator.innerText);
            console.log(toDelete);
            if (isNaN(toDelete))
                toDelete = 0;
            indicator.remove();
        }
    }
    if (toDelete){
        userInformations.notifications['all'] -= toDelete;
        if (!userInformations.notifications['all']){
            for (let badgeDiv of badgesDivs['all']){
                let indicator = badgeDiv.querySelector(`.indicator`);
                if (indicator)
                    indicator.remove();
            }
        }
        else {
            for (let allBadgesDiv of badgesDivs['all']){
                let indicator = allBadgesDiv.querySelector(`.indicator`);
                if (indicator)
                    indicator.innerText = userInformations.notifications['all'];
            }
        }
    }
}

function displayMainAlert(alertTitle, alertContent) {
    const alertContentDiv = document.getElementById('alertContent');
    const alertTitleDiv = document.getElementById('alertModalLabel');
    const alertModal = new bootstrap.Modal(document.getElementById('alertModal'));

    alertContentDiv.innerText = alertContent;
    alertTitleDiv.innerText = alertTitle;
    alertModal.show();
}

function displayConfirmModal(confirmTitle, confirmContent) {
    window.PongGame.pauseGame();
    const confirmContentDiv = document.getElementById('confirmContent');
    const confirmTitleDiv = document.getElementById('confirmModalLabel');
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));

    confirmContentDiv.innerText = confirmContent;
    confirmTitleDiv.innerText = confirmTitle;
    // document.getElementById('confirmModal').addEventListener('shown.bs.modal', function() {
    //     document.getElementById('confirmModalClose').focus();
    // })
    confirmModal.show();
}

window.displayMainAlert = displayMainAlert;

// ========================== INDEX SCRIPT ==========================

async function loadFriendListModal() {
    const friendModal = document.getElementById('friendListModal');
    if (friendModal)
        friendModal.remove();
    await loadContent('/friendList.html', 'modals', true);
}

async function loadBlockedModal(){
    const friendModal = document.getElementById('blockedUsersModal')
    if (friendModal)
        friendModal.remove();
    await loadContent('/blockedUsers.html', 'modals', true);
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
    // if (!userInformations.is_guest)
        
}

document.getElementById('home').addEventListener('click', async event => {
    event.preventDefault();
    if (pathName === '/game'){
        cancelNavigation(undefined, '/');
    }
    else
        await navigateTo('/');
})

function addNotificationIndicator(div, number){
    if (!div.querySelector('.indicator')){
        const indicator = document.createElement('div');
        indicator.classList.add('indicator');
        indicator.innerText = number;
        div.appendChild(indicator);
    }
    else {
        div.querySelector('.indicator').innerText = number;
    }
}

function addSSEListeners(){
    console.log(document.getElementById('friendListModal'));
    
    sse.addEventListener('receive-friend-request', async event => {
        const friendListModal = bootstrap.Modal.getInstance(document.getElementById('friendListModal'));
        const isModalShown = friendListModal ? friendListModal._isShown : friendListModal;
        const isTabActive = document.getElementById('innerFriendRequests-tab').classList.contains('active');
        event = JSON.parse(event.data);
        console.log(event);
        if (!isModalShown || !isTabActive) {
            await displayNotification(undefined, 'friend request', event.message, event => {
                const friendListModal = new bootstrap.Modal(document.getElementById('friendListModal'));
                friendListModal.show();
            }, event.target);
            userInformations.notifications['friend_requests'] += 1;
            displayBadges();
        }
        addFriendRequest(event.data);
    });

    sse.addEventListener('accept-friend-request', async event => {
        event = JSON.parse(event.data);
        console.log(event);
        if (!(bootstrap.Modal.getInstance(document.getElementById('friendListModal'))._isShown))
            await displayNotification(undefined, 'friend request', event.message);
        removeFriendRequest(event.data.id);
        addFriend(event.data);
    })

    sse.addEventListener('cancel-friend-request', async event => {
        event = JSON.parse(event.data);
        if (userInformations.notifications['friend_requests'])
            userInformations.notifications['friend_requests'] -= 1;
        if (!userInformations.notifications['friend_requests'])
            removeBadges('friend_requests');
        else    
            displayBadges();
        removeFriendRequest(event.data.id);
    })

    sse.addEventListener('reject-friend-request', async event => {
        event = JSON.parse(event.data);
        removeFriendRequest(event.data.id);
        console.log(event);
    })

    sse.addEventListener('delete-friend', event => {
        event = JSON.parse(event.data);
        removeFriend(event.data);
    })
}

function initSSE(){
    sse = new EventSource(`/sse/users/?token=${getAccessToken()}`);

    sse.onopen = () => {
        console.log('SSE connection initialized');
    }

    sse.onmessage = event => {
        let data = JSON.parse(event.data);
        console.log(data);
    }

    // sse.addEventListener('ping', event => {
    //     console.log(event);
    // })

    sse.onerror = async error => {
        console.log(error);
        const shownModal = document.querySelector('.modal.show[aria-modal="true"]');
        if (shownModal)
            return;
        displayMainAlert('Error', 'Unable to connect to Server Sent Events. Note that several services will be unaivailable.');
    }

    addSSEListeners();
}

function addFriendListListener(){
    document.getElementById('friendListModal').addEventListener('show.bs.modal', async function() {
        this.clicked = true;
        initFriendModal();
    }, {once: true})
    document.getElementById('friendListModal').addEventListener('show.bs.modal', () => {
        if (document.getElementById('innerFriendRequests-tab').classList.contains('active'))
            removeBadges('friend_requests');
    })
    document.getElementById('innerFriendRequests-tab').addEventListener('click', () => {
        removeBadges('friend_requests');
    })
}

function getBadgesDivs(){
    badgesDivs['all'] = document.querySelectorAll('.all-badges');
    badgesDivs['friend_requests'] = document.querySelectorAll('.friend-badges');
    badgesDivs['chat'] = document.querySelectorAll('.chat-badges');
}

async function  indexInit(auto=true) {
    if (!auto){
        if (userInformations.code === 'user_not_found'){
            console.log('user was deleted from database, switching to guest mode');
            displayMainAlert("Unable to retrieve your account/guest profile","We're sorry your account has been permanently deleted and cannot be recovered.");
            await generateToken();
            await fetchUserInfos(true);
            initSSE();
            return navigateTo('/');
        }
        await loadUserProfile();
        getBadgesDivs();
    }
    else{
        await fetchUserInfos();
        initSSE();
        await loadFriendListModal();
        document.getElementById('innerFriendRequests-tab').clicked = true;
        addFriendListListener();
        let currentState = getCurrentState();
        console.log(`added ${window.location.pathname} to history with state ${currentState}`)
        history.replaceState({state: currentState}, '', window.location.pathname);
        incrementCurrentState();
        loadCSS('/css/styles.css', false);
        handleRoute();
    }
}

function handleFriendRequestNotification(target, img, notification, toastContainer, toastInstance){
    img.addEventListener('click', async event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        try {
            let data = await apiRequest(getAccessToken(), target.url, target.method);
            if (target.url.includes('friend_request')){
                userInformations.notifications['friend_requests'] -= 1;
                if (userInformations.notifications['friend_requests'])
                    displayBadges();
                else
                    removeBadges('friend_requests');
                removeFriendRequest(target.url.match(/\/(\d+)\/?$/)[1]);
                if (target.method === 'POST')
                    addFriend(data);
            }
        }
        catch(error){
            console.log(error);
        }
        notification.clicked = true;
        dismissNotification(notification, toastInstance, toastContainer);
    })
}

async function addTargets(notification, targets, toastInstance, toastContainer){
    console.log(targets);
    const notificationBody = notification.querySelector('.toast-body');
    Object.entries(targets).forEach(([i, target]) => {
        const img = document.createElement('img');
        img.id = `notif${notification.id}-target${i}`;
        img.className = 'notif-img';
        img.src = target.display_icon;
        
        notificationBody.appendChild(img);
        
        if (target.type === 'API') {
            handleFriendRequestNotification(target, img, notification, toastContainer, toastInstance);
            // img.addEventListener('click', event => {
            //     notification.clicked = true;
            //     dismissNotification(notification, toastInstance, toastContainer);
            // });
        }
    });
}

function dismissNotification(notification, toastInstance, toastContainer){
    toastInstance.hide();
    setTimeout (() => {
        displayedNotifications--;
        toastContainer.removeChild(document.getElementById(notification.id));
        if (notificationQueue.length){
            let notif= notificationQueue.shift();
            console.log(notificationQueue);
            displayNotification(notif[0], notif[1], notif[2], notif[3]);
        }
    }, 500);
}

async function displayNotification(icon=undefined, title=undefined, body=undefined, mainListener=undefined, target=undefined){

    if (displayedNotifications >= MAX_DISPLAYED_NOTIFICATIONS) {
        notificationQueue.push([icon, title, body, mainListener]);
        return;
    }
    const toastContainer = document.getElementById('toastContainer');

    await loadContent('/notification.html', 'toastContainer', true);
    const notification = document.getElementById('notification');
    notification.id = `notification${notificationIdentifier}`;
    if (icon)
        notification.querySelector('img').src = icon;
    if (title)
        notification.querySelector('strong').innerText = title;
    if (body)
        notification.querySelector('.toast-body').innerText = body;
    if (mainListener)
        notification.addEventListener('click', event => {
            mainListener(event);
            notification.clicked = true;
            dismissNotification(notificationIdentifier, toastInstance, toastContainer);
        }, {once: true});
    const toastInstance = new bootstrap.Toast(notification);
    if (target)
        addTargets(notification, target, toastInstance, toastContainer);
        // console.log(target);
    toastInstance.show();
    notificationIdentifier++;
    displayedNotifications++;
    setTimeout(() => {
        if (!notification.clicked){
            dismissNotification(notification, toastInstance, toastContainer)
        }
    }, 5000);
}

window.indexInit = indexInit;
window.loadUserProfile = loadUserProfile;

indexInit();
