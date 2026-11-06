const THEME_STORAGE_KEY = "incidentiq-theme";

export function initTheme() {
  let savedTheme = "dark";
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "dark" || stored === "light") savedTheme = stored;
  } catch {
    // Theme remains usable for the current page if browser storage is disabled.
  }
  applyTheme(savedTheme);
  const toggle = document.querySelector("#theme-toggle");
  toggle?.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    } catch {
      // The selected theme still applies until the page is closed.
    }
  });
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute(
    "content",
    theme === "light" ? "#E9E5DF" : "#171310",
  );
  const toggle = document.querySelector("#theme-toggle");
  const label = document.querySelector("#theme-label");
  const icon = document.querySelector(".theme-icon");
  if (toggle) {
    toggle.setAttribute("aria-pressed", String(theme === "light"));
    toggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} theme`);
  }
  if (label) label.textContent = theme === "dark" ? "Light appearance" : "Dark appearance";
  if (icon) icon.textContent = theme === "dark" ? "☼" : "☾";
}
