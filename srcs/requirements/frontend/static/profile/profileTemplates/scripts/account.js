if (typeof selectedValue === 'undefined'){
    var selectedValue;
}

document.getElementById('pDeleteAccount').addEventListener('click', event => {
    event.preventDefault();
    const deleteAccountModal = new bootstrap.Modal(document.getElementById('pDeleteAccountModal'));
    deleteAccountModal.show();
    window.deleteModal = deleteAccountModal;
})

document.getElementById('pChangePassword').addEventListener('click', event => {
    event.preventDefault();
    const changePasswordModal = new bootstrap.Modal(document.getElementById('pChangePasswordModal'));
    changePasswordModal.show();
    window.changePasswordModal = changePasswordModal;
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
                sse.close();
                removeTokens();
                await generateToken();
                initSSE();
                await fetchUserInfos(true);
                await navigateTo('/');
                setTimeout(()=> {
                    displayMainAlert('Account deleted', 'Your account has been successfully deleted. You have been redirected to homepage.');
                }, 500);
            }
        })
        .catch(error => {
            console.log('error', error)
        })
}

async function changePassword(new_password, old_password){
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, "PATCH",
        undefined, undefined, {'password' : new_password, 'old_password' : old_password});
        if (!data.id){
            let error = data.detail ?? data.password;
            if (error){
                document.getElementById('pChangePasswordError').innerText = error;
                changePasswordModal.hide();
            }
            error = data.old_password;
            if (error)
                document.getElementById('pChangeContextError').innerText = error;
        }
        else{
            changePasswordModal.hide();
            document.getElementById('pChangePasswordError').innerText = "";
            document.getElementById('pChangeContextError').innerText = "";
            document.getElementById('pPasswordInput').value = "";
            setTimeout(() => {
                displayMainAlert("password updated", "successfully updated your password.");
            }, 500);
        }
    }
    catch (error){
        console.log('error on password change', error);
    }
}

document.getElementById('deleteAccountConfirm').addEventListener('submit', event => {
    event.preventDefault();
    deleteAccount(document.getElementById('pConfirmDeletion').value);
})

document.getElementById('changePasswordConfirm').addEventListener('submit', event => {
    event.preventDefault();
    changePassword(document.getElementById('pPasswordInput').value, document.getElementById('pConfirmPassword').value);
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
            document.getElementById('pChangeNicknameError').innerText = "";
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

document.getElementById('pDownloadData').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/users/me/download-data/', {
            method: 'GET',
            headers: {
                Authorization: 'Bearer ' + getAccessToken(),
                'Content-Type': 'application/json',
                // Remove Content-Type since we're expecting a file, not JSON
            }
        });

        if (!response.ok) {
            throw new Error(`Error while downloading: ${response.statusText}`);
        }

        // Get the file directly as blob instead of parsing as JSON
        const blob = await response.blob();
        
        // Create download link
        const fileURL = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = fileURL;
        
        // Get filename from Content-Disposition header if available
        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition
            ? contentDisposition.split('filename=')[1].replace(/["']/g, '')
            : 'your_data.json';
            
        link.download = filename;
        link.click();
        URL.revokeObjectURL(fileURL);
    } catch (error) {
        console.error('Erreur:', error);
    }
});

function fillNicknamePlaceholder() {
    document.getElementById('pNicknameInput').placeholder = userInformations.username;
}

function setChatAcceptationOptions(){
	const options = document.querySelectorAll('.option');
	selectedValue = userInformations.accept_chat_from;

	options.forEach(option => {
  		if (option.dataset.value == selectedValue) {
    		option.classList.add('selected');
  		}
  
  		option.addEventListener('click', async () => {
            try {
                await apiRequest(getAccessToken(), `${baseAPIUrl}/users/me/`, 'PATCH', undefined, undefined, {
                    'accept_chat_from': option.dataset.value,
                })
                options.forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                selectedValue = option.dataset.value;
            }
            catch(error){
                console.log(error);
            }
 		});
	});
}

async function accountInit(){
    if (userInformations.is_guest){
        document.getElementById('pDeleteAccount').classList.add('disabled');
    }
    fillNicknamePlaceholder();
    setChatAcceptationOptions();
} 

accountInit();