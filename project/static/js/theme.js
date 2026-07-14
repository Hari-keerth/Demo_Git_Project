const toggle = document.getElementById("themeToggle");

const savedTheme = localStorage.getItem("theme");

if(savedTheme==="dark"){

    document.documentElement.setAttribute("data-theme","dark");

    toggle.checked=true;

}else{

    document.documentElement.setAttribute("data-theme","light");

}

toggle.addEventListener("change",function(){

    if(this.checked){

        document.documentElement.setAttribute("data-theme","dark");

        localStorage.setItem("theme","dark");

    }else{

        document.documentElement.setAttribute("data-theme","light");

        localStorage.setItem("theme","light");

    }

});