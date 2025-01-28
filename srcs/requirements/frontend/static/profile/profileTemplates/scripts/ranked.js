if (typeof nextRanked === 'undefined')
    var nextRanked;
if (typeof rankedData === 'undefined')
    var rankedData;
if (typeof chart === 'undefined')
    var chart;
if (typeof selectedGraph === 'undefined')
    var selectedGraph;
if (typeof defaultTrophiesMatch === 'undefined'){
    var defaultTrophiesMatch = {
        "id": 0,
        "trophies": 0,
        "total_trophies": 0,
        "at": "-",
        "user": 0
    }
}

async function getMatchesAfter(date){
    lastDataDate = new Date(rankedData.results.slice(-1)[0].at);
    while (nextRanked && lastDataDate >= date){
        try {
            let data = await apiRequest(getAccessToken(), nextRanked);
            nextRanked = data.next;
            rankedData.results.push(...data.results);
            lastDataDate = new Date(rankedData.results.slice(-1)[0].at);
        }
        catch (error){
            console.log(error);
        }
    }
    let results = [];
    let passed = false;
    rankedData.results.forEach(match => {
        matchDate = new Date(match.at);
        if (matchDate >= date){
            results.push(match);
            if (!passed){
                passed = true;
                const index = rankedData.results.findIndex(obj => obj.id === match.id);
                if (index){
                    previousRank = rankedData.results[index - 1];
                    let copy = {...previousRank};
                    copy.at = date;
                    results.unshift(copy);
                }
            }
        }
    });
    return results;
}

function filterDataForPeriod(data, period) {
    test = [...data];
    let filteredData = [];
    let seenDates = {};
    let simulationDate;
    if (period === "year") {
        for (let entry of data) {
            const date = new Date(entry.at);
            const year = date.getFullYear();
            const month = date.getMonth();

            seenDates[`${year}-${month}`] = entry;
        }

        filteredData = Object.values(seenDates);
        simulationDate = getLastYearDate();
    } else if (period === "month" || period === "week") {
        for (let entry of data) {
            const date = new Date(entry.at);
            const year = date.getFullYear();
            const month = date.getMonth();
            const day = date.getDate();

            const dayKey = `${year}-${month + 1}-${day}`;

            seenDates[dayKey] = entry;
        }

        filteredData = Object.values(seenDates);
        simulationDate = period === 'month' ? getLastMonthDate() : getLastWeekDate();

    } else if (period === "day") {
        filteredData = data;
        simulationDate = getLastDayDate();
    }
    if (filteredData.length === 1){
        defaultTrophiesMatch.at = simulationDate;
        filteredData.unshift(defaultTrophiesMatch);
    }
    return filteredData;
}

function getLastDayDate(){
    var today = new Date();
    const oneDayBefore = new Date(today);
    oneDayBefore.setDate(today.getDate() - 1);
    return oneDayBefore;
}

function getLastMonthDate(){
    var today = new Date();
    const oneMonthBefore = new Date(today);
    oneMonthBefore.setMonth(today.getMonth() - 1);
    return oneMonthBefore;
}

function getLastWeekDate(){
    var today = new Date();
    const sevenDaysBefore = new Date(today);
    sevenDaysBefore.setDate(today.getDate() - 7);
    return sevenDaysBefore;
}

function getLastYearDate(){
    var today = new Date();
    const oneYearBefore = new Date(today);
    oneYearBefore.setFullYear(today.getFullYear() - 1);
    return oneYearBefore;
}

function updateChart(trophiesChart, data, period) {

    const labels = data.map(item => {
        const date = new Date(item.at);
        switch (period) {
            case "day":
                return date.toLocaleTimeString(); // Heure pour le dernier jour
            case "week":
            case "month":
                return date.toLocaleDateString(); // Date pour semaine ou mois
            case "year":
                return date.toLocaleString('default', { month: 'short' }); // Mois pour l'année
            default:
                return date.toISOString();
        }
    });
    const totalTrophies = data.map(item => item.total_trophies);

    trophiesChart.data.labels = labels;
    trophiesChart.data.datasets[0].data = totalTrophies;
    trophiesChart.update();
}

function setGraph(data){
    const labels = data.map(item => new Date(item.at).toLocaleTimeString()); // Heures en format lisible
    const totalTrophies = data.map(item => item.total_trophies);

    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'trophies',
                data: totalTrophies,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Trophies'
                    },
                    beginAtZero: true
                }
            }
        }
    };

    const ctx = document.getElementById('trophiesChart').getContext('2d');
    const trophiesChart = new Chart(ctx, config);
    return trophiesChart;
}

async function loadRankedStats(){
    try {
        rankedData = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/stats/ranked/`);
        nextRanked = rankedData.next;
        let date = getLastDayDate();
        let data = await getMatchesAfter(date);
        chart = setGraph(data);
    }
    catch (error){
        console.log(error);
    }
}

async function changePeriod(period){
    let date;
    switch (period){
        case 'day':
            date = getLastDayDate();
            break;
        case 'week':
            date = getLastWeekDate();
            break;
        case 'month':
            date = getLastMonthDate();
            break;
        default:
            date = getLastYearDate();
            break;
    }
    let data = await getMatchesAfter(date);
    data = filterDataForPeriod(data, period);
    updateChart(chart, data, period);
}

function setGraphOptions(){
	const options = document.getElementById('selectGraph').querySelectorAll('.option');
	selectedGraph = 'day';

	options.forEach(option => {
  		if (option.dataset.value == selectedGraph) {
    		option.classList.add('selected');
  		}
  
  		option.addEventListener('click', async () => {
            options.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            selectedGraph = option.dataset.value;
            changePeriod(selectedGraph);
 		});
	});
}

async function initStatistics(){
    setGraphOptions();
    await loadRankedStats();
}

initStatistics();