document.getElementById('searchTournamentForm').addEventListener('keyup', async (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	console.log(e.target.value);
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/search/?q=${e.target.value}`);
		console.log(data);
	}
	catch (error){
		console.log(error);
	}
});

document.getElementById('searchTournamentForm').addEventListener('submit', (e) => {
	e.preventDefault();
	const tournamentName = document.getElementById('searchTournament').value;
	const createTournamentModal = new bootstrap.Modal(document.getElementById('createTournamentModal'));
	document.getElementById('tournamentName').value = tournamentName;
	createTournamentModal.show();
});

document.getElementById('rangeInput').addEventListener('input', e => {
	document.getElementById('tournamentSize').innerText = `Select size (${e.target.value})`;	
})

document.getElementById('createTournament').addEventListener('click', async event => {
	event.preventDefault();
	const tournamentName = document.getElementById('tournamentName').value;
	const tournamentSize = document.getElementById('rangeInput').value;
	try { 
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`, 'POST', undefined, undefined, {
			'name' : tournamentName,
			'size' : tournamentSize
		});
		console.log(data);
	}
	catch (error){
		console.log(error);
	}
})

async function initTournament(){
    await indexInit(false);
}

initTournament();