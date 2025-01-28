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
            if (data?.password)
                document.getElementById('pContextError').innerText = data.password;
            else if (data?.detail)
                document.getElementById('pContextError').innerText = data.detail;
            else if (!data){
                sse.close();
                deleteModal.hide();
                sse = undefined;
                removeTokens();
                closeChatView();
                await generateToken();
                initSSE();
                await fetchUserInfos(true);
                await navigateTo('/');
                setTimeout(()=> {
                    displayMainAlert('Account deleted', 'Your account has been successfully deleted. You have been redirected to homepage.');
                }, 300);
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

document.getElementById('changeProfilePic').addEventListener('click', async ()=> {
    try {
        let data = await apiRequest(getAccessToken(), `${baseAPIUrl}/users/profile-pictures/`)
        const profilePicContainer = document.getElementById('profilePicContainer');
        profilePicContainer.innerHTML = '';
        for (i in data){
            let profilePic = data[i];
            const profilePicDiv = document.createElement('div');
            profilePicDiv.classList.add('profile-pic-div');
            profilePicDiv.setAttribute('data-bs-toggle', 'popover');
            profilePicDiv.setAttribute('data-bs-trigger', 'hover');
            profilePicDiv.setAttribute('data-bs-placement', 'top');
            profilePicDiv.setAttribute('data-bs-content', `${profilePic.name} (${profilePic.unlock_reason.slice(0, -1)})`);
            profilePicDiv.innerHTML = `
            <img src=${profilePic.small} style='cursor: ${profilePic.unlock ? "pointer" : "not-allowed;filter: grayscale(90%);"}'
            class="${profilePic.is_equiped ? 'border border-warning border-2 m-1' : 'm-1'}">
            `
            if (profilePic.unlock && !profilePic.is_equiped){
                profilePicDiv.addEventListener('click', async ()=> {
                    try {
                        await apiRequest(getAccessToken(), `${baseAPIUrl}/users/profile-picture/${profilePic.id}/`, 'PUT');
                        handleRoute();
                    }
                    catch(error){
                        console.log(error);
                    }
                })
            }
            profilePicContainer.appendChild(profilePicDiv);
        }
        const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
        popovers.forEach((popover) => {
            new bootstrap.Popover(popover);
        });
    }
    catch(error){
        console.log(error)
    }
    const changeProfilePicModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('pChangeProfilePictureModal'));
    changeProfilePicModal.show();
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
        const blob = await response.blob();
        
        const fileURL = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = fileURL;

        const contentDisposition = response.headers.get('Content-Disposition');
        const filename = contentDisposition
            ? contentDisposition.split('filename=')[1].replace(/["']/g, '')
            : 'your_data.json';
            
        link.download = filename;
        link.click();
        URL.revokeObjectURL(fileURL);
    } catch (error) {
        console.error('error:', error);
    }
});

function fillNicknamePlaceholder() {
    document.getElementById('pNicknameInput').placeholder = userInformations.username;
}

function setChatAcceptationOptions(){
	const options = document.getElementById('options').querySelectorAll('.option');
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

function fillBanner(){
    const usernameDiv = document.getElementById('bUsername');
    usernameDiv.innerText = userInformations.username;
    const profilePicDiv = document.getElementById('pProfilePicture');
    profilePicDiv.innerHTML = `
    <img class="rounded-1" src="${userInformations.profile_picture?.small}" onerror="src='/assets/imageNotFound.png'">
    `
}

async function accountInit(){
    if (userInformations.is_guest){
        document.getElementById('pDeleteAccount').classList.add('disabled');
    }
    await fetchUserInfos(true);
    fillBanner();
    fillNicknamePlaceholder();
    setChatAcceptationOptions();
} 

accountInit();