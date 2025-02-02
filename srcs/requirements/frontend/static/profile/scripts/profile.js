async function loadTabs() {
    const tabFiles = {
        'account' : '/profile/profileTemplates/account.html',
        'friends' : '/profile/profileTemplates/friends.html',
        'ranked' : '/profile/profileTemplates/ranked.html',
        'statistics': '/profile/profileTemplates/statistics.html',
        'history' : '/profile/profileTemplates/matchHistory.html',
    }

    for (const key in tabFiles){
        await loadContent(tabFiles[key], key);
        await new Promise(r => setTimeout(r, 300));
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