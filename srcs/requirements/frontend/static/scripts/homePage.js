function checkAuthentication(){
    if (!localStorage.getItem('token'))
        navigateTo("login");
}

document.getElementById('logoutButton').addEventListener('click', () => {
    getDataFromApi(undefined, `${baseAPIUrl}/auth/guest/`, "POST")
        .then(data => {
            if (data.access) {
                removeTokens();
                localStorage.setItem('temp_refresh', data.refresh);
                localStorage.setItem('temp_token', data.access);
                navigateTo('/login');
                // fillGuestPlaceHolder();
            }
            else
                console.log('error a gerer', data);
        })
        .catch(error => {
            console.log('error a gerer1', error);
        })
})

checkAuthentication();