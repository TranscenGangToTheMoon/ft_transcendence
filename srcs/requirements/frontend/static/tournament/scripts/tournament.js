document.getElementById('searchChatForm').addEventListener('keyup', (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	selectChatMenu(e.target.value);
});

document.getElementById('searchChatForm').addEventListener('submit', (e) => {
	e.preventDefault();
	startChat(e.target.searchUser.value);
});

async function initTournament(){
    await indexInit(false);
}

initTournament();