// ==============================================
// DOM ELEMENTS
// ==============================================

const generateBtn = document.getElementById("generateBtn");
const downloadBtn = document.getElementById("downloadBtn");
const copyBtn = document.getElementById("copyBtn");
const loading = document.getElementById("loading");
const resumePreview = document.getElementById("resumePreview");

// ==============================================
// CSRF TOKEN
// ==============================================

function getCSRFToken() {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith("csrftoken=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring("csrftoken=".length)
                );

                break;
            }
        }
    }

    return cookieValue;
}

// ==============================================
// GENERATE RESUME
// ==============================================

generateBtn.addEventListener("click", generateResume);

async function generateResume() {

    generateBtn.disabled = true;
    loading.classList.add("active");

    try {

        const formData = {

            resume_type: document.getElementById("resumeType").value,

            personal_info: document.getElementById("personalInfo").value,

            education: document.getElementById("education").value,

            experience: document.getElementById("experience").value,

            projects: document.getElementById("projects").value,

            skills: document.getElementById("skills").value,

            extracurricular: document.getElementById("extracurricular").value

        };

        const response = await fetch("/generate-resume/", {

            method: "POST",

            headers: {

                "Content-Type": "application/json",

                "X-CSRFToken": getCSRFToken()

            },

            body: JSON.stringify(formData)

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(data.error || "Something went wrong.");

        }

        let html = data.resume_html
            .replace(/```html/g, "")
            .replace(/```/g, "")
            .trim();

        resumePreview.innerHTML = html;

    }

    catch (error) {

        console.error(error);

        alert(error.message);

    }

    finally {

        loading.classList.remove("active");

        generateBtn.disabled = false;

    }

}

// ==============================================
// DOWNLOAD PDF
// ==============================================

downloadBtn.addEventListener("click", function () {

    if (resumePreview.innerHTML.trim() === "") {

        alert("Please generate a resume first.");

        return;

    }

    window.print();

});

// ==============================================
// EXPORT HTML
// ==============================================

copyBtn.addEventListener("click", function () {
  if (resumePreview.innerHTML.trim() === "") {
    alert("Please generate a resume first.");

    return;
  }

  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Resume</title>
<link rel="stylesheet" href="resume.css">
</head>
<body>

${resumePreview.innerHTML}

</body>
</html>`;

  navigator.clipboard.writeText(html);

  alert("HTML copied successfully.");
});

async function loadQuestion() {

    questionNo.innerText = `${currentQuestion} / ${totalQuestions}`;

    progressFill.style.width =
        `${(currentQuestion / totalQuestions) * 100}%`;

    answerBox.value = "";

    questionText.innerHTML = "Generating AI Question...";

    try {

        const response = await fetch("/generate-question/", {

            method: "POST",

            headers: {

                "Content-Type": "application/json",

                "X-CSRFToken": getCSRFToken()

            },

            body: JSON.stringify({

                role: document.getElementById("jobRole").value,

                asked_questions: questions

            })

        });

        const data = await response.json();

        if (data.success) {

            questionText.innerHTML = data.question;

            questions.push(data.question);

        } else {

            questionText.innerHTML = "Unable to generate question.";

        }

    } catch (error) {

        console.error(error);

        questionText.innerHTML = "Server Error.";

    }

}