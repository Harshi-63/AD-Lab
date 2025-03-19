const backendURL = "http://127.0.0.1:5000"; // Flask backend URL

async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const statusMessage = document.getElementById("uploadStatus");
    const filePreview = document.getElementById("filePreview");

    if (!fileInput.files.length) {
        alert("Please select a file first.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        statusMessage.innerText = "Uploading file...";
        statusMessage.style.color = "blue";

        // Send request to backend
        const response = await fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        console.log("Upload Response:", result);

        if (response.ok) {
            statusMessage.innerText = result.message || "File uploaded successfully!";
            statusMessage.style.color = "green";

            // Preview the uploaded document
            previewDocument(file, filePreview);
        } else {
            statusMessage.innerText = result.error || "File upload failed.";
            statusMessage.style.color = "red";
        }
    } catch (error) {
        console.error("Upload error:", error);
        statusMessage.innerText = "Upload failed. Check console.";
        statusMessage.style.color = "red";
    }
}
function previewDocument(file, previewElement) {
    const fileURL = URL.createObjectURL(file);
    const fileExtension = file.name.split('.').pop().toLowerCase();

    if (fileExtension === "pdf") {
        previewElement.innerHTML = `<iframe src="${fileURL}" width="100%" height="400px"></iframe>`;
    } else if (fileExtension === "docx" || fileExtension === "doc") {
        previewElement.innerHTML = `<p>Preview not supported for Word files. Download it <a href="${fileURL}" target="_blank">here</a>.</p>`;
    } else if (fileExtension === "xls" || fileExtension === "xlsx") {
        previewElement.innerHTML = `<p>Preview not supported for Excel files. Download it <a href="${fileURL}" target="_blank">here</a>.</p>`;
    } else {
        previewElement.innerHTML = `<p>Unsupported file format.</p>`;
    }
}

// Function to send query to chatbot
async function sendQuery() {
    const queryInput = document.getElementById("queryInput").value;
    const chatResponse = document.getElementById("chatResponse"); // Chat response display

    if (!queryInput.trim()) {
        alert("Please enter a query!");
        return;
    }

    try {
        chatResponse.innerText = "Thinking...";
        chatResponse.style.color = "blue";

        const response = await fetch(`${backendURL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: queryInput }),
        });

        const result = await response.json();
        console.log("Chat Response:", result);

        if (response.ok) {
            chatResponse.innerText = result.response || "No response from chatbot.";
            chatResponse.style.color = "green";
        } else {
            chatResponse.innerText = result.error || "Error processing query.";
            chatResponse.style.color = "red";
        }
    } catch (error) {
        console.error("Chat error:", error);
        chatResponse.innerText = "Chat failed. Check console.";
        chatResponse.style.color = "red";
    }
}