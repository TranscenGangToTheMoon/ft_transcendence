async function loadTabs() {
    const tabFiles = {
        'account' : 'profileTemplates/account.html',
        'friends' : 'profileTemplates/friends.html',
    }

    for (const key in tabFiles){
        loadContent(tabFiles[key], key);
    }
}

async function profileInit() {
    loadTabs();
    // await fetchUserInfos(true);
    // if (document.getElementById('username').innerText !== userInformations)
    // await loadUserProfile();
}

profileInit();