async function loadTabs() {
    const tabFiles = {
        'account' : 'profileTemplates/account.html',
        'friends' : 'profileTemplates/friends.html',
    }

    for (const key in tabFiles){
        await loadContent(tabFiles[key], key);
    }
}

async function profileInit() {
    await indexInit(false);
    loadTabs();
}

profileInit();