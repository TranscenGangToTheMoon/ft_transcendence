if (typeof tournaments === 'undefined')
	var tournaments;

document.getElementById('searchTournamentForm').addEventListener('keyup', async (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/search/?q=${e.target.value}`);
		const tempDiv = document.createElement('div');
		tournaments = data;
		if (data.count){
			for (i in data.results){
				let tournament = data.results[i];
				let tournamentDiv = document.createElement('div');
				tournamentDiv.classList.add('tournamentDiv');
				tournamentDiv.id = `tournamentDiv${tournament.id}`
				tournamentDiv.innerText = `${tournament.name} (${tournament.n_participants}/${tournament.size})`;
				tempDiv.appendChild(tournamentDiv);

			}
		}
		document.getElementById('tournamentsList').innerHTML = tempDiv.innerHTML;
	}
	catch (error){
		console.log(error);
	}
});

function addParticipant(participant){
	const tournamentViewDiv = document.getElementById('tournamentView');
	const participantDiv = document.createElement('div');
	participantDiv.id = `tParticipant${participant.id}`;
	participantDiv.classList.add('tournament-participant');
	participantDiv.innerText = participant.username;
	tournamentViewDiv.appendChild(participantDiv);
}

function removeParticipant(id){
	const participantDiv = document.getElementById(`tParticipant${id}`);
	if (participantDiv)
		participantDiv.remove();
}

function tournamentJoined(event){
	event = JSON.parse(event.data);
	addParticipant(event.data);
}

function tournamentLeaved(event){
	event = JSON.parse(event.data);
	removeParticipant(event.data.id)
}

async function tournamentBanned(event){
	event = JSON.parse(event.data);
	console.log(event);
	// await navigateTo('/');
	// displayMainAlert('')
}

function tournamentStartAt(event) {
	if (document.getElementById('tCountdown')) return;
	event = JSON.parse(event.data);
	const startTime = event.data.start_at;
	const tournamentDiv = document.getElementById('tournamentView');
	const countdownDiv = document.createElement('div');
	countdownDiv.id = 'tCountdown';
	tournamentDiv.appendChild(countdownDiv);
	const targetDate = new Date(startTime);

	function updateCountdown() {
		const currentDate = new Date();
		const difference = Math.floor((targetDate - currentDate) / 1000);
		
		if (difference <= 0) {
			countdownDiv.innerHTML = "Starting Soon!";
			clearInterval(timer);
			return;
		}
		
		countdownDiv.innerHTML = `Starting in: ${difference}s`;
	}

	updateCountdown();
	const timer = setInterval(updateCountdown, 1000);
}

function tournamentStartCancel(){
	const countdownDiv = document.getElementById('tCountdown');
	if (countdownDiv)
		countdownDiv.remove();
}

function addTournamentSSEListeners(){

	if (!SSEListeners.has('tournament-join')){
        SSEListeners.set('tournament-join', tournamentJoined);
        sse.addEventListener('tournament-join', tournamentJoined);
    }

	if (!SSEListeners.has('tournament-leave')){
        SSEListeners.set('tournament-leave', tournamentLeaved);
        sse.addEventListener('tournament-leave', tournamentLeaved);
    }

	if (!SSEListeners.has('tournament-banned')){
        SSEListeners.set('tournament-banned', tournamentBanned);
        sse.addEventListener('tournament-banned', tournamentBanned);
    }

	if (!SSEListeners.has('tournament-start-at')){
        SSEListeners.set('tournament-start-at', tournamentStartAt);
        sse.addEventListener('tournament-start-at', tournamentStartAt);
    }

	if (!SSEListeners.has('tournament-start-cancel')){
        SSEListeners.set('tournament-start-cancel', tournamentStartCancel);
        sse.addEventListener('tournament-start-cancel', tournamentStartCancel);
    }

	// if (!SSEListeners.has('tournament-banned')){
    //     SSEListeners.set('tournament-banned', tournamentBanned);
    //     sse.addEventListener('tournament-banned', tournamentBanned);
    // }
}

function loadTournament(tournament){
	for (i in tournament.participants){
		let participant = tournament.participants[i];
		addParticipant(participant);
	}
	addTournamentSSEListeners();
}

document.getElementById('searchTournamentForm').addEventListener('submit', async (e) => {
	e.preventDefault();
	const tournamentName = document.getElementById('searchTournament').value;
	if (tournaments.count !== 0){
		for (i in tournaments.results){
			let tournament = tournaments.results[i];
			if (tournament.name === tournamentName){
				try {
					let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${tournament.code}/`, 'POST');
					const tournamentDiv = document.getElementById(`tournamentDiv${tournament.id}`);
					console.log(tournament);
					if (tournamentDiv)
						tournamentDiv.innerText = `${tournament.name} (${tournament.n_participants + 1}/${tournament.size})`;
					loadTournament(data);
				}
				catch (error){	
					console.log(error);
				}
				return;
			}
		}
	}
	const createTournamentModal = new bootstrap.Modal(document.getElementById('createTournamentModal'));
	document.getElementById('tournamentName').value = tournamentName;
	createTournamentModal.show();
});

document.getElementById('rangeInput').addEventListener('input', e => {
	document.getElementById('tournamentSize').innerText = `Select size (${e.target.value})`;	
})

document.getElementById('createTournament').addEventListener('click', async event => {
	event.preventDefault();
	const createTournamentModal = bootstrap.Modal.getOrCreateInstance('#createTournamentModal');
	const tournamentName = document.getElementById('tournamentName').value;
	const tournamentSize = document.getElementById('rangeInput').value;
	try { 
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`, 'POST', undefined, undefined, {
			'name' : tournamentName,
			'size' : tournamentSize
		});
		console.log(data);
		if (data.detail){
			document.getElementById('createTournamentError').innerText = data.detail;
			setTimeout(() => {
				document.getElementById('createTournamentError').innerText = '';
			}, 2500);
			return;
		}
		createTournamentModal.hide();
		loadTournament(data);
	}
	catch (error){
		console.log(error);
	}
})

async function initTournament(){
    await indexInit(false);
	// try {
	// 	let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`);
	// 	console.log('idejio',data);
	// }
	// catch(error) {
	// 	console.log(error);
	// }
}

initTournament();