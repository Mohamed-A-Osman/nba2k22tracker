// Light/dark theme. Loaded in <head> so the saved theme applies before the page is drawn.
(function () {
    // Lets the stylesheet show controls that only work with JavaScript
    document.documentElement.classList.add('js');
    var saved = null;
    try {
        saved = localStorage.getItem('theme');
    } catch (e) {}
    var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme = saved || (prefersDark ? 'dark' : 'light');
})();

function toggleTheme() {
    var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try {
        localStorage.setItem('theme', next);
    } catch (e) {}
}
