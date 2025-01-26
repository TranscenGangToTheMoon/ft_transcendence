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
var pathName = window.location.pathname;
var badgesDivs = {};
var notificationQueue = [];
const SSEListeners = new Map();
var fromTournament = false;

// ========================== SCRIPT ROUTING ==========================

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

// ========================== MAIN  ==========================

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
    await loadContent('/friends/friendList.html', 'modals', true);
}

async function loadBlockedModal(){
    const friendModal = document.getElementById('blockedUsersModal')
    if (friendModal)
        friendModal.remove();
    await loadContent('/blockedUsers/blockedUsers.html', 'modals', true);
}

async function loadChatListModal(){
    const chatListModal = document.getElementById('chatListModal')
    if (chatListModal)
        chatListModal.remove();
    await loadContent('/chatTemplates/chatListModal.html', 'modals', true);
}

async function  loadUserProfile(){
    let profileMenu = 'profileMenu/profileMenu.html';

    document.getElementById('username').innerText = userInformations.username;
    if (userInformations.is_guest){
        profileMenu = 'profileMenu/guestProfileMenu.html'
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
        console.log('zizi');
        await loadUserProfile();
    }
    else{
        await loadScript('/scripts/singlePageApplicationUtils.js');
        await loadScript('/scripts/api.js');
        await loadScript('/scripts/token.js');
        await loadScript('/scripts/serverSentEventsUtils.js');
        await loadScript('/notification/scripts/notificationUtils.js');
        await loadScript('/scripts/utils.js');
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
        quitLobbies('', window.location.pathname);
        handleRoute();
    }
}

window.addEventListener("pageshow", (event) => {
    if (event.persisted) {
        indexInit();
    }
});

indexInit();
