document.addEventListener("click", function(event) {
    if (event.target.matches("button[id^='copy_btn_']")) {
        const btn = event.target;
        const content = btn.getAttribute("data-content");
        if (content) {
            navigator.clipboard.writeText(content)
                .then(() => {
                    btn.innerText = "✅ Copié !";
                    setTimeout(() => btn.innerText = "📋 Copier", 1200);
                })
                .catch(err => console.error("Clipboard error:", err));
        } else {
            console.error("No data-content attribute found on button.");
        }
    }
});