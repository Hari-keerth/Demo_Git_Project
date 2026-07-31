// =========================
// Update Selected File Name
// =========================

function updateFileName(input) {

    const fileName =
        document.getElementById("file-name");

    if (!fileName)
        return;

    if (input.files.length > 0) {

        fileName.textContent =
            input.files[0].name;

    } else {

        fileName.textContent =
            "No file selected";
    }
}

// =========================
// Enable / Disable Buttons
// =========================

function setButtonsDisabled(disabled) {

    document
        .querySelectorAll("button")
        .forEach(button => {

            button.disabled = disabled;

        });

}

// =========================
// Generate Documents
// =========================

async function generateDocuments() {

    const jobDescription =
        document
            .getElementById("job_description")
            .value
            .trim();

    const resumeFile =
        document
            .getElementById("resume")
            .files[0];

    if (!jobDescription || !resumeFile) {

        alert(
            "Please enter the Job Description and upload your Resume."
        );

        return null;
    }

    try {

        setButtonsDisabled(true);

        document.getElementById(
            "email_subject"
        ).value =
            "Generating...";

        document.getElementById(
            "email_body"
        ).value =
            "Generating...";

        document.getElementById(
            "cover_letter"
        ).value =
            "Generating...";

        const formData =
            new FormData();

        formData.append(
            "job_description",
            jobDescription
        );

        formData.append(
            "resume",
            resumeFile
        );

        const response =
            await fetch(
                "/generate/",
                {
                    method: "POST",
                    body: formData
                }
            );

        if (!response.ok) {

            throw new Error(
                `Server Error (${response.status})`
            );

        }

        const result =
            await response.json();

        if (result.error) {

            throw new Error(
                result.error
            );

        }

        document.getElementById(
            "email_subject"
        ).value =
            result.email_subject || "";

        document.getElementById(
            "email_body"
        ).value =
            result.email_body || "";

        document.getElementById(
            "cover_letter"
        ).value =
            result.cover_letter || "";

        return result;

    }

    catch (error) {

        console.error(error);

        document.getElementById(
            "email_subject"
        ).value =
            "Error";

        document.getElementById(
            "email_body"
        ).value =
            error.message;

        document.getElementById(
            "cover_letter"
        ).value =
            "Failed to generate.";

        return null;

    }

    finally {

        setButtonsDisabled(false);

    }

}

// =========================
// Send Application
// =========================

async function sendApplication() {

    const recruiterEmail =
        document
            .getElementById(
                "recruiter_email"
            )
            .value
            .trim();

    if (!recruiterEmail) {

        alert(
            "Please enter the recruiter email."
        );

        return;

    }

    const emailSubject =
        document
            .getElementById(
                "email_subject"
            )
            .value;

    const emailBody =
        document
            .getElementById(
                "email_body"
            )
            .value;

    const coverLetter =
        document
            .getElementById(
                "cover_letter"
            )
            .value;

    try {

        setButtonsDisabled(true);

        document.getElementById(
            "application_status"
        ).innerText =
            "Sending...";

        const response =
            await fetch(
                "/send-application/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        recruiter_email:
                            recruiterEmail,

                        email_subject:
                            emailSubject,

                        email_body:
                            emailBody,

                        cover_letter:
                            coverLetter

                    })

                }
            );

        const result = await response.json();

            if (!response.ok) {

                throw new Error(
                    result.error || `Server Error (${response.status})`
                );

            }


        document.getElementById(
            "application_status"
        ).innerText =
            result.message ||
            "Application Sent Successfully.";

    }

    catch (error) {

        console.error(error);

        document.getElementById(
            "application_status"
        ).innerText =
            error.message;

    }

    finally {

        setButtonsDisabled(false);

    }

}

// =========================
// Generate & Send
// =========================

async function generateAndSend() {

    const recruiterEmail =
        document
            .getElementById(
                "recruiter_email"
            )
            .value
            .trim();

    if (!recruiterEmail) {

        alert(
            "Please enter the recruiter email."
        );

        return;

    }

    const generated =
        await generateDocuments();

    if (!generated)
        return;

    await sendApplication();

}

// =========================
// Download Cover Letter PDF
// =========================

async function downloadCoverLetterPDF() {

    const coverLetter =
        document
            .getElementById(
                "cover_letter"
            )
            .value;

    if (
        !coverLetter ||
        coverLetter === "Generating..."
    ) {

        alert(
            "Generate the Cover Letter first."
        );

        return;

    }

    try {

        const response =
            await fetch(
                "/download-cover-letter-pdf/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        cover_letter:
                            coverLetter

                    })

                }
            );

        if (!response.ok) {

            throw new Error(
                "Failed to download Cover Letter."
            );

        }

        const blob =
            await response.blob();

        const url =
            window.URL.createObjectURL(blob);

        const a =
            document.createElement("a");

        a.href = url;

        a.download =
            "Cover_Letter.pdf";

        document.body.appendChild(a);

        a.click();

        a.remove();

        window.URL.revokeObjectURL(url);

    }

    catch (error) {

        alert(error.message);

    }

}

// =========================
// Download Email PDF
// =========================

async function downloadEmailPDF() {

    const emailSubject =
        document
            .getElementById(
                "email_subject"
            )
            .value;

    const emailBody =
        document
            .getElementById(
                "email_body"
            )
            .value;

    if (
        !emailBody ||
        emailBody === "Generating..."
    ) {

        alert(
            "Generate the Email first."
        );

        return;

    }

    try {

        const response =
            await fetch(
                "/download-email-pdf/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        email_subject:
                            emailSubject,

                        email_body:
                            emailBody

                    })

                }
            );

        if (!response.ok) {

            throw new Error(
                "Failed to download Email PDF."
            );

        }

        const blob =
            await response.blob();

        const url =
            window.URL.createObjectURL(blob);

        const a =
            document.createElement("a");

        a.href = url;

        a.download =
            "Application_Email.pdf";

        document.body.appendChild(a);

        a.click();

        a.remove();

        window.URL.revokeObjectURL(url);

    }

    catch (error) {

        alert(error.message);

    }

}

