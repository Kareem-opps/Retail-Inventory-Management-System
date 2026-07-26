document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const sidebar = document.getElementById("app-sidebar");
    const toggle = document.querySelector("[data-sidebar-toggle]");
    const dismiss = document.querySelector("[data-sidebar-dismiss]");

    if (!sidebar || !toggle || !dismiss) {
        return;
    }

    const setSidebarOpen = (isOpen) => {
        body.classList.toggle("sidebar-open", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
        toggle.setAttribute(
            "aria-label",
            isOpen ? "Close navigation menu" : "Open navigation menu"
        );
        dismiss.tabIndex = isOpen ? 0 : -1;
    };

    toggle.addEventListener("click", () => {
        setSidebarOpen(!body.classList.contains("sidebar-open"));
    });

    dismiss.addEventListener("click", () => {
        setSidebarOpen(false);
        toggle.focus();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && body.classList.contains("sidebar-open")) {
            setSidebarOpen(false);
            toggle.focus();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth >= 992 && body.classList.contains("sidebar-open")) {
            setSidebarOpen(false);
        }
    });

    const deleteModal = document.getElementById("deleteProductModal");

    if (deleteModal) {
        deleteModal.addEventListener("show.bs.modal", (event) => {
            const trigger = event.relatedTarget;
            const deleteForm = deleteModal.querySelector("#delete-product-form");
            const productName = deleteModal.querySelector(
                "[data-delete-product-name]"
            );

            if (!trigger || !deleteForm || !productName) {
                return;
            }

            deleteForm.action = trigger.dataset.deleteUrl;
            productName.textContent = trigger.dataset.productName;
        });
    }
});
