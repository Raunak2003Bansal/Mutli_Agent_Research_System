async function runResearch() {
    const topic = document.getElementById("topic").value;

    if (!topic.trim()) {
        alert("Please enter a research topic.");
        return;
    }

    // Reset UI
    document.getElementById("output").style.display = "none";
    document.getElementById("output").innerText = "";
    document.getElementById("error").style.display = "none";
    document.getElementById("loading").style.display = "block";

    try {
        const response = await fetch("/submit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic: topic })
        });

        const data = await response.json();

        document.getElementById("loading").style.display = "none";

        if (data.error) {
            document.getElementById("error").style.display = "block";
            document.getElementById("error").innerText = "❌ " + data.error;
        } else {
            document.getElementById("output").style.display = "block";
            document.getElementById("output").innerText = data.message;
        }

    } catch (error) {
        document.getElementById("loading").style.display = "none";
        document.getElementById("error").style.display = "block";
        document.getElementById("error").innerText = "❌ Error: " + error.message;
    }
}