if (typeof tournaments === 'undefined')
	var tournaments;
if (typeof tournament === 'undefined')
	var tournament;
if (typeof selectedValue === 'undefined')
	var selectedValue;

async function joinTournament(code){
	console.log('je passe');
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${code}/`, 'POST');
		// const tournamentDiv = document.getElementById(`tournamentDiv${tournament.id}`);
		// console.log(tournament);
		// if (tournamentDiv)
		// 	tournamentDiv.innerText = `${tournament.name} (${tournament.n_participants + 1}/${tournament.size})`;
		// tournament = data;
		if (data.detail){
			document.getElementById('searchTournamentContextError').innerText = data.detail;
			return;
		}
		document.getElementById('chatsListView').style.display = 'none';
		document.getElementById('leaveTournament').style.display = 'block';
		tournament = data;
		setBanOption();
		loadTournament(data);
	}
	catch (error){	
		console.log(error);
	}
}

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
				console.log(tournament);
				let tournamentDiv = document.createElement('div');
				tournamentDiv.classList.add('tournament-div');
				tournamentDiv.id = `tournamentDiv${tournament.code}`
				tournamentDiv.innerText = `${tournament.name} (${tournament.n_participants}/${tournament.size})`;
				tempDiv.appendChild(tournamentDiv);
			}
		}
		document.getElementById('tournamentsList').innerHTML = tempDiv.innerHTML;
		const tournamentDivs = document.querySelectorAll('.tournament-div');
		for (tournamentDiv of tournamentDivs){
			tournamentDiv.addEventListener('click', function () {
				const code = this.id.slice(-4);
				joinTournament(code);
			})
		}
	}
	catch (error){
		console.log(error);
	}
});

if (typeof clickedUserDiv === 'undefined')
	var clickedUserDiv;

function setBanOption(){
	const banDiv = document.getElementById('cBan');
	if (tournament.created_by !== userInformations.id){
		banDiv.classList.add('disabled');
	}
	else{
		if (banDiv.classList.contains('disabled'))
			banDiv.classList.remove('disabled');
	}
}

document.getElementById('cBan').addEventListener('click', async ()=> {
	const playerId = clickedUserDiv.id.substring(12);
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${tournament.code}/ban/${playerId}/`, 'DELETE');
    }
    catch(error){
        console.log(error);
    }
})

document.getElementById('cFriendRequest').addEventListener('click', async () => {
    const friendRequestUsername = clickedUserDiv.innerText;
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/friend_requests/`, 'POST', undefined, undefined, {
            'username' : friendRequestUsername,
        })
        const validator = document.getElementById('friendRequestValidator');
        validator.style.removeProperty('display');
        setTimeout(()=> validator.style.display='none', 1500);
    }
    catch (error){
        console.log(error);
    }
})

document.getElementById('cBlock').addEventListener('click', async () => {
    const blockedUserId = clickedUserDiv.id.substring(12);
    try {
        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/blocked/`, 'POST', undefined, undefined, {
            'user_id' : blockedUserId
        })
    }
    catch (error){
        console.log(error);
    }
})


function addParticipant(participant){
	const tournamentViewDiv = document.getElementById('tournamentView');
	const participantDiv = document.createElement('div');
	participantDiv.id = `tParticipant${participant.id}`;
	participantDiv.classList.add('tournament-participant');
	participantDiv.innerText = participant.username;
	tournamentViewDiv.appendChild(participantDiv);
	if (participant.id !== userInformations.id){
		participantDiv.addEventListener('contextmenu', function(e) {
			e.preventDefault();
			clickedUserDiv = this;
			const contextMenu = document.getElementById('contextMenu');
			contextMenu.style.left = `${e.pageX}px`;
			contextMenu.style.top = `${e.pageY}px`;
			contextMenu.style.display = 'block';
		});
	}
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
	await navigateTo('/');
	displayMainAlert('Banned', event.message);
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


function createBracket(data) {
	const bracketDiv = document.getElementById('bracket');
	bracketDiv.innerHTML = '';
	const rounds = ['sixteenth-final' ,'eighth-final', 'quarter-final', 'semi-final', 'final'];
	let firstPassed = false;

	rounds.forEach(roundName => {
		const matches = data.matches[roundName] || [];
		if (matches.length)
			firstPassed = true;

		if (firstPassed){
			var roundDiv = document.createElement('div');
			roundDiv.className = 'round';
	
			var titleDiv = document.createElement('h5');
			titleDiv.className = 'text-center mb-4';
			titleDiv.textContent = roundName.replace('-', ' ').toUpperCase();
			roundDiv.appendChild(titleDiv);
			var roundInsideDiv = document.createElement('div');
			roundInsideDiv.className = 'round-inside';
			roundDiv.appendChild(roundInsideDiv);
		}

		matches.forEach(match => {
			const matchDiv = document.createElement('div');
			matchDiv.className = 'match';

			const card = document.createElement('div');
			card.className = 'card';
			if (match === null){
				const player1Div = document.createElement('div');
				player1Div.className = 'card-body border-bottom';
				player1Div.innerHTML = `
					<div class="d-flex justify-content-between">
						<span>to be defined</span>
					</div>
				`;
	
				const player2Div = document.createElement('div');
				player2Div.className = 'card-body';
				player2Div.innerHTML = `
					<div class="d-flex justify-content-between">
						<span>to be defined</span>
					</div>
				`;
	
				card.appendChild(player1Div);
				card.appendChild(player2Div);
				matchDiv.appendChild(card);
				roundInsideDiv.appendChild(matchDiv);
			}
			else {
				let score = match.winner === match.user_1?.id ? match.score_winner : match.score_looser;
				if (score === null)
					score = '';
				const player1Div = document.createElement('div');
				player1Div.className = `card-body border-bottom ${match.winner === match.user_1?.id ? 'winner' : ''}`;
				player1Div.innerHTML = `
					<div class="d-flex justify-content-between">
						<img class="tournament-participant-pp" src="/assets/imageNotFound.png"></img>
						<span>${match.user_1?.username}</span>
						<span class="fw-bold">${score}</span>
					</div>
				`;
	
				const player2Div = document.createElement('div');
				score = match.winner === match.user_2?.id ? match.score_winner : match.score_looser;
				if (score === null)
					score = '';
				player2Div.className = `card-body ${match.winner === match.user_2?.id ? 'winner' : ''}`;
				player2Div.innerHTML = `
					<div class="d-flex justify-content-between">
						<img class="tournament-participant-pp" src="/assets/imageNotFound.png"></img>
						<span>${match.user_2?.username}</span>
						<span class="fw-bold">${score}</span>
					</div>
				`;
	
				card.appendChild(player1Div);
				card.appendChild(player2Div);
				matchDiv.appendChild(card);
				roundInsideDiv.appendChild(matchDiv);
			}
		});
		if (firstPassed)
			bracketDiv.appendChild(roundDiv);
	});
}

function tournamentStart(event){
	event = JSON.parse(event.data);
	console.log(event);
	loadTournament(event.data);
	// if (!event.data.matches['semi-final']){
	// 	event.data.matches['semi-final'] = [];
	// 	for (i = 0; i < event.data.matches['quarter-final'].length / 2; ++i)
	// 		event.data.matches['semi-final'].push(null);
	// }
	// if (!event.data.matches['final']){
	// 	event.data.matches['final'] = [];
	// 	for (i = 0; i < event.data.matches['semi-final'].length / 2; ++i)
	// 		event.data.matches['final'].push(null);
	// }
	// console.log(event.data.matches);
	// document.getElementById('tournamentView').innerHTML = '';
	// createBracket(event.data);
}

function updateMatchFromWinnerId(id, data){
	for (round in tournament.matches){
		for (let match in tournament.matches[round]){
			match = tournament.matches[round][match];
			if (match.finished)
				continue;
			if (match.user_1.id === id || match.user_2.id === id){
				match.score_winner = data.score_winner;
				match.score_looser = data.score_looser;
				match.reason = data.reason;
				match.finished = true;
				match.winner = id;
			}
		}
	}
}

async function tournamentMatchFinished(event){
	event = JSON.parse(event.data);
	console.log('received match finished event');
	console.log(event);
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`);
		tournament = data;
		setBanOption()
		loadTournament(data);
	}
	catch(error){
		if (error.code === 404)
			document.getElementById('bracket').innerHTML = '';
		console.log(error);
	}
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

	if (!SSEListeners.has('tournament-ban')){
        SSEListeners.set('tournament-ban', tournamentBanned);
        sse.addEventListener('tournament-ban', tournamentBanned);
    }

	if (!SSEListeners.has('tournament-start-at')){
        SSEListeners.set('tournament-start-at', tournamentStartAt);
        sse.addEventListener('tournament-start-at', tournamentStartAt);
    }

	if (!SSEListeners.has('tournament-start-cancel')){
        SSEListeners.set('tournament-start-cancel', tournamentStartCancel);
        sse.addEventListener('tournament-start-cancel', tournamentStartCancel);
    }

	if (!SSEListeners.has('tournament-start')){
        SSEListeners.set('tournament-start', tournamentStart);
        sse.addEventListener('tournament-start', tournamentStart);
    }

	if (!SSEListeners.has('tournament-match-finish')){
		SSEListeners.set('tournament-match-finish', tournamentMatchFinished);
        sse.addEventListener('tournament-match-finish', tournamentMatchFinished);
	}
}

function loadTournament(tournament){
	document.getElementById('tournamentView').innerHTML = '';
	for (i in tournament.participants){
		let participant = tournament.participants[i];
		addParticipant(participant);
	}
	addTournamentSSEListeners();
	if (tournament.matches){
		if (!tournament.matches['semi-final']|| !tournament.matches['semi-final'].length){
			tournament.matches['semi-final'] = [];
			for (i = 0; i < tournament.matches['quarter-final'].length / 2; ++i)
				tournament.matches['semi-final'].push(null);
		}
		if (!tournament.matches['final'] || !tournament.matches['final'].length){
			tournament.matches['final'] = [];
			for (i = 0; i < tournament.matches['semi-final'].length / 2; ++i)
				tournament.matches['final'].push(null);
		}
		console.log(tournament.matches);
		document.getElementById('tournamentView').innerHTML = '';
		createBracket(tournament);
	}
}

document.getElementById('searchTournamentForm').addEventListener('submit', async (e) => {
	e.preventDefault();
	const tournamentName = document.getElementById('searchTournament').value;
	if (tournaments.count !== 0){
		for (i in tournaments.results){
			let tournament = tournaments.results[i];
			if (tournament.name === tournamentName){
				return joinTournament(tournament.code);
			}
		}
	}
	const createTournamentModal = new bootstrap.Modal(document.getElementById('createTournamentModal'));
	document.getElementById('tournamentName').value = tournamentName;
	createTournamentModal.show();
});

// document.getElementById('rangeInput').addEventListener('input', e => {
// 	document.getElementById('tournamentSize').innerText = `Select size (${e.target.value})`;	
// })

document.getElementById('createTournament').addEventListener('click', async event => {
	event.preventDefault();
	const createTournamentModal = bootstrap.Modal.getOrCreateInstance('#createTournamentModal');
	const tournamentName = document.getElementById('tournamentName').value;
	const tournamentSize = selectedValue;
	try { 
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`, 'POST', undefined, undefined, {
			'name' : tournamentName,
			'size' : tournamentSize
		});
		console.log(data);
		if (data.detail || (data.name && !data.id)){
			document.getElementById('createTournamentError').innerText = data.detail ?? data.name;
			setTimeout(() => {
				document.getElementById('createTournamentError').innerText = '';
			}, 2500);
			return;
		}
		document.getElementById('chatsListView').style.display = 'none';
		document.getElementById('leaveTournament').style.display = 'block';
		createTournamentModal.hide();
		tournament = data;
		setBanOption();
		loadTournament(data);
	}
	catch (error){
		console.log(error);
	}
})

document.getElementById('leaveTournament').addEventListener('click', () => {
	leaveTournament();
})

async function leaveTournament(){
	if (!tournament) return;
	const tournamentViewDiv = document.getElementById('tournamentView');
	if (tournamentViewDiv) tournamentViewDiv.innerHTML = '';
	try {
		await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${tournament.code}/`, 'DELETE');
		document.getElementById('chatsListView').style.display = 'block';
		document.getElementById('leaveTournament').style.display = 'none';
	}
	catch (error){
		console.log(error);
	}
}

function setTournamentOptions(){
	const options = document.querySelectorAll('.option');
	selectedValue = 16;

	options.forEach(option => {
  		if (option.dataset.value == selectedValue) {
    		option.classList.add('selected');
  		}
  
  		option.addEventListener('click', () => {
			options.forEach(opt => opt.classList.remove('selected'));
			option.classList.add('selected');
			selectedValue = option.dataset.value;
 		});
	});
}

if (typeof tournamentData === 'undefined')
	var tournamentData;

async function gameStart(event) {
	event = JSON.parse(event.data);
	if (!checkEventDuplication(event)) return;
	console.log('game-start received (tournament)',event);
	if (fromTournament)
		userInformations.cancelReturn = true;
	fromTournament = true;
	tournamentData = event.data;
	await navigateTo('/game/tournament');
}

async function initTournament(){
	document.getElementById('chatsListView').style.display = 'block';
	document.getElementById('leaveTournament').style.display = 'none';
	fromTournament = false;
	userInformations.cancelReturn = false;
    await indexInit(false);
	if (window.location.pathname === '/')
		return;
	if (userInformations.is_guest){
		await navigateTo('/');
		return displayMainAlert('Error', 'You do not have permission to play in tournaments');
	}
	loadCSS('/tournament/css/tournament.css', false);
	setTournamentOptions();

	if (SSEListeners.has('game-start')){
		// console.log('je remove :', SSEListeners.get('game-start'));
        sse.removeEventListener('game-start', SSEListeners.get('game-start'));
        SSEListeners.delete('game-start');
    }
	SSEListeners.set('game-start', gameStart);
	sse.addEventListener('game-start', gameStart);

	document.getElementById('tournamentsList').addEventListener('click', async (e) => {
		const tournamentDiv = e.target.closest('.tournament-div');
		if (!tournamentDiv) return;
		
		const cTournament = tournaments.results.find(t => 
			`tournamentDiv${t.id}` === tournamentDiv.id
		);
		if (!cTournament) return;
		
		try {
			let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${cTournament.code}/`, 'POST');
			tournamentDiv.innerText = `${cTournament.name} (${cTournament.n_participants + 1}/${cTournament.size})`;
			if (data.detail)
				console.log(data.detail);
			else{
				tournament = data;
				setBanOption();
				document.getElementById('chatsListView').style.display = 'none';
				document.getElementById('leaveTournament').style.display = 'block';
				loadTournament(data);
			}
		} catch (error) {
			console.log(error);
		}
	});
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`);
		tournament = data;
		setBanOption()
		console.log(data);
		loadTournament(data);
		console.log('je cache')
		document.getElementById('chatsListView').style.display = 'none';
		document.getElementById('leaveTournament').style.display = 'block';
	}
	catch(error) {
		console.log(error);
	}
	// createBracket(dataTest);
}

initTournament();