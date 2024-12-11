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
                await fetchUserInfos(true);
                await navigateTo('/');
                displayMainAlert('Account deleted', 'Your account has been successfully deleted. You have been redirected to homepage.');
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
            document.getElementById('pChangeNicknameError').innerText = data.username;
        else {
            await fetchUserInfos(true);
            await indexInit(false);
            displayMainAlert("Nickname updated", `Successfully updated your nickname to '${newUsername}'`)
            handleRoute();
        }
    }
    catch (error){
        console.log('error on username change', error);
    }
})

document.getElementById('pChangePassword').addEventListener('submit', async event => {
    event.preventDefault();
    const newPasswordInputDiv = document.getElementById('pPasswordInput');
    const newPassword = newPasswordInputDiv.value;
    if (!newPassword)
        return;
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
        undefined, undefined, {'password' : newPassword});
        if (!data.id){
            document.getElementById('pChangePasswordError').innerText = data.username;
            let error = data.detail ? data.detail : data.password;
            if (error)
                document.getElementById('pChangePasswordError').innerText = error;
            
        }
        else{
            displayMainAlert("password updated", "successfully updated your password.");
            newPasswordInputDiv.value = "";
        }
    }
    catch (error){
        console.log('error on password change', error);
    }
})

function fillNicknamePlaceholder() {
    document.getElementById('pNicknameInput').placeholder = userInformations.username;
}

async function accountInit(){
    if (userInformations.is_guest){
        document.getElementById('pDeleteAccount').classList.add('disabled');
    }
    fillNicknamePlaceholder();
} 

accountInit();