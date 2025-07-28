async function uploadFile(event) {
    if(event) event.preventDefault();

    const input = document.getElementById("fileInput");
    const file = input.files[0];
    const resultDiv = document.getElementById("uploadResult");

    if (!file) {
        resultDiv.innerText = "❌ Please select a file to upload.";
        return;
    }
    
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.innerHTML = `✅ Upload success: <code>${data.filename}</code>`;
        } else {
            resultDiv.innerText = `❌ Upload failed: File rejected.`;
        }
    } catch (error) {
        resultDiv.innerText = `❌ Upload failed: Unexpected error.`;
    }
}


async function showMySubmissions(event) {
    if (event) event.preventDefault();

    const gallery = document.getElementById("imageGallery");
    gallery.innerHTML = ""; 

    try {
        const response = await fetch("/uploads"); 
        const files = await response.json(); 

        for (const filename of files) {
            const ext = filename.slice(filename.lastIndexOf(".")).toLowerCase();

            if (ext === ".jpg" || ext === ".png") {
                const img = document.createElement("img");
                img.src = `/uploads/${filename}`;
                img.alt = filename;
                img.style.maxWidth = "300px";
                img.style.margin = "10px";
                gallery.appendChild(img);
            }
            else if (ext === ".txt"){
                const link = document.createElement("a");
                link.href =  `/uploads/${filename}`;
                link.textContent = `${filename}`;
                link.target = "_blank";
                link.style.display = "block";
                link.style.margin = "5px 0";
                gallery.appendChild(link);
            }
        }
    } catch (error) {
        gallery.innerText = `❌ Failed to load submissions: ${error}`;
    }
}


async function askChatbot(event) {
    if (event) event.preventDefault();
    
    const input = document.getElementById("promptInput");
    const prompt = input.value.trim();
    const responseDiv = document.getElementById("chatbotResponse");

    if (!prompt) {
        responseDiv.innerText = "❌ Please enter a prompt.";
        return;
    }

    try {
        const response = await fetch("/llm", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt: prompt })
        });

        const data = await response.json();

        if (response.ok) {
            responseDiv.innerHTML = `<b>🟢 MatchaBot:</b> ${data.response}`;
        } else {
            responseDiv.innerHTML = `<b>🔴 Error:</b> ${data.error}`;
        }
    } catch (error) {
        responseDiv.innerHTML = `<b>🔴 Network Error:</b> ${error}`;
    }
}
