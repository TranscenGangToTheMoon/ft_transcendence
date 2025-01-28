async function apiRequest(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined, currentlyRefreshing=false, nav=false){
    let options = {
        method: method,
        headers: {
            "content-type": contentType
        }
    }
    if (token && endpoint != `${baseAPIUrl}/auth/login/`)
        options.headers["Authorization"] = `${authType} ${token}`;
    if (body)
        options.body = JSON.stringify(body);
    removeAlert();
    return fetch(endpoint, options)
        .then(async response => {
            if (!response.ok && (response.status > 499 || response.status === 404)){
                throw {code: response.status};
            }
            if (response.status === 204){
                return;
            }
            let data = await response.json();
            if (data.code === 'token_not_valid') {
                if (currentlyRefreshing)
                    return {};
                token = await refreshToken(token);
                if (token) {
                    console.log('done, reposting request');
                    return apiRequest(token, endpoint, method, authType, contentType, body);
                }
            }
            return data;
        })
        .catch(async error =>{
            if (error.message === 'relog')
                return apiRequest(getAccessToken(), endpoint, method, authType, contentType, body);
            if (error.code === 502 || error.code === 503 || error.code === 500 || error.message === 'Failed to fetch'){
                closeExistingModals();
                console.log('service unavailable');
                const contentDiv = document.getElementById('content');
                removeAlert();
                const alertHtml = `
                <div class="alert alert-danger unavailable" role="alert">
                    Service unavailable
                </div>`;
                contentDiv.insertAdjacentHTML('beforebegin', alertHtml);
            }
            throw error;
        })
}

async function getDataFromApi(token, endpoint, method="GET", authType="Bearer",
    contentType="application/json", body=undefined){
    try {
        let data = await apiRequest(token, endpoint, method, authType, contentType, body);
        return data;
    }
    catch (error) {
        throw error;
    }
}

function removeAlert(){
    const existingAlert = document.querySelector('.unavailable');
    if (existingAlert)
        existingAlert.remove();
}