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

            alert("ATS Score : " + data.ats_score + "%");

            console.log("Matched Skills:", data.matched_skills);

            console.log("Missing Skills:", data.missing_skills);

            console.log("Recommended Skills:", data.recommended_skills);

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