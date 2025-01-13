async function loadTabs() {
    const tabFiles = {
        'account' : 'profileTemplates/account.html',
        'friends' : 'profileTemplates/friends.html',
        'statistics': 'profileTemplates/statistics.html',
        'history' : 'profileTemplates/matchHistory.html',
    }

    for (const key in tabFiles){
        await loadContent(tabFiles[key], key);
    }
}

async function profileInit() {
    await indexInit(false);
    const buggyModals = document.querySelectorAll('.modal[style]');
    for (let buggyModal of buggyModals)
        buggyModal.removeAttribute('style');
    await loadTabs();
}

profileInit();