// ===============================
// Show Selected File Name
// ===============================

function updateFileName(input) {

    const fileName = document.getElementById("file-name");

    if (input.files.length > 0) {
        fileName.innerHTML = input.files[0].name;
    } else {
        fileName.innerHTML = "No file selected";
    }

}


// ===============================
// Get CSRF Token
// ===============================

function getCSRFToken() {

    return document.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;

}


// ===============================
// Calculate ATS Score
// ===============================

function calculate_ats_score() {

    const resume =
        document.getElementById("resume").files[0];

    const jobDescription =
        document.getElementById("job_description").value;

    if (!resume) {

        alert("Please upload your Resume.");

        return;

    }

    if (jobDescription.trim() === "") {

        alert("Please paste the Job Description.");

        return;

    }

    const formData = new FormData();

    formData.append("resume", resume);

    formData.append("job_description", jobDescription);


    fetch("/calculate-ats/", {

        method: "POST",

        headers: {

            "X-CSRFToken": getCSRFToken()

        },

        body: formData

    })

    .then(response => response.json())

    .then(data => {

        console.log(data);

        if (data.success) {

            document.getElementById("loading").style.display = "none";

            document.getElementById("ats-result").style.display = "block";

            document.getElementById("ats-score").innerHTML =
                Math.round(data.ats_score) + "%";


            displaySkills(
                document.getElementById("matched-skills"),
                data.matched_skills
            );

            displaySkills(
                document.getElementById("missing-skills"),
                data.missing_skills
            );

            displaySkills(
                document.getElementById("recommended-skills"),
                data.recommended_skills
            );

            document.getElementById("ats-result").scrollIntoView({

                behavior: "smooth"

            });

        }

        else {

            alert(data.message);

        }

    })

    .catch(error => {

        console.error(error);

        alert("Error calculating ATS Score.");

    });

}

// ===============================
// Display Skills
// ===============================

function displaySkills(elementId, skills) {

    const container = document.getElementById(elementId);

    container.innerHTML = "";


    if (!skills || skills.length === 0) {

        container.innerHTML =

            "<span class='skill-chip'>No Skills Found</span>";

        return;

    }


    skills.forEach(skill => {

        const chip = document.createElement("span");

        chip.className = "skill-chip";

        chip.innerHTML = skill;

        container.appendChild(chip);

    });

}

// ==========================
// DOM Elements
// ==========================

const form = document.getElementById("atsForm");

const fileInput = document.getElementById("resume");

const fileName = document.getElementById("file-name");

const loading = document.getElementById("loading");

const resultSection = document.getElementById("ats-result");

const scoreElement = document.getElementById("ats-score");

const matchedSkills = document.getElementById("matched-skills");

const missingSkills = document.getElementById("missing-skills");

const recommendedSkills = document.getElementById("recommended-skills");

// ==========================
// Show Selected Resume Name
// ==========================

fileInput.addEventListener("change", () => {

    if(fileInput.files.length){

        fileName.textContent = fileInput.files[0].name;

    }

    else{

        fileName.textContent = "No file selected";

    }

});

// ==========================
// Create Skill Chip
// ==========================

function createSkillChip(skill){

    const chip = document.createElement("span");

    chip.className = "skill-chip";

    chip.textContent = skill;

    return chip;

}

// ==========================
// Display Skill List
// ==========================

function displaySkills(container,data){

    container.innerHTML = "";

    if(data.length === 0){

        container.innerHTML =

            "<span class='empty-chip'>No Skills Found</span>";

        return;

    }

    data.forEach(skill=>{

        container.appendChild(

            createSkillChip(skill)

        );

    });

}

// ==========================
// Animate ATS Score
// ==========================

function animateScore(target){

    let current = 0;

    scoreElement.innerHTML = "0%";

    const timer = setInterval(()=>{

        current++;

        scoreElement.innerHTML = current + "%";

        if(current >= target){

            clearInterval(timer);

        }

    },15);

}