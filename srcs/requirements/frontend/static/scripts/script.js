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
let keepAlert = false;

// ========================== SCRIPT ROUTING ==========================

function loadScript(scriptSrc, type) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = scriptSrc;
        if (type)
            script.type = type;
        script.onload = () => {
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
let isInside = false;
document.getElementById('home').addEventListener('mouseover', function(){
    if (!isInside){
        document.getElementById('home').querySelector('img').style.transition = 'all 0.3s'
        document.getElementById('home').querySelector('img').style.filter = 'invert(1)'
    }
    isInside = true;
})

document.getElementById('home').addEventListener('mouseleave', event => {
    isInside = false;
    document.getElementById('home').querySelector('img').style.removeProperty('filter');
})

document.addEventListener('click', (e) => {
    contextMenu = document.getElementById('contextMenu');
    if (contextMenu)
        document.getElementById('contextMenu').style.display = 'none';
    else{
        contextMenu = document.getElementById('friendListContextMenu');
        if (contextMenu)
            contextMenu.style.display = 'none'
    }
});

document.addEventListener('keyup', e => {
    if (e.key === 'Escape'){
        let contextMenu = document.getElementById('contextMenu');
        if (contextMenu)
            contextMenu.style.display = 'none';
        else{
            contextMenu = document.getElementById('friendListContextMenu');
            if (contextMenu)
                contextMenu.style.display = 'none'
        }
    }
})

document.getElementById('privacyPolicyLink').addEventListener('click', function(){
    privacyPolicyModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('privacyPolicyModal'));
    if (isModalOpen()) return;
    if (privacyPolicyModal && !privacyPolicyModal._isShown){
        privacyPolicyModal.show();
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

async function loadPrivacyPolicy(){
    const privacyPolicyModal = document.getElementById('privacyPolicyModal')
    if (privacyPolicyModal)
        privacyPolicyModal.remove();
    await loadContent('/privacyPolicyModal.html', 'modals', true);
}

let cancelHide = false;

function addHoverListeners(userInfosDiv, dropdownMenu){
    console.log(dropdownMenu);
    let mouseAlreadyIn = false;
    userInfosDiv.addEventListener('mouseover', () => {
        if (mouseAlreadyIn) return;
        dropdownMenuInstance = bootstrap.Dropdown.getOrCreateInstance(dropdownMenu);
        cancelHide = true;
        console.log(dropdownMenuInstance);
        if (dropdownMenuInstance && !dropdownMenuInstance._element.classList.contains('show'))
            dropdownMenuInstance.toggle();
        mouseAlreadyIn = true;
    })
    userInfosDiv.addEventListener('mouseleave', () => {
        dropdownMenuInstance = bootstrap.Dropdown.getOrCreateInstance(dropdownMenu);
        cancelHide = false;
        mouseAlreadyIn = false;
        if (dropdownMenuInstance)
            setTimeout(()=> {
                if (!cancelHide && dropdownMenuInstance._element.classList.contains('show'))
                    dropdownMenuInstance.toggle();
            }, 300);
    });
    dropdownMenu.addEventListener('mouseover', () => {
        cancelHide = true;
    })
    dropdownMenu.addEventListener('mouseleave', function () {
        dropdownMenuInstance = bootstrap.Dropdown.getOrCreateInstance(this);
        cancelHide = false;
        if (dropdownMenuInstance)
            setTimeout(()=> {
                if (!cancelHide && dropdownMenuInstance._element.classList.contains('show'))
                    dropdownMenuInstance.toggle();
            }, 300);
    })
}

// function addGuestHoverListeners(userInfosDiv, dropdownMenu){
//     let mouseAlreadyIn = false;
//     userInfosDiv.addEventListener('mouseover', () => {
//         if (mouseAlreadyIn) return;
//         dropdownMenuInstance = bootstrap.Dropdown.getOrCreateInstance(dropdownMenu);
//         cancelHide = true;
//         console.log(dropdownMenuInstance);
//         if (dropdownMenuInstance && !dropdownMenuInstance._element.classList.contains('show'))
//             dropdownMenuInstance.toggle();
//         mouseAlreadyIn = true;
//     })
//     userInfosDiv.addEventListener('mouseleave', () => {
//         dropdownMenuInstance = bootstrap.Dropdown.getOrCreateInstance(dropdownMenu);
//         cancelHide = false;
//         mouseAlreadyIn = false;
//         if (dropdownMenuInstance)
//             setTimeout(()=> {
//                 if (!cancelHide && dropdownMenuInstance._element.classList.contains('show'))
//                     dropdownMenuInstance.toggle();
//             }, 300);
//     });
//     dropdownMenu.addEventListener('mouseover', () => {
//         cancelHide = true;
//     })
//     dropdownMenu.addEventListener('mouseleave', function () {
//         dropdownMenuInstance = bootstrap.Dropdown.getOrCreateInstance(this);
//         cancelHide = false;
//         if (dropdownMenuInstance)
//             setTimeout(()=> {
//                 if (!cancelHide && dropdownMenuInstance._element.classList.contains('show'))
//                     dropdownMenuInstance.toggle();
//             }, 300);
//     })
// }

async function  loadUserProfile(){
    let profileMenu = 'profileMenu/profileMenu.html';

    const usernameDiv = document.getElementById('username')
    usernameDiv.innerText = userInformations.username;
    usernameDiv.style.width = '100px';
    usernameDiv.className = 'text-truncate text-center px-1 fs-4'
    if (userInformations.is_guest){
        profileMenu = 'profileMenu/guestProfileMenu.html'
        document.getElementById('trophies').innerText = "";
    }
    else {
        document.getElementById('trophies').innerHTML = `
        <div>${userInformations.trophies}</div><img src="/assets/trophy.png" style="width:20px;height:20px">`;
    }
    const userInfos = document.getElementById('userInfos');
    userInfos.style.backgroundImage = `url(${userInformations['profile_picture']?.small ?? '/assets/imageNotFound.png'})`;
    userInfos.style.maxHeight = `100px`;
    userInfos.style.maxWidth = `100px`;
    userInfos.style.aspectRatio = '1 / 1';
    userInfos.style.backgroundRepeat = 'repeat-y';
    userInfos.style.backgroundSize = 'cover';
    userInfos.className = 'd-flex flex-column-reverse overflow-hidden'
    const profileDiv = document.getElementById('profile');
    profileDiv.style.cursor = 'pointer';
    await loadContent(`/${profileMenu}`, 'profileMenu');
    const dropdownMenu = document.getElementById('dropdownMenuProfile');
    addHoverListeners(profileDiv, dropdownMenu);
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
    }
    else{
        await loadScript('/scripts/singlePageApplicationUtils.js');
        await loadScript('/scripts/api.js');
        await loadScript('/scripts/token.js');
        await loadScript('/scripts/serverSentEventsUtils.js');
        await loadScript('/notification/scripts/notificationUtils.js');
        await loadScript('/scripts/utils.js');
        loadCSS('/css/styles.css', false);
        await fetchUserInfos();
        if (!userInformations)
            return;
        if (userInformations.code === 'user_not_found'){
            console.log('user was deleted from database, switching to guest mode');
            await generateToken();
            await fetchUserInfos(true);
            displayMainAlert("Account Not Found", "We are unable to retrieve your account or guest profile.", 'warning', '4000');
        }
        initSSE();
        await loadFriendListModal();
        await loadChatListModal();
        await loadPrivacyPolicy();
        document.getElementById('innerFriendRequests-tab').clicked = true;
        addFriendListListener();
        let currentState = getCurrentState();
        console.log(`added ${window.location.pathname} to history with state ${currentState}`)
        history.replaceState({state: currentState}, '', window.location.pathname);
        incrementCurrentState();
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
