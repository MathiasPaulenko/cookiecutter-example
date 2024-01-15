$(document).ready(() => {
    if (portal_running === 'True' && pid > 0) {
        waitUntilNoElement();
    }
});

function waitUntilNoElement(callback){
    if ($(".swal2-container").length){
        setTimeout(function() {
            waitUntilNoElement();
        }, 1000);
    }else{
        showAlertRunning();
    }
}

function showAlertRunning() {
    Swal.fire({
        title: 'Execution in progress...',
        text: 'Do you want to open log console?',
        icon: 'info',
        confirmButtonText: 'View log console',
        showConfirmButton: true,
    }).then((willConfirm) => {
        if (willConfirm.isConfirmed) {
            window.location.href = '/view-executions';
        }
    });
}