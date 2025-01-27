function historyBracket(matches, roundInsideDiv){
    matches.forEach(match => {
        const matchDiv = document.createElement('div');
        matchDiv.className = 'match';
        const card = document.createElement('div');
        card.className = 'card';
        
        let profilePicPath = match.winner?.profile_picture?.small;
        const player1Div = document.createElement('div');
        player1Div.className = `card-body border-bottom winner`;
        player1Div.innerHTML = `
            <div class="d-flex justify-content-between">
                ${match.winner? '<img class="tournament-participant-pp" src="'+ profilePicPath
                    +'" onerror="src=`/assets/imageNotFound.png`"></img>' : ''}
                <span>${match.winner?.username ?? 'to be defined'}</span>
            </div>
        `;

        const player2Div = document.createElement('div');
        profilePicPath = match.looser?.profile_picture?.small;

        player2Div.className = `card-body`;
        player2Div.innerHTML = `
            <div class="d-flex justify-content-between">
                ${match.looser? '<img class="tournament-participant-pp" src="'+ profilePicPath
                    +'" onerror="src=`/assets/imageNotFound.png`"></img>' : ''}
                <span>${match.looser?.username ?? 'to be defined'}</span>
            </div>
        `;

        card.appendChild(player1Div);
        card.appendChild(player2Div);
        matchDiv.appendChild(card);
        roundInsideDiv.appendChild(matchDiv);
    });
}

function createBracket(data, history=false) {
	const bracketDiv = document.getElementById('bracket');
	bracketDiv.innerHTML = '';
	const rounds = ['round of 16', 'quarter-final', 'semi-final', 'final'];
	let firstPassed = false;

	rounds.forEach(roundName => {
		const matches = data.matches[roundName] || [];
		if (matches.length)
			firstPassed = true;

		if (firstPassed){
			var roundDiv = document.createElement('div');
			roundDiv.className = 'round col';
	
			var titleDiv = document.createElement('h5');
			titleDiv.className = 'text-center mb-4';
			titleDiv.textContent = roundName.replace('-', ' ').toUpperCase();
			roundDiv.appendChild(titleDiv);
			var roundInsideDiv = document.createElement('div');
			roundInsideDiv.className = 'round-inside';
			roundDiv.appendChild(roundInsideDiv);
		}

        if (history)
            historyBracket(matches, roundInsideDiv)
        else{

            matches.forEach(match => {
                const matchDiv = document.createElement('div');
                matchDiv.className = 't-match';
                matchDiv.id = `match_${match.id}`;
                const card = document.createElement('div');
                card.className = 'card';
                
                let score = match.winner === match.user_1?.id ? match.score_winner : match.score_looser;
                if (score === null)
                    score = '';
                const player1Div = document.createElement('div');
                player1Div.className = `card-body border-bottom ${match.winner !== undefined
                                        && match.winner === match.user_1?.id ? 'winner' : ''}`;
                let profilePicPath = match.user_1?.profile_picture?.small;
                player1Div.innerHTML = `
                    <div class="d-flex justify-content-between">
                        ${match.user_1? '<img class="tournament-participant-pp" src="'+ profilePicPath
                            +'" onerror="src=`/assets/imageNotFound.png`"></img>' : ''}
                        <span>${match.user_1?.username ?? 'to be defined'}</span>
                        <span class="fw-bold">${score}</span>
                    </div>
                `;
    
                score = match.winner === match.user_2?.id ? match.score_winner : match.score_looser;
                if (score === null)
                    score = '';
                const player2Div = document.createElement('div');
                player2Div.className = `card-body border-bottom ${match.winner !== undefined
                                        && match.winner === match.user_2?.id ? 'winner' : ''}`;
                profilePicPath = match.user_2?.profile_picture?.small;
                player2Div.innerHTML = `
                    <div class="d-flex justify-content-between">
                    ${match.user_2? '<img class="tournament-participant-pp" src="' + profilePicPath
                        +'" onerror="src=`/assets/imageNotFound.png`"></img>' : ''}
                        <span>${match.user_2?.username ?? 'to be defined'}</span>
                        <span class="fw-bold">${score}</span>
                    </div>
                `;
    
                card.appendChild(player1Div);
                card.appendChild(player2Div);
                matchDiv.appendChild(card);
                roundInsideDiv.appendChild(matchDiv);
            });
        }
		if (firstPassed)
			bracketDiv.appendChild(roundDiv);
	});
}