document.addEventListener("DOMContentLoaded", function () {
    const checkForm = document.getElementById("checkForm");
    const downloadForm = document.getElementById("downloadForm");

    // ✅ Fetch video info
    if (checkForm) {
        checkForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const urlInput = document.getElementById("youtube_url");
            const csrfTokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
            const fetchUrl = checkForm.dataset.fetchUrl;

            if (!urlInput || !csrfTokenInput || !fetchUrl) {
                alert("Missing form elements.");
                return;
            }

            const url = urlInput.value;
            const csrfToken = csrfTokenInput.value;

            document.getElementById("loading").style.display = "block";

            fetch(fetchUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ youtube_url: url }),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("loading").style.display = "none";

                if (data.success) {
                    document.getElementById("video-info").style.display = "block";
                    document.getElementById("video-title").textContent = data.title;
                    document.getElementById("video-thumb").src = data.thumbnail;
                    document.getElementById("hidden_url").value = url;

                    const dropdown = document.getElementById("video-resolutions");
                    dropdown.innerHTML = "";

                    data.formats.forEach(fmt => {
                        const option = document.createElement("option");
                        const filesize = fmt.filesize ? `${(fmt.filesize / 1024 / 1024).toFixed(2)} MB` : "Unknown size";
                        option.value = fmt.itag;
                        option.textContent = `${fmt.resolution || fmt.format_note} (${fmt.ext}, ${filesize})`;
                        dropdown.appendChild(option);
                    });
                } else {
                    alert(data.error || "Failed to fetch video info");
                }
            })
            .catch(err => {
                document.getElementById("loading").style.display = "none";
                alert("An error occurred while fetching video info.");
                console.error(err);
            });
        });
    }

    // ✅ Let browser handle video download via form submission
    if (downloadForm) {
        downloadForm.addEventListener("submit", function (e) {
            const url = document.getElementById("hidden_url").value;
            const itag = document.getElementById("video-resolutions").value;

            if (!url || !itag) {
                alert("Please select a resolution.");
                e.preventDefault(); // Prevent empty submission
                return;
            }

            // Fill hidden fields
            document.getElementById("hidden_resolution").value = itag;

            // ✅ Let browser handle file download via form submission to new tab
            // Do not prevent default! Let the form submit normally
            // Optional: Show loading spinner
            document.getElementById("download-spinner").style.display = "inline"; // if you have one
        });
    }
});
