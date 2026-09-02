function copyToClipboard(elementId, button) {
    const copyElement = document.getElementById(elementId);

    if (!copyElement) {
        console.error(`Element with ID "${elementId}" not found.`);
        return;
    }

    const text = copyElement.value || copyElement.textContent;
    const icon = button.querySelector("i");

    navigator.clipboard.writeText(text.trim()).then(
        function () {
            if (icon) {
                icon.classList.remove("bi-clipboard");
                icon.classList.add("bi-clipboard-check");

                setTimeout(function () {
                    icon.classList.remove("bi-clipboard-check");
                    icon.classList.add("bi-clipboard");
                }, 2000);
            }
        },
        function (err) {
            console.error("Could not copy text: ", err);
        }
    );
}