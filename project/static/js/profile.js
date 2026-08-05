const resumeInput = document.getElementById("resume");

const fileName = document.getElementById("file-name");

resumeInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        fileName.textContent = this.files[0].name;

    } else {

        fileName.textContent = "No file selected";

    }

});