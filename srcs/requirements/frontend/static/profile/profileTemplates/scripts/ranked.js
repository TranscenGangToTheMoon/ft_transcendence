async function loadRankedStats(){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/stats/ranked/`);
        // console.log('cestla',data);
    }
    catch (error){
        console.log(error);
    }
}

async function initStatistics(){
    await loadRankedStats();
}

initStatistics();