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
    confirmModal.show();
}