document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach((alert) => {
        window.setTimeout(() => {
            const closeButton = alert.querySelector(".btn-close");
            if (closeButton) {
                closeButton.click();
            }
        }, 7000);
    });
});
