async function loadTabs() {
    const tabFiles = {
        'account' : 'profileTemplates/account.html',
        'friends' : 'profileTemplates/friends.html',
    }

    for (const key in tabFiles){
        loadContent(tabFiles[key], key);
        console.log(`je load ${tabFiles[key]} dans la div ${key}`);
    }
}

async function atStart() {
    loadTabs();
    await fetchUserInfos(true);
    await loadUserProfile();
}

atStart();