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
    chatTabLink.innerHTML = "Game";
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

	await chatTabListener(gameInfo);
	sendMessageListener(gameInfo);
}

async function chatTabListener(gameInfo)
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
			openGameChatTab(gameInfo);
			return;
		}
	});
}

function sendMessageListener(gameInfo) {
    const chatForm = document.getElementById('sendGameMessageForm');
    if (!chatForm.hasAttribute('data-listener-added')) {
        chatForm.setAttribute('data-listener-added', 'true');
        chatForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const message = this.querySelector('input').value;
			if (message === '') return;
			//send message to server
            chatForm.reset();
        });
    }
}

async function closeChatTab(gameInfo)
{
	var isTabActive = false;
	let chatActiveTab = document.querySelector('#chatTabs .nav-link.active');
	let buttonCollapseChat = document.getElementById('chatTabsCollapse');
	if (!chatActiveTab) return;
	if (chatActiveTab.id === 'chatGameTab') isTabActive = true;
	document.getElementById('chatGameTab').remove();
	document.getElementById('chatGameBox').remove();
	let lastTab = document.getElementById('chatTabs').lastElementChild;
	await disconnect();
	if (!lastTab) {
		console.log('Chat: Closing chat view', lastTab);
		document.getElementById('chatView').remove();
	}
	else if (isTabActive) {
		if (buttonCollapseChat.getAttribute('aria-expanded') === 'true')
			lastTab.querySelector('a').click();
		else 
			lastClick = lastTab.querySelector('a').id;
	}
}

async function openGameChatTab(gameInfo) {
	chatTabs = document.getElementById('chatTabs');
	if (!chatTabs) {
		await setChatView();
	}
	if ()
}