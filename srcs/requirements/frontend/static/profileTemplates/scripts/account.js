document.getElementById('pDeleteAccount').addEventListener('click', event => {
    event.preventDefault();
    const deleteAccountModal = new bootstrap.Modal(document.getElementById('pDeleteAccountModal'));
    deleteAccountModal.show();
    window.deleteModal = deleteAccountModal;
})

async function deleteAccount(password) {
    getDataFromApi(getAccessToken(), `${baseAPIUrl}/users/me/`, 'DELETE', undefined, undefined, {
        'password' : password
    })
        .then(async data => {
            if (data?.password){
                document.getElementById('pContextError').innerText = data.password;
            }
            else if (!data){
                deleteModal.hide();
                removeTokens();
                await generateToken();
                navigateTo('/');
                displayMainError('Account deleted', 'Your account has been successfully deleted. You have been redirected to homepage.');
            }
        })
        .catch(error => {
            console.log('error', error)
        })
}

document.getElementById('test').addEventListener('submit', event => {
    event.preventDefault();
    deleteAccount(document.getElementById('pConfirmDeletion').value);
})

document.getElementById('pChangeNickname').addEventListener('submit', async event => {
    event.preventDefault();
    const newUsername = document.getElementById('pNicknameInput').value;
    if (!newUsername)
        return; 
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
        undefined, undefined, {'username' : newUsername});
        if (!data.id)
            document.getElementById('container').innerText = data.username;
        else 
            navigateTo('/profile');
    }
    catch (error){
        console.log('error on username change', error);
    }
})

document.getElementById('pChangePassword').addEventListener('submit', async event => {
    event.preventDefault();
    const newPassword = document.getElementById('pPasswordInput').value;
    if (!newPassword)
        return;
    if (newPassword === 'Password123')
        return document.getElementById('container').innerText = 'Please enter a new password';
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
        undefined, undefined, {'password' : newPassword});
        if (!data.id)
            document.getElementById('container').innerText = data.username;
        else 
            navigateTo('/profile');
    }
    catch (error){
        console.log('error on password change', error);
    }
})

document.getElementById('pPasswordInput').addEventListener('focus', function clearInput(event) {
    event.preventDefault();
    this.value = "";
})

document.getElementById('pPasswordInput').addEventListener('focusout', function fillInput(event) {
    event.preventDefault();
    this.value = "Password123";
})

function fillNicknamePlaceholder() {
    document.getElementById('pNicknameInput').placeholder = userInformations.username;
}

async function atStart(){
    await fetchUserInfos(true);
    fillNicknamePlaceholder();
} 

atStart();