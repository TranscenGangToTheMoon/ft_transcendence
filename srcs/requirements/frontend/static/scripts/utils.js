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

async function closeGameChatTab()
{
	var isTabActive = false;
	let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
    if (typeof actualGameChat !== 'undefined')
        actualGameChat = undefined;
	if (!chatActiveTab) return;
	if (chatActiveTab.id === 'chatGameTabLink') isTabActive = true;
	let chatGameTab = document.getElementById('chatGameTab');
	let chatGameBox = document.getElementById('chatGameBox');
	if (chatGameTab) chatGameTab.remove();
	if (chatGameBox) chatGameBox.remove();
	let lastTab = document.getElementById('chatTabs').lastElementChild;
	if (!lastTab) {
		lastClick = undefined;
		document.getElementById('chatView').remove();
	}
	else if (isTabActive) {
		lastClick = undefined;
		if (buttonCollapseChat.getAttribute('aria-expanded') === 'true') {
			lastTab.querySelector('a').click();
		}
		else {
			lastClick = lastTab.querySelector('a').id;
		}
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
    await closeGameChatTab();
    if (oldUrl === '/service-unavailable') return;
    console.log('je passe pourtant');
    let regex = /\/[A-Za-z]+\/[0-9]+/i;;
    console.log('hey' ,regex.test(newUrl));
    console.log('hey1' ,localStorage.getItem('lobbyCode'));
    if (localStorage.getItem('lobbyCode') && !regex.test(newUrl)){
        try {
            await apiRequest(getAccessToken(), `${baseAPIUrl}/play${localStorage.getItem('lobbyCode')}/`, 'DELETE');
            localStorage.removeItem('lobbyCode');
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