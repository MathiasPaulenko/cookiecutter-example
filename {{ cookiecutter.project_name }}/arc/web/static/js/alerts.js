async function showPopup(title, text, icon, buttonMessage, showConfirmButton) {
    await Swal.fire({
      title: title,
      text: text,
      icon: icon,
      confirmButtonText: buttonMessage,
      showConfirmButton: showConfirmButton
    });
}


async function showNotification(title, text, icon, timer, buttonNotificationMessage, showConfirmButton, timerProgressBar, position) {
  if (typeof title === 'string') {
    await Swal.fire({
        title: title,
        text: text,
        icon: icon,
        timer: timer,
        confirmButtonText: buttonNotificationMessage,
        showConfirmButton: showConfirmButton, // bool
        timerProgressBar: timerProgressBar, // bool
        // width: "em",
        heightAuto: false,
        toast: true,
        position: position,
        didOpen: (toast) => {
          toast.addEventListener('mouseenter', Swal.stopTimer)
          toast.addEventListener('mouseleave', Swal.resumeTimer)
        },
        hideClass: {
          popup: '',
          backdrop: ''
        }
      });
  }
  else if (Array.isArray(title)) {
    for (const current_title of title) {
      await Swal.fire({
        title: current_title,
        text: text,
        icon: icon,
        timer: timer,
        confirmButtonText: buttonNotificationMessage,
        showConfirmButton: showConfirmButton, // bool
        timerProgressBar: timerProgressBar, // bool
        // width: "em",
        heightAuto: false,
        toast: true,
        position: position,
        didOpen: (toast) => {
          toast.addEventListener('mouseenter', Swal.stopTimer)
          toast.addEventListener('mouseleave', Swal.resumeTimer)
        },
        hideClass: {
          popup: '',
          backdrop: ''
        }
      });
    }
  }
}

function goBack() {
  window.history.back();
}