document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(
        'form[action="/get_team_calendar"]'
    );
    const buttons = document.querySelectorAll(".team-card");
    const overlay = document.getElementById("loading-overlay");

    forms.forEach((form) => {
        form.addEventListener("submit", function () {
            // Disable all team cards.
            buttons.forEach((button) => {
                button.disabled = true;
            });

            // Show loading overlay.
            overlay.classList.add("is-visible");
            overlay.setAttribute("aria-hidden", "false");

            // Prevent further interaction with the page.
            document.body.classList.add("is-loading");
        });
    });
});