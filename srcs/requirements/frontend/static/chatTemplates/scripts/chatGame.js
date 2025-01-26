function displayGameChatMessage(event){
	event = JSON.parse(event.data);
	let messageDiv = document.createElement('div');
	messageDiv.className = 'messageGame';
	messageDiv.innerText = event.message;
	let chatBox = document.getElementById('messagesGame');
	if (chatBox) {
		chatBox.appendChild(messageDiv);
	}
}

async function createGameChatTab(gameInfo) {
	let idChatTab = "chatGameTab";
    let idChatBox = "chatGameBox";

    let chatTabs = document.getElementById('chatTabs');

    let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
    if (chatActiveTab) {
        chatActiveTab.classList.remove('active');
        let lastTabId = chatActiveTab.getAttribute('href').substring(1);
        let lastChatBox = document.getElementById(lastTabId);
        if (lastChatBox) {
            lastChatBox.classList.remove('active');
        }
    }

    let chatTab = document.createElement('li');
    chatTab.id = idChatTab;
    chatTab.className = 'chatTab nav-item';
    chatTabs.setAttribute('role', 'presentation');

    let chatTabLink = document.createElement('a');
    chatTabLink.id = idChatTab + "Link";
    chatTabLink.innerText = "Game";
    chatTabLink.setAttribute('data-bs-toggle', 'tab');
    chatTabLink.setAttribute('role', 'tab');
    chatTabLink.setAttribute('href', "#" + idChatBox);
	chatTabLink.setAttribute('aria-controls', idChatBox);
	chatTabLink.setAttribute('aria-selected', 'true');
    chatTabLink.className = 'nav-link active';

    chatTab.appendChild(chatTabLink);
    chatTabs.appendChild(chatTab);

    let chatBody = document.getElementById('chatBody');
    let chatBox = document.createElement('div');
    chatBox.id = idChatBox;
	chatBox.className = 'tab-pane fade show active';
    chatBox.setAttribute('role', 'tabpanel');
    chatBox.setAttribute('aria-labelledby', idChatTab);
    chatBody.appendChild(chatBox);

    await loadContent('/chatTemplates/chatBox.html', idChatBox);
	const messagesDiv = chatBox.querySelector('.messages');
	if (messagesDiv){
		messagesDiv.id = 'messagesGame';
	}
	const sendMessageForm = chatBox.querySelector('.sendMessageForm');
	if (sendMessageForm){
		sendMessageForm.id = 'sendGameMessageForm';
	}
	const tab = new bootstrap.Tab(chatTabLink);
	tab.show();

	lastClick = chatTabLink.id;

	await chatGameTabListener();
	sendGameMessageListener(gameInfo);
}

async function chatGameTabListener()
{
	document.getElementById('chatGameTab').addEventListener('click', async e => {
		e.preventDefault();
		if (e.target.id === 'chatGameTab') {
			let buttonCollapseChat = document.getElementById('chatTabsCollapse');
			if (buttonCollapseChat.getAttribute('aria-expanded') === 'false') {
				lastClick = undefined;
				buttonCollapseChat.click();
			}
			if (lastClick === e.target.id) return;
			lastClick = e.target.id;
			return;
		}
	});
}

function sendGameMessageListener(gameInfo) {
    const chatForm = document.getElementById('sendGameMessageForm');
	chatForm.addEventListener('submit', async function (e) {
		e.preventDefault();
		const message = this.querySelector('input').value;
		if (message === '') return;
		try {
			var apiAnswer = undefined;
			if (gameInfo.type === 'lobby'){
				apiAnswer = await apiRequest(getAccessToken(), `/api/play/lobby/${gameInfo.code}/message/`, 'POST', undefined, undefined, {
					'content': message,
				});
			}
			else if (gameInfo.type === 'tournament'){
				apiAnswer = await apiRequest(getAccessToken(), `/api/play/tournament/${gameInfo.code}/message/`, 'POST', undefined, undefined, {
					'content': message,
				});
			}
			if (apiAnswer.detail) {
				throw {'code': 400, 'detail': apiAnswer.detail};
			}
			let messageDiv = document.createElement('div');
			messageDiv.className = 'messageGame';
			messageDiv.innerText = "You: " + message;
			let chatBox = document.getElementById('messagesGame');
			if (chatBox) {
				chatBox.appendChild(messageDiv);
			}
			chatForm.reset();
		} catch (error) {
			console.log('Error game chat:', error);
			displayChatError(error, 'messagesGame');
		}
	});
}

async function closeGameChatTab()
{
	var isTabActive = false;
	let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
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

async function openGameChatTab(gameInfo) {
	chatTabs = document.getElementById('chatTabs');
	if (!chatTabs) {
		await setChatView();
	}
	if (document.getElementById('chatGameTab')) 
	{
		document.getElementById('messagesGame').innerHTML = '';
		return;
	}
	await createGameChatTab(gameInfo);
}