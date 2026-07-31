/*=========================================================
                    SETTINGS
=========================================================*/

document.addEventListener("DOMContentLoaded",()=>{

    /*=====================================
                MODALS
    =====================================*/

    const modals =
        document.querySelectorAll(".modal");

    function openModal(id){

        document
            .getElementById(id)
            ?.classList.add("show");

        document.body.style.overflow="hidden";

    }

    function closeModal(id){

        document
            .getElementById(id)
            ?.classList.remove("show");

        document.body.style.overflow="";

    }

    document
        .getElementById("openPasswordModal")
        ?.addEventListener("click",()=>{

            openModal("passwordModal");

        });

    document
        .getElementById("openDeleteModal")
        ?.addEventListener("click",()=>{

            openModal("deleteModal");

        });

    document
        .querySelectorAll(".close-modal")
        .forEach(btn=>{

            btn.addEventListener("click",()=>{

                closeModal(

                    btn.dataset.close

                );

            });

        });

    modals.forEach(modal=>{

        modal.addEventListener("click",e=>{

            if(e.target===modal){

                modal.classList.remove("show");

                document.body.style.overflow="";

            }

        });

    });

    document.addEventListener("keydown",e=>{

        if(e.key==="Escape"){

            modals.forEach(modal=>{

                modal.classList.remove("show");

            });

            document.body.style.overflow="";

        }

    });

    /*=====================================
            DELETE VALIDATION
    =====================================*/

    const input =
        document.getElementById("deleteConfirm");

    const button =
        document.getElementById("confirmDelete");

    if(input){

        input.addEventListener("input",()=>{

            button.disabled =

                input.value.trim()!=="DELETE";

        });

    }

});