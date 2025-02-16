const BASE_URL = window.location.origin;

function edit_menu_state() {
    $('.sidebar-button').toggleClass('d-none d-flex');
    $('.sidebar').toggleClass('d-none d-flex');
    return;
}

let alertTimeout;

function edit_alert_window_state(text, status=null, timeout=1000) {
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

    if (status === 'error') {
        alert.removeClass(['alert-primary', 'alert-success']).addClass('alert-danger');
    } else if (status === 'success') {
        alert.removeClass(['alert-primary', 'alert-danger']).addClass('alert-success');
    } else {
        if (!alert.hasClass('alert-primary')) {
            alert.removeClass(['alert-danger', 'alert-success']).addClass('alert-primary')
        }
    }

    alertTimeout = setTimeout(() => {
        alert.empty();
        elem.toggleClass('d-none d-flex');
    }, timeout);
}

function copy_credent(e) {
    const elem = e.currentTarget;
    const parent = elem.parentNode;
    const input = $(parent).find('input');
    const value = input.val()
    navigator.clipboard.writeText(value);
    return edit_alert_window_state(`Copy ${value.slice(0, 30)} ...`)
}

function edit_application_form_state() {
    const modal = $('.signup-modal');
    modal.toggleClass('d-none d-block');

    modal.off('click', '.send-application-form').on('click', '.send-application-form', async () => {
        const form = modal.find('form');

        const fullname = form.find('#fullname').val();
        const email = form.find('#email').val()

        if (fullname.length === 0 || email.length === 0) {
            return edit_alert_window_state('Email or fullname can\'t to be empty', 'error', 5000);
        }

        const data = {
            fullname: fullname,
            email: email
        }

        try {
            const request = await fetch(`${BASE_URL}/api/signup/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })

            const { status, message } = await request.json();
            edit_alert_window_state(message, status, 5000);
        } catch (error) {
            edit_alert_window_state(error.message, 'error', 5000);
        }
    })

    modal.off('click', '.btn-close').on('click', '.btn-close', () => {
        modal.toggleClass('d-none d-block');
        return;
    })
}

$(document).ready(() => {
    $('.download-api-docs').off('click').on('click', () => window.open(`${BASE_URL}/api/docs/`, '_blank'));
    $('.open-menu').off('click').on('click', () => edit_menu_state());
    $('.close-menu').off('click').on('click', () => edit_menu_state());
    $('.copy-button').off('click').on('click', (e) => copy_credent(e));
    $('.open-application-form').off('click').on('click', (e) => edit_application_form_state());
    $('.current-year').text(new Date().getFullYear());
})