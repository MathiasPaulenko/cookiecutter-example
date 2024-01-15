// sidebar js
document.addEventListener("DOMContentLoaded", function (event) {

    const showNavbar = (toggleId, navId, bodyId, headerId) => {
        const toggle = document.getElementById(toggleId),
            nav = document.getElementById(navId),
            bodypd = document.getElementById(bodyId)

        // Validate that all variables exist
        if (toggle && nav && bodypd) {
            toggle.addEventListener('click', () => {
                // show navbar
                nav.classList.toggle('reduced-sidebar')
                nav.classList.toggle('show')
                // change icon
                toggle.classList.toggle('bi-list')
                toggle.classList.toggle('bi-chevron-double-left')
                // add padding to body
                bodypd.classList.toggle('body-pd')
                // add padding to header
            })
        }
    }

    showNavbar('sidebar-toggle', 'sidebarMenu', 'body-pd')

    /*===== LINK ACTIVE =====*/
    const linkColor = document.querySelectorAll('.nav_link')

    function colorLink() {
        if (linkColor) {
            linkColor.forEach(l => l.classList.remove('active'))
            this.classList.add('active')
        }
    }

    linkColor.forEach(l => l.addEventListener('click', colorLink))

    // Your code to run since DOM is loaded and ready

    $("#color-mode").click((element)=>{
        fetch("/set_dark_mode/");
        $("body").toggleClass('dark-mode');
        $("#color-mode").toggleClass('bi-moon');
        $("#color-mode").toggleClass('bi-sun');
    });
});