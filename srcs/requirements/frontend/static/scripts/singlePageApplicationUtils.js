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
        getBadgesDivs(contentDiv);
        badgesDivs['friend_requests'] = contentDiv.querySelectorAll('.friend-badges');
        displayBadges();

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
        '/': '/homePage/homePage.html',
        '/profile' : '/profile/profile.html',
        '/lobby' : '/lobby/lobby.html',

        '/game/ranked' : '/game/game.html',
        '/game/duel' : '/game/game.html',
        '/game/custom' : '/game/game.html',
        '/game/local' : '/game/localGame.html',
        '/game/tournament' : '/game/game.html',
        '/game/1v1' : '/game/game.html',
        '/game/3v3' : '/game/3v3.html',
        '/tournament' : '/tournament/tournament.html'
    };

    const page = routes[path] || '/errors/404.html';
    await loadContent(page);
}

if (typeof lastState === 'undefined')
    var lastState = 0;
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
    if (url === window.location.pathname) return;
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

function confirmPopstate() {
    pathName = "";
    if (direction > 0){
        history.forward();
    }
    else{
        history.go(direction);
    }
}

if (typeof isUserGoBack === 'undefined')
    var isUserGoBack = true;
if (typeof direction === 'undefined')
    var direction = 0;

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