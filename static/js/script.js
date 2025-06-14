document.addEventListener("DOMContentLoaded", function () {
    const downloadForm = document.getElementById("downloadForm");

    if (downloadForm) {
        downloadForm.addEventListener("submit", function (e) {
            // Optional: validate selection
            const itag = document.getElementById("video-resolutions").value;
            const url = document.getElementById("youtube_url").value;

            document.getElementById("hidden_resolution").value = itag;
            document.getElementById("hidden_url").value = url;

            // Let it submit normally (browser handles download)
        });
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const checkForm = document.getElementById("checkForm");
    const downloadForm = document.getElementById("downloadForm");

    // Handle check form (fetch video info)
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

    // Handle download form (download video)
    if (downloadForm) {
        downloadForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const url = document.getElementById("hidden_url").value;
            const itag = document.getElementById("video-resolutions").value;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            if (!url || !itag) {
                alert("Please select a resolution.");
                return;
            }

            document.getElementById("hidden_resolution").value = itag;
            document.getElementById("progress-container").style.display = "block";

            fetch("/download/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
                body: new URLSearchParams({
                    youtube_url: url,
                    resolution: itag,
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("✅ Download complete!");
                } else {
                    alert("❌ " + data.error);
                }
            })
            .catch(err => {
                alert("❌ An error occurred during download.");
                console.error(err);
            });

            // Simulate fake progress
            let i = 0;
            const interval = setInterval(() => {
                i += 5;
                if (i > 100) i = 100;
                document.getElementById("download-progress").value = i;
                document.getElementById("progress-text").textContent = `${i}%`;
                if (i === 100) clearInterval(interval);
            }, 300);
        });
    }
});
