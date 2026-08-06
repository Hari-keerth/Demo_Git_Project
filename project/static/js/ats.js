// =========================================
// DOM Elements
// =========================================

const fileInput = document.getElementById("resume");
const fileName = document.getElementById("file-name");

const loading = document.getElementById("loading");
const resultSection = document.getElementById("ats-result");

const scoreElement = document.getElementById("ats-score");

const matchedSkillsContainer =
    document.getElementById("matched-skills");

const missingSkillsContainer =
    document.getElementById("missing-skills");

const recommendedSkillsContainer =
    document.getElementById("recommended-skills");


// =========================================
// File Upload
// =========================================

fileInput.addEventListener("change", () => {

    if (fileInput.files.length > 0) {

        fileName.textContent = fileInput.files[0].name;

    }

    else {

        fileName.textContent = "No file selected";

    }

});


// =========================================
// CSRF Token
// =========================================

function getCSRFToken() {

    return document.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;

}


// =========================================
// Skill Chip
// =========================================

function createSkillChip(skill) {

    const chip = document.createElement("span");

    chip.className = "skill-chip";

    chip.textContent = skill;

    return chip;

}


// =========================================
// Display Skills
// =========================================

function displaySkills(container, skills) {

    container.innerHTML = "";

    if (!skills || skills.length === 0) {

        container.innerHTML =
            "<span class='skill-chip'>No Skills Found</span>";

        return;

    }

    skills.forEach(skill => {

        container.appendChild(
            createSkillChip(skill)
        );

    });

}


// =========================================
// Display Bullet List
// =========================================

function displayList(elementId, items) {

    const container = document.getElementById(elementId);

    if (!container) return;

    container.innerHTML = "";

    if (!items || items.length === 0) {

        container.innerHTML = "<li>-</li>";

        return;

    }

    items.forEach(item => {

        const li = document.createElement("li");

        li.textContent = item;

        container.appendChild(li);

    });

}


// =========================================
// Display Text
// =========================================

function displayText(elementId, text) {

    const element = document.getElementById(elementId);

    if (!element) return;

    element.textContent = text || "-";

}


// =========================================
// Animate Score
// =========================================

function animateScore(target) {

    let current = 0;

    scoreElement.textContent = "0%";

    const timer = setInterval(() => {

        current++;

        scoreElement.textContent = current + "%";

        if (current >= target) {

            clearInterval(timer);

        }

    }, 15);

}


// =========================================
// Calculate ATS Score
// =========================================

async function calculate_ats_score() {

    const resume = fileInput.files[0];

    const jobDescription =
        document.getElementById("job_description")
        .value
        .trim();

    if (!resume) {

        alert("Please upload your resume.");

        return;

    }

    if (!jobDescription) {

        alert("Please paste the Job Description.");

        return;

    }

    const formData = new FormData();

    formData.append("resume", resume);

    formData.append("job_description", jobDescription);

    loading.style.display = "block";

    resultSection.style.display = "none";

    try {

        const response = await fetch(

            "/calculate-ats/",

            {

                method: "POST",

                headers: {

                    "X-CSRFToken": getCSRFToken()

                },

                body: formData

            }

        );

        const data = await response.json();

        loading.style.display = "none";

        console.log(data);

        if (!data.success) {

            alert(

                data.error ||

                data.message ||

                "ATS Analysis Failed."

            );

            return;

        }

        resultSection.style.display = "block";

        animateScore(

            Math.round(data.ats_score)

        );

        // Skills

        displaySkills(

            matchedSkillsContainer,

            data.matched_skills

        );

        displaySkills(

            missingSkillsContainer,

            data.missing_skills

        );

        displaySkills(

            recommendedSkillsContainer,

            data.recommended_skills

        );

        // Lists

        displayList(

            "strengths-list",

            data.strengths

        );

        displayList(

            "improvement-list",

            data.improvements

        );

        // Text Sections

        displayText(

            "overall-match",

            data.overall_match

        );

        displayText(

            "experience-analysis",

            data.experience_analysis

        );

        displayText(

            "project-analysis",

            data.project_analysis

        );

        displayText(

            "education-analysis",

            data.education_analysis

        );

        displayText(

            "resume-quality",

            data.resume_quality

        );

        displayText(

            "ats-compatibility",

            data.ats_compatibility

        );

        displayText(

            "summary",

            data.summary

        );

        displayText(

            "final-recommendation",

            data.final_recommendation

        );

        resultSection.scrollIntoView({

            behavior: "smooth"

        });

    }

    catch (error) {

        loading.style.display = "none";

        console.error(error);

        alert("Unable to analyze resume.");

    }

}