async function atStart() {
    await fetchUserInfos(true);
    await loadUserProfile();
}

atStart();