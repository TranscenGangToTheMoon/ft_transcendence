async function loadTabs() {
    const tabFiles = {
        'account' : 'profileTemplates/account.html',
        'friends' : 'profileTemplates/friends.html',
    }

    for (const key in tabFiles){
        loadContent(tabFiles[key], key);
    }
}

async function atStart() {
    loadTabs();
    await fetchUserInfos(true);
    await loadUserProfile();
}

atStart();