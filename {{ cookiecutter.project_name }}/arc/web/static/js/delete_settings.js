$(document).ready(()=>{
    let deleteModal = document.getElementById('deleteSettingModal');
    deleteModal.addEventListener('show.bs.modal', function (event) {
      // Button that triggered the modal
      let button = event.relatedTarget;
      // Extract info from data-bs-* attributes
      let settingName = button.getAttribute('data-bs-setting-name');
      let settingId = button.getAttribute('data-bs-setting-id');
      // Update the modal's content.
      let modalTitle= deleteModal.querySelector('.modal-title');
      let modalBodyConfirmation= deleteModal.querySelector('.modal-body-confirmation');
      let modalForm= deleteModal.querySelector('#deleteSettingForm');

      modalTitle.textContent = modalTitle.textContent + `'${settingName}'`
      modalBodyConfirmation.textContent = modalBodyConfirmation.textContent + `'${settingName}'`
      modalForm.action = modalForm.action + settingId + "/"
    })
});