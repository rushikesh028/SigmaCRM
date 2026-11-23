document.addEventListener('DOMContentLoaded', function () {
    // Sidebar toggle for mobile
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => sidebar.classList.toggle('show'));
    }

    // Auto-dismiss alerts
    document.querySelectorAll('.alert-dismissible').forEach(el => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Confirm delete forms
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!confirm(this.dataset.confirm || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Kanban drag & drop
function initKanban() {
    const cards = document.querySelectorAll('.kanban-card[draggable="true"]');
    const columns = document.querySelectorAll('.kanban-column');

    cards.forEach(card => {
        card.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', card.dataset.dealId);
            card.classList.add('opacity-50');
        });
        card.addEventListener('dragend', () => card.classList.remove('opacity-50'));
    });

    columns.forEach(col => {
        col.addEventListener('dragover', e => {
            e.preventDefault();
            col.classList.add('bg-light');
        });
        col.addEventListener('dragleave', () => col.classList.remove('bg-light'));
        col.addEventListener('drop', e => {
            e.preventDefault();
            col.classList.remove('bg-light');
            const dealId = e.dataTransfer.getData('text/plain');
            const stage = col.dataset.stage;
            const card = document.querySelector(`.kanban-card[data-deal-id="${dealId}"]`);
            if (card && stage) {
                col.querySelector('.kanban-cards').appendChild(card);
                updateDealStage(dealId, stage);
            }
        });
    });
}

function updateDealStage(dealId, stage) {
    const formData = new FormData();
    formData.append('stage', stage);
    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    fetch(`/deals/${dealId}/stage/`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    }).then(r => r.json()).then(data => {
        if (data.ok) {
            // optional toast
        }
    }).catch(console.error);
}

document.addEventListener('DOMContentLoaded', initKanban);
