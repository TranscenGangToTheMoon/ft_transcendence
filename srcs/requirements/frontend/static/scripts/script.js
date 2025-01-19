// ========================== GLOBAL VALUES ==========================

const MAX_DISPLAYED_NOTIFICATIONS = 3;
const MAX_DISPLAYED_FRIENDS = 12;
const MAX_DISPLAYED_FRIEND_REQUESTS = 5;
const MAX_DISPLAYED_BLOCKED_USERS = 10;
const GAME_CONNECTION_TIMEOUT = 5500; // min 5500
const DEBOUNCE_TIME = 100;
const eventTimestamps = new Map();
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
const SSEListeners = new Map();
var fromTournament = false;

window.pathName = pathName;

// ========================== API REQUESTS ==========================

async function apiRequest(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined, currentlyRefreshing=false, nav=false){
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
        .catch(async error =>{
            if (error.message === 'relog')
                return apiRequest(getAccessToken(), endpoint, method, authType, contentType, body);
            if (error.code === 500 || error.message === 'Failed to fetch')
                document.getElementById('container').innerText = `alala pas bien ${error.code? `: ${error.code}` : ''} (jcrois c'est pas bon)`;
            if (error.code === 502 || error.code === 503){
                pathName = '/service-unavailable';
                closeExistingModals();
                if (nav)
                    await navigateTo('/service-unavailable', true, true);
                else{
                    history.replaceState({}, '', '/service-unavailable');
                    handleRoute();
                }
            }
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

async function relog(){
    // if (window.location.pathname !== '/')
    //     await navigateTo('/');
    await generateToken();
    displayMainAlert("Unable to retrieve your account/guest profile","We're sorry your account has been permanently deleted and cannot be recovered.");
    throw new Error('relog');
    // await fetchUserInfos();
    // await loadUserProfile();
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
            console.log('refresh token expired must relog')
            // if (userInformations && userInformations.is_guest === true){
            //     return forceReloadGuestToken();
            // }
            await relog();
        }
    }
    catch (error) {
        if (error.message === 'relog')
            throw error;
        else
            console.log("ERROR", error);
    }
}

function getAccessToken() {
    return localStorage.getItem('token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh');
}

function removeTokens() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
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

function clearCSS(){
    const links = document.querySelectorAll('link[clearable]');
    for (let link of links){
        link.remove();
    }
}

function loadCSS(cssHref, clearable) {
    const existingLink = document.querySelector(`link[href="${cssHref}"]`);
    if (existingLink) {
        existingLink.remove();
    }
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = cssHref;
    if (clearable)
        link.setAttribute('clearable', 'true');
    document.head.appendChild(link);
}

async function loadContent(url, containerId='content', append=false, container=undefined) {
    let contentDiv = document.getElementById(containerId);
    if (container)
        contentDiv = container;
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
            loadCSS(css.getAttribute(style), css.getAttribute('clearable'));//, !css.getAttribute(style).includes('Guest'));
    } catch (error) {
        console.log(error);
        contentDiv.innerHTML = '<h1>Erreur 404 : Page non trouvée</h1>';
    }
}

function containsCode(path){
    const regex = /^\/(game|lobby|tournament)\/\d+$/;
    return regex.test(path);
}

async function handleRoute() {
    var path = window.location.pathname;
    if (window.location.pathname !== 'game')
        window.PongGame?.stopGame();
    if (containsCode(path))
        path = "/" + path.split("/")[1];
    const routes = {
        '/': '/homePage.html',
        '/service-unavailable' : '/503.html',
        '/profile' : 'profile.html',
        '/lobby' : '/lobby.html',

        '/game/ranked' : '/game/game.html',
        '/game/duel' : '/game/game.html',
        '/game/custom' : '/game/game.html',
        '/game/local' : '/game/localGame.html',
        '/game/tournament' : '/game/game.html',
        '/game/1v1' : '/game/game.html',
        '/game/3v3' : '/game/3v3.html',
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

function _cancelTimeout(){
    if (typeof cancelTimeout !== 'undefined')
        cancelTimeout = true;
}

async function navigateTo(url, doNavigate=true, dontQuit=false){
    let currentState = getCurrentState();
    lastState = currentState;
    // if (doNavigate){
    _cancelTimeout();
    if (!dontQuit){
        await handleSSEListenerRemoval(url);
        await quitLobbies(window.location.pathname, url);
        await closeGameConnection(window.location.pathname);
    }
    // }
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
    _cancelTimeout();
    await quitLobbies(pathName, window.location.pathname);
    await closeGameConnection(pathName);
    pathName = window.location.pathname;
    if (event.state && event.state.state)
        lastState = event.state.state;
    if (userInformations.is_guest !== (document.getElementById('trophies') === '')){
        await loadUserProfile();
    }
    handleRoute();
})

async function quitLobbies(oldUrl, newUrl){
    if (oldUrl === '/service-unavailable') return;
    if (oldUrl.includes('/lobby')){
        try {
            await apiRequest(getAccessToken(), `${baseAPIUrl}/play${oldUrl}/`, 'DELETE');
        }
        catch (error){
            console.log(error);
        }
    }
    if (oldUrl.includes('/tournament') && typeof tournament !== 'undefined' && tournament && (!fromTournament && (
        containsCode(oldUrl) && !containsCode(newUrl)
    ))){
        console.log(fromTournament);
        try {
            await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${tournament.code}/`, 'DELETE');
        }
        catch (error){
            console.log(error);
        }
    }
}

window.loadContent = loadContent;
window.cancelNavigation = cancelNavigation;

// ========================== SSE SCRIPTS ==========================

async function handleSSEListenerRemoval(url){
    if (window.pathName.includes('/lobby') && !url.includes('/lobby')){
        removeSSEListeners('lobby');
    }
    if (window.pathName.includes('/tournament')){
        removeSSEListeners('tournament');
    }
}

function checkEventDuplication(data){
    const now = Date.now();

    const lastTimeStamp = eventTimestamps.get(data.event_code);
    // console.log(lastTimeStamp);f
    if (lastTimeStamp && (now - lastTimeStamp < DEBOUNCE_TIME)){
        console.log('skip', data);
        return 0;
    }

    eventTimestamps.set(data.event_code, now);
    // console.log('cala',eventTimestamps.get(data));
    return 1;
}

function removeSSEListeners(type){
    for (const [key, value] of SSEListeners) {
        if (key.includes(type)) {
            sse.removeEventListener(key, value);
            SSEListeners.delete(key);
            // console.log('removed sse listener:', key);
        }
    }
}

function addFriendSSEListeners(){
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
                document.getElementById('innerFriendRequests-tab').click();
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
        console.log(event.data);
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

function addInviteSSEListeners(){
    sse.addEventListener('invite-clash', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        console.log(event);
    })

    sse.addEventListener('invite-3v3', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        console.log(event);
    })

    sse.addEventListener('invite-1v1', event => {
        event = JSON.parse(event.data);
        displayNotification(undefined, event.service, event.message, undefined, event.target);
        console.log(event);
    })

    sse.addEventListener('invite-tournament', event => {
        event = JSON.parse(event.data);
        console.log(event);
    })

}

function addChatSSEListeners(){
    sse.addEventListener('send-message', async event => {
        event = JSON.parse(event.data);
        console.log(event, 'ai je ce qu il faut ?');
        chat = event.target[0]['url'];
        let apiAnswer = undefined;
        try {
            apiAnswer = await apiRequest(getAccessToken(), `${baseAPIUrl}${chat}`, 'GET');
            if (apiAnswer.details) {
                console.log('Error:',apiAnswer.details);
                return;
            }
        }
        catch (error){
            console.log('Error:', error);
            return;
        }
        userInformations.notifications['chats'] += 1;
        chatInfo = {
            'chatId': apiAnswer.id,
            'target': apiAnswer.chat_with.username,
            'targetId': apiAnswer.chat_with.id,
            'lastMessage': '< Say hi! >',
            'isLastMessageRead': false,
            'chatMessageNext': null,
        };
        if (apiAnswer.last_message) {
            if (apiAnswer.last_message.content.length > 37){
                chatInfo.lastMessage = apiAnswer.last_message.content.slice(0, 37) + '...';
            }
            else chatInfo.lastMessage = apiAnswer.last_message.content;
            chatInfo.isLastMessageRead = apiAnswer.last_message.is_read;
        }
        await displayNotification(undefined, 'message received', event.message, async event => {
            await openChatTab(chatInfo);
        });
        displayBadges();
    })
}

function addSSEListeners(){

    addFriendSSEListeners();
    addInviteSSEListeners();
    addChatSSEListeners();
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
        displayMainAlert('Error', 'Unable to connect to Server Sent Events. Note that several services will be unavailable.');
    }

    addSSEListeners();
}

// ====================== NOTIFICATIONS UTILS ======================


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

function getBadgesDivs(){
    badgesDivs['all'] = document.querySelectorAll('.all-badges');
    badgesDivs['friend_requests'] = document.querySelectorAll('.friend-badges');
    badgesDivs['chats'] = document.querySelectorAll('.chat-badges');
}


function handleFriendRequestNotification(target, img, notification, toastContainer, toastInstance){
    img.addEventListener('click', async event => {
        event.preventDefault();
        event.stopImmediatePropagation();
        event.stopPropagation();
        console.log('click ?')
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
        if (target.display_icon){
            var img = document.createElement('img');
            img.id = `notif${notification.id}-target${i}`;
            img.className = 'notif-img';
            img.src = target.display_icon;
            
            notificationBody.appendChild(img);
        }
        if (target.display_name){
            var button = document.createElement('button');
            button.id = `notif${notification.id}-nametarget${i}`;
            button.className = 'notif-button';
            button.innerText = target.display_name;

            notificationBody.appendChild(button);
        }
        if (target.type === 'api') {
            handleFriendRequestNotification(target, img, notification, toastContainer, toastInstance);
            // img.addEventListener('click', event => {
            //     notification.clicked = true;
            //     dismissNotification(notification, toastInstance, toastContainer);
            // });
        }
        else if (target.type === 'url'){
            button.addEventListener('click', async () => {
                console.log(target.url.slice(0, -1));
                await navigateTo(target.url.slice(0, -1));
                notification.clicked = true;
                dismissNotification(notification, toastInstance, toastContainer);
            })
        }
    });
}

function dismissNotification(notification, toastInstance, toastContainer){
    toastInstance.hide();
    setTimeout (() => {
        displayedNotifications--;
        console.log(notification);
        toastContainer.removeChild(document.getElementById(notification.id));
        if (notificationQueue.length){
            let notif= notificationQueue.shift();
            console.log(notificationQueue);
            displayNotification(notif[0], notif[1], notif[2], notif[3], notif[4]);
        }
    }, 500);
}

async function displayNotification(icon=undefined, title=undefined, body=undefined, mainListener=undefined, target=undefined){

    if (displayedNotifications >= MAX_DISPLAYED_NOTIFICATIONS) {
        notificationQueue.push([icon, title, body, mainListener, target]);
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
            if (event.target.classList.contains('btn-close')) return;
            mainListener(event);
            notification.clicked = true;
            dismissNotification(notification, toastInstance, toastContainer);
        }, {once: true});
    const toastInstance = new bootstrap.Toast(notification);
    if (target)
        addTargets(notification, target, toastInstance, toastContainer);
    toastInstance.show();
    notificationIdentifier++;
    displayedNotifications++;
    setTimeout(() => {
        if (!notification.clicked){
            dismissNotification(notification, toastInstance, toastContainer)
        }
    }, 5000);
}

// ========================== OTHER UTILS ==========================

async function closeGameConnection(oldUrl){
    if (!oldUrl.includes('game') || oldUrl.includes('local')) return;
    if (typeof gameSocket !== 'undefined'){
        console.log("je close la grosse game socket la");
        gameSocket.close();
        gameSocket = undefined;
    }
    if (fromTournament)return;
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}${oldUrl.replace("game", 'play')}/`, 'DELETE');
    }
    catch(error){
        console.log(error);
    }
}

function closeExistingModals(){
    const modals = document.querySelectorAll('.modal');
    for (let modal of modals){
        if (modal.classList.contains('show')){
            const modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
            if (modalInstance)
                modalInstance.hide();
        }
    }
}

async function fetchUserInfos(forced=false) {
    if (!getAccessToken())
        await generateToken();
    if (!userInformations || forced) {
        try {
            let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`);
            userInformations = data;
            console.log(userInformations);
            displayBadges();
        }
        catch (error) {
            if (error.message === 'relog')
                throw error;
            console.log(error);
        }
    }
}

function isModalOpen() {
    return (
        document.querySelector('.modal.show') !== null ||
        document.querySelector('.modal[style*="display: block"]') !== null ||
        document.querySelector('.modal.fade.in') !== null ||
        document.querySelector('.modal-backdrop') !== null
    );
}

function displayMainAlert(alertTitle, alertContent) {
    if (isModalOpen()) return;
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

document.addEventListener('click', (e) => {
    contextMenu = document.getElementById('contextMenu');
    if (contextMenu)
        document.getElementById('contextMenu').style.display = 'none';
});

document.addEventListener('keyup', e => {
    if (e.key === 'Escape'){
        let contextMenu = document.getElementById('contextMenu');
        if (contextMenu)
            contextMenu.style.display = 'none';
    }
})

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

async function loadChatListModal(){
    const chatListModal = document.getElementById('chatListModal')
    if (chatListModal)
        chatListModal.remove();
    await loadContent('/chatTemplates/chatListModal.html', 'modals', true);
}

async function  loadUserProfile(){
    let profileMenu = 'profileMenu.html';

    document.getElementById('username').innerText = userInformations.username;
    if (userInformations.is_guest){
        profileMenu = 'guestProfileMenu.html'
        document.getElementById('trophies').innerText = "";
    }
    else {
        document.getElementById('trophies').innerText = userInformations.trophies;
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

async function  indexInit(auto=true) {
    if (!auto){
        await loadUserProfile();
        getBadgesDivs();
    }
    else{
        await fetchUserInfos();
        if (userInformations.code === 'user_not_found'){
            console.log('user was deleted from database, switching to guest mode');
            await generateToken();
            await fetchUserInfos(true);
            displayMainAlert("Unable to retrieve your account/guest profile","We're sorry your account has been permanently deleted and cannot be recovered.");
        }
        initSSE();
        await loadFriendListModal();
        await loadChatListModal();
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

window.indexInit = indexInit;
window.loadUserProfile = loadUserProfile;

indexInit();

async function temp(ind=25){
    try{
        let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST');
            data = await apiRequest(data.access, `${baseAPIUrl}/auth/register/guest/`, 'PUT', undefined, undefined, {
                'username' : 'flo',
                'password' : 'flo',
            })
    }
    catch (error){
        console.log(error);
    }
    for (let i = 0; i < ind; i++){
        try {
            let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST');
            data = await apiRequest(data.access, `${baseAPIUrl}/auth/register/guest/`, 'PUT', undefined, undefined, {
                'username' : `${getCurrentState()}user${i}`,
                'password' : 'user',
            })
            data = await apiRequest(data.access, `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
                'username': userInformations.username,
            });
        }
        catch(error){
            console.log(error);
        }
    }
}

// temp();