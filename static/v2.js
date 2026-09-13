// v2 page behavior: filters that apply themselves, sortable tables and the extra-columns toggle.
// Every page works without it: filters keep an Apply button and tables arrive sorted.

// Filters: go straight to the filtered page, leaving empty fields out of the URL
function applyFilters(form) {
    var params = new URLSearchParams();
    new FormData(form).forEach(function (value, key) {
        if (value) {
            params.append(key, value);
        }
    });
    var query = params.toString();
    window.location.assign(form.action.split('?')[0] + (query ? '?' + query : ''));
}

document.querySelectorAll('form[data-autosubmit]').forEach(function (form) {
    form.addEventListener('change', function (event) {
        // Teammate and opponent filters belong to the chosen player
        if (event.target.name === 'Name') {
            form.querySelectorAll('[data-player-filter]').forEach(function (field) {
                if (field.type === 'radio') {
                    field.checked = field.value === '';
                } else {
                    field.value = '';
                }
            });
        }
        applyFilters(form);
    });
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        applyFilters(form);
    });
});

// Sortable tables: numbers sort high to low first, names A to Z first
document.querySelectorAll('table[data-sortable]').forEach(function (table) {
    var headers = table.querySelectorAll('thead th');
    headers.forEach(function (th, index) {
        var button = th.querySelector('button.sort');
        if (!button) {
            return;
        }
        button.addEventListener('click', function () {
            var isText = button.dataset.type === 'text';
            var current = th.getAttribute('aria-sort');
            var descending = isText ? current === 'ascending' : current !== 'descending';
            headers.forEach(function (other) {
                other.removeAttribute('aria-sort');
            });
            th.setAttribute('aria-sort', descending ? 'descending' : 'ascending');

            var body = table.tBodies[0];
            var rows = Array.prototype.slice.call(body.rows);
            rows.sort(function (a, b) {
                var x = a.cells[index].dataset.value;
                var y = b.cells[index].dataset.value;
                var result = isText
                    ? x.localeCompare(y, undefined, { sensitivity: 'base' })
                    : parseFloat(x) - parseFloat(y);
                return descending ? -result : result;
            });
            rows.forEach(function (row) {
                body.appendChild(row);
            });
        });
    });
});

// "More stats" shows the less-used columns
document.querySelectorAll('[data-toggle-extra]').forEach(function (button) {
    button.addEventListener('click', function () {
        var open = button.closest('.table-block').classList.toggle('show-extra');
        button.setAttribute('aria-expanded', open ? 'true' : 'false');
        button.textContent = open ? 'Fewer stats' : 'More stats';
    });
});

// Lineups played once stay tucked away until asked for
document.querySelectorAll('[data-show-once]').forEach(function (button) {
    button.addEventListener('click', function () {
        button.closest('.table-block').classList.add('show-once');
        button.remove();
    });
});
