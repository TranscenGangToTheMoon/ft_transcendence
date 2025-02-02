if (typeof tournaments === 'undefined')
	var tournaments;
if (typeof tournament === 'undefined')
	var tournament;
if (typeof selectedValue === 'undefined')
	var selectedValue;
if (typeof emptyMatch === 'undefined'){
	var emptyMatch = {
		"id": 31,
		"n": 1,
		"match_code": null,
		"score_winner": null,
		"score_looser": null,
		"finish_reason": null,
		"finished": false,
	}
}

async function joinTournament(code){
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/${code}/`, 'POST');
		if (data.detail){
			document.getElementById('searchTournamentContextError').innerText = data.detail;
			return 0;
		}
		if (window.location.pathname !== '/tournament/' + code)
			navigateTo('/tournament/' + code, false, true);
		document.getElementById('chatsListView').style.display = 'none';
		document.getElementById('leaveTournament').style.display = 'block';
		tournament = data;
		setBanOption();
		loadTournament(data);
	}
	catch (error){
		displayMainAlert('Error', 'This tournament does not exists.', 'error', 5000);
		console.log(error);
		return 0;
	}
	return 1;
}

async function searchForTournament(filter){
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/search/?q=${filter}`);
		const tempDiv = document.createElement('div');
		tournaments = data;
		if (data.count){
			for (i in data.results){
				let tournament = data.results[i];
				let tournamentDiv = document.createElement('div');
				tournamentDiv.className = 'btn btn-dark m-1 d-flex justify-content-center tournament-div';
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
}

document.getElementById('searchTournamentForm').addEventListener('keyup', async (e) => {
	e.preventDefault();
	if (e.key === 'Enter') return;
	await searchForTournament(e.target.value);
});

if (typeof clickedUserDiv === 'undefined')
	var clickedUserDiv;

function setBanOption(){
	const banDiv = document.getElementById('cBan');
	if (!banDiv) return;
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
	participantDiv.className = 'tournament-participant';
	participantDiv.innerHTML = `
		<img class="profile-pic-medium" src="${participant['profile_picture'].small}" 
		onerror="this.onerror=null; this.src='/assets/imageNotFound.png'" 
		alt="profile pic">
		<div class='trunc-username'>
			${participant.username}
		</div>
	`
	tournamentViewDiv.appendChild(participantDiv);
	if (participant.id !== userInformations.id){
		participantDiv.addEventListener('contextmenu', function(e) {
			e.preventDefault();
			console.log('test');
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

function displayCountdown(){
	// return;
	const countdownElement = document.getElementById('tMainCountdown');
	const backdrop = document.getElementById('tBackdrop');

	let counter = 2;

        // Show the backdrop
	backdrop.classList.replace('d-none', 'd-flex');

	// Start the countdown
	const interval = setInterval(() => {
		countdownElement.textContent = counter;
		counter--;

		if (counter < 0) {
			clearInterval(interval);

			// Hide the backdrop when countdown ends
			backdrop.classList.replace('d-flex', 'd-none');
			// alert('Tournament Started!');
		}
	}, 1000); // Update every 1 second
}

function tournamentJoined(event){
	event = JSON.parse(event.data);
	displayGameChatNotif(event, false);
	addParticipant(event.data);
}

function tournamentLeaved(event){
	event = JSON.parse(event.data);
	displayGameChatNotif(event, false);
	removeParticipant(event.data.id)
}

async function tournamentBanned(event){
	event = JSON.parse(event.data);
	displayGameChatNotif(event, false);
	console.log(event);
	await navigateTo('/');
	displayMainAlert('Banned', event.message, 'warning', 5000);
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
			displayGameChatNotif({'message':"Starting Soon!"}, false);
			clearInterval(timer);
			return;
		}
		
		countdownDiv.innerHTML = `Starting in: ${difference}s`;
		displayGameChatNotif({'message':`Starting in: ${difference}s`}, false);
	}

	updateCountdown();
	const timer = setInterval(updateCountdown, 1000);
}

function tournamentStartCancel(){
	const countdownDiv = document.getElementById('tCountdown');
	if (countdownDiv)
		countdownDiv.remove();
}

function tournamentStart(event){
	displayGameChatNotif({'message':":Tournament begins"}, false);
	displayCountdown();
	event = JSON.parse(event.data);
	loadTournament(event.data);
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
	tournament = event.data;
	displayGameChatNotif(event, false);
	setBanOption();
	loadTournament(tournament);
}

if( typeof clickedUserDiv !== 'undefined')
    var clickedUserDiv;

document.getElementById('cSpectate').addEventListener('click', async () => {
    navigateTo('/spectate/' + clickedUserDiv.code);
})

async function updateAvailableSpectateMatches(event){
    event = JSON.parse(event.data);
    const contextMenuSpectate = document.getElementById('contextMenuSpectate');
    const matches = document.querySelectorAll('.t-match')
    for (let match of matches){
        let id = match.id.split('_')[1];
        if (event.data[id]) {
            match.code = event.data[id];
            match.addEventListener('contextmenu', function (e){
                e.preventDefault();
                clickedUserDiv = this;
                contextMenuSpectate.style.left = `${e.pageX}px`;
                contextMenuSpectate.style.top = `${e.pageY}px`;
                contextMenuSpectate.style.display = 'block';
            })
        }
    }
}

async function tournamentFinished(event){
	event = JSON.parse(event.data);
	closeGameChatTab();
	await navigateTo('/', true, true);
	displayNotification(undefined, 'tournament finished', event.message, undefined, undefined);
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

	if(!SSEListeners.has('tournament-message')){
        SSEListeners.set('tournament-message', displayGameChatMessage);
        sse.addEventListener('tournament-message', displayGameChatMessage);
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

	if (!SSEListeners.has('tournament-finish')){
		SSEListeners.set('tournament-finish', tournamentFinished);
        sse.addEventListener('tournament-finish', tournamentFinished);
	}
	
	if (!SSEListeners.has('tournament-available-spectate-matches')){
		SSEListeners.set('tournament-available-spectate-matches', updateAvailableSpectateMatches);
		sse.addEventListener('tournament-available-spectate-matches', updateAvailableSpectateMatches);
	}
}

function getMatch(i, lastRound, tournament){
    let result = {...emptyMatch};
    const lastRoundMatches = tournament.matches[lastRound];
    
    const matchingMatches = [lastRoundMatches[i * 2 - 2], lastRoundMatches[i * 2 - 1]];
    
    for (let j in matchingMatches){
        const match = matchingMatches[j];
        let matchWinnerId = match.winner;
        
        if (!matchWinnerId || matchWinnerId === null){
            result[`user_${parseInt(j) + 1}`] = null;
            continue;
        }
        if (match.user_1 && match.user_1.id == matchWinnerId) {
            result[`user_${parseInt(j) + 1}`] = match.user_1;
        } else if (match.user_2 && match.user_2.id == matchWinnerId) {
            result[`user_${parseInt(j) + 1}`] = match.user_2;
        }
    }
    
    return result;
}

function loadTournament(tournament){
	localStorage.setItem('lobbyCode', '/tournament/' + tournament.code);
	if (window.location.pathname === '/game/tournament') return;
	document.getElementById('tournamentView').innerHTML = '';
	for (i in tournament.participants){
		let participant = tournament.participants[i];
		addParticipant(participant);
	}
	if (tournament.matches != null){
		document.getElementById('leaveTournament').style.display = 'none';
		if ((!tournament.matches['quarter-final']|| !tournament.matches['quarter-final'].length)
			&& tournament.matches['round-of-16']
		){
			tournament.matches['quarter-final'] = [];
			for (i = 0; i < tournament.matches['round-of-16'].length / 2; ++i)
				tournament.matches['quarter-final'].push(getMatch(i+1, 'round-of-16', tournament));
		} 
		if ((!tournament.matches['semi-final']|| !tournament.matches['semi-final'].length)
			&& tournament.matches['quarter-final']
		){
			tournament.matches['semi-final'] = [];
			for (i = 0; i < tournament.matches['quarter-final'].length / 2; ++i)
				tournament.matches['semi-final'].push(getMatch(i+1, 'quarter-final', tournament));
		}
		if ((!tournament.matches['final'] || !tournament.matches['final'].length)
				&& tournament.matches['semi-final']
			){
				tournament.matches['final'] = [];
				for (i = 0; i < tournament.matches['semi-final'].length / 2; ++i)
					tournament.matches['final'].push(getMatch(i+1, 'semi-final', tournament));
			}
			document.getElementById('tournamentView').innerHTML = '';
			createBracket(tournament);
	}
	openGameChatTab({'type': 'tournament', 'code': tournament.code});
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
		if (window.location.pathname !== '/tournament/' + tournament.code)
			navigateTo('/tournament/' + tournament.code, false, true);
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
	navigateTo('/tournament');
}

function setTournamentOptions(){
	const options = document.querySelectorAll('.option');
	selectedValue = 8;

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
	localStorage.setItem('tournament-code', tournament.code);
	if (fromTournament)
		userInformations.cancelReturn = true;
	fromTournament = true;
	tournamentData = [event.data, event.target[0].url, event.target[0].type];
	localStorage.setItem('game-event', JSON.stringify(event));
	await navigateTo('/game/tournament', true, true);
}

async function initTournament(){
	addTournamentSSEListeners();
	await loadScript('/tournament/scripts/createBracket.js');
	document.getElementById('chatsListView').style.display = 'block';
	document.getElementById('leaveTournament').style.display = 'none';
	fromTournament = false;
	userInformations.cancelReturn = false;
    await indexInit(false);
	if (window.location.pathname === '/')
		return;
	loadCSS('/tournament/css/tournament.css', false);
	setTournamentOptions();
	await searchForTournament('');
	if (SSEListeners.has('game-start')){
        sse.removeEventListener('game-start', SSEListeners.get('game-start'));
        SSEListeners.delete('game-start');
    }
	SSEListeners.set('game-start', gameStart);
	sse.addEventListener('game-start', gameStart);
	const oldTournamentCode = localStorage.getItem('tournament-code-reconnect');
	if (oldTournamentCode){
		localStorage.removeItem('tournament-code');
		localStorage.removeItem('tournament-code-reconnect');
		if (joinTournament(oldTournamentCode))
			return;
	}
	let tournamentCode = window.location.pathname.split('/')[2];
	try {
		let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/play/tournament/`);
		tournament = data;
		if (window.location.pathname !== '/tournament/' + tournament.code)
			navigateTo('/tournament/' + tournament.code, false, true);
		setBanOption()
		loadTournament(data);
		document.getElementById('chatsListView').style.display = 'none';
		document.getElementById('leaveTournament').style.display = 'block';
	}
	catch(error) {
		if (error.code === 404 && tournamentCode){
			if (!await joinTournament(tournamentCode))
				await navigateTo('/tournament', true, true);
		}
		console.log(error);
	}
	// createBracket(dataTest);
}

initTournament();