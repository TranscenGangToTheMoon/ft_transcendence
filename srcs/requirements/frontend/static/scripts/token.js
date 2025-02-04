async function forceReloadGuestToken() {
    try {
        let data = await apiRequest(undefined, `${baseAPIUrl}/auth/guest/`, 'POST')
        if (data.access){
            localStorage.setItem('token', data.access);
            return data.access;
        }
        else
            console.log(data);
    }
    catch (error) {
        console.log(error);
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
            console.log(data);
    }
    catch(error){
        console.log(error)
    }
}

async function relog(){
    await generateToken();
    displayMainAlert("Account Not Found", "We are unable to retrieve your account or guest profile.", 'warning', '4000');
    throw new Error('relog');
}

async function refreshToken(token) {
    var refresh = getRefreshToken();
    try {
        let data = await apiRequest(token, `${baseAPIUrl}/auth/refresh/`, 'POST', undefined, undefined, {'refresh':refresh}, true)
        if (data.access) {
            token = data.access;
            localStorage.setItem('token', token);
            // localStorage.setItem('refresh', token);
            return token;
        }
        else {
            await relog();
        }
    }
    catch (error) {
        if (error.message === 'relog')
            throw error;
        else
            console.log(error);
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