async function loadGameStats(){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/stats/`);
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