document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("attendanceForm");
    const nameInput = document.getElementById("name");

    if (form && nameInput) {
        // Focus name input on load
        nameInput.focus();

        // Prevent double submit
        form.addEventListener("submit", function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.textContent = "Submitting...";
            }
        });

        // Trim name on input
        nameInput.addEventListener("blur", function () {
            this.value = this.value.trim();
        });
    }

    // Auto-hide flash messages after 4 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.4s";
            alert.style.opacity = "0";
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 4000);
    });
});