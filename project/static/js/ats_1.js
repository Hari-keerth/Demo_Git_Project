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