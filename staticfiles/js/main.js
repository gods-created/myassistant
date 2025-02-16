const BASE_URL = window.location.origin;

function edit_menu_state() {
    $('.sidebar-button').toggleClass('d-none d-flex');
    $('.sidebar').toggleClass('d-none d-flex');
    return;
}

let alertTimeout;

function edit_alert_window_state(text) {
    const elem = $('.alert-window');
    const alert = elem.find('.alert');

    if (elem.hasClass('d-flex')) {
        clearTimeout(alertTimeout);
        alert.empty();
        elem.toggleClass('d-none d-flex');
        return;
    }

    alert.empty().append(text);
    elem.toggleClass('d-none d-flex');

    alertTimeout = setTimeout(() => {
        alert.empty();
        elem.toggleClass('d-none d-flex');
    }, 1000);
}

function copy_credent(e) {
    const elem = e.currentTarget;
    const parent = elem.parentNode;
    const input = $(parent).find('input');
    const value = input.val()
    navigator.clipboard.writeText(value);
    return edit_alert_window_state(`Copy ${value.slice(0, 30)} ...`)
}

$(document).ready(() => {
    $('.download-api-docs').off('click').on('click', () => window.open(`${BASE_URL}/api/docs/`, '_blank'));
    $('.open-menu').off('click').on('click', () => edit_menu_state());
    $('.close-menu').off('click').on('click', () => edit_menu_state());
    $('.copy-button').off('click').on('click', (e) => copy_credent(e));
    $('.current-year').text(new Date().getFullYear());
})