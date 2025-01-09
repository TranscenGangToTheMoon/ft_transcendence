async function loadGameStats(){
    try {
        let data = apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/stats/`);
        console.log(data);
    }
    catch (error){
        console.log(error);
    }
}

async function initStatistics(){
    await loadGameStats();
}

initStatistics();