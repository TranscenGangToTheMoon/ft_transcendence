async function forceReloadGuestToken() {
    try {
        let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST')
        if (data.access){
            localStorage.setItem('token', data.access);
            return data.access;
        }
        else
            console.log('error', data);
    }
    catch (error) {
        console.log('error', error);
    }
}

async function generateToken() {
    try {
        let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, "POST");
        if (data.access) {
            localStorage.setItem('token', data.access);
            localStorage.setItem('refresh', data.refresh);
        }
        else
            console.log('error', data);
    }
    catch(error){
        console.log('error', error)
    }
}

async function relog(){
    // if (window.location.pathname !== '/')
    //     await navigateTo('/');
    await generateToken();
    displayMainAlert("Unable to retrieve your account/guest profile","We're sorry your account has been permanently deleted and cannot be recovered.");
    throw new Error('relog');
    // await fetchUserInfos();
    // await loadUserProfile();
}

async function refreshToken(token) {
    var refresh = getRefreshToken();
    try {
        console.log('token expired. refreshing.')
        let data = await apiRequest(token, `${baseAPIUrl}/auth/refresh/`, 'POST', undefined, undefined, {'refresh':refresh}, true)
        if (data.access) {
            token = data.access;
            localStorage.setItem('token', token);
            // localStorage.setItem('refresh', token);
            return token;
        }
        else {
            console.log('refresh token expired must relog')
            await relog();
        }
    }
    catch (error) {
        if (error.message === 'relog')
            throw error;
        else
            console.log("ERROR", error);
    }
}

function getAccessToken() {
    return localStorage.getItem('token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh');
}

function removeTokens() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh');
}