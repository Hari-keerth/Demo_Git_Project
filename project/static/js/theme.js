/*=========================================================
                    THEME
=========================================================*/

document.addEventListener("DOMContentLoaded",()=>{

    const html =
        document.documentElement;

    const cards =
        document.querySelectorAll(".theme-option");

    function getSystemTheme(){

        return window.matchMedia(
            "(prefers-color-scheme: dark)"
        ).matches
            ? "dark"
            : "light";

    }

    function applyTheme(theme){

        if(theme==="system"){

            html.setAttribute(
                "data-theme",
                getSystemTheme()
            );

        }

        else{

            html.setAttribute(
                "data-theme",
                theme
            );

        }

    }

    function updateActive(theme){

        cards.forEach(card=>{

            card.classList.toggle(

                "active",

                card.dataset.theme===theme

            );

        });

    }

    let savedTheme =
        localStorage.getItem("theme") || "system";

    applyTheme(savedTheme);

    updateActive(savedTheme);

    cards.forEach(card=>{

        card.addEventListener("click",()=>{

            const theme =
                card.dataset.theme;

            localStorage.setItem(
                "theme",
                theme
            );

            applyTheme(theme);

            updateActive(theme);

        });

    });

    window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).addEventListener("change",()=>{

        if(

            localStorage.getItem("theme")==="system"

        ){

            applyTheme("system");

        }

    });

});