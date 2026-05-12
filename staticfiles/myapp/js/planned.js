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

function initDeleteButtons() {
    document.querySelectorAll('.remove-item-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const itemId = btn.dataset.id;
            const response = await fetch(`/api/planned/delete/${itemId}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            if (response.ok) {
                btn.closest('.sidebar-item').remove();
            }
        });
    });
    
    document.querySelectorAll('.remove-schedule-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const itemId = btn.dataset.id;
            const response = await fetch(`/api/planned/delete/${itemId}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            if (response.ok) {
                btn.closest('.grid-cell').innerHTML = '';
            }
        });
    });
}

// Перемещение из сайдбара в сетку
function initDragAndDrop() {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    const gridCells = document.querySelectorAll('.grid-cell');
    
    sidebarItems.forEach(item => {
        item.setAttribute('draggable', 'true');
        
        item.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', JSON.stringify({
                id: item.dataset.sourceId,
                type: item.dataset.type,
                title: item.dataset.title,
                plannedId: item.dataset.plannedId || null
            }));
        });
    });
    
    gridCells.forEach(cell => {
        cell.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        cell.addEventListener('drop', async (e) => {
            e.preventDefault();
            
            if (cell.querySelector('.scheduled-item')) return;
            
            const data = JSON.parse(e.dataTransfer.getData('text/plain'));
            const date = cell.dataset.date;
            const hour = cell.dataset.hour;
            const startDateTime = `${date}T${String(hour).padStart(2, '0')}:00:00`;
            const endDateTime = `${date}T${String(parseInt(hour) + 1).padStart(2, '0')}:00:00`;
            
            let itemId = data.plannedId;
            
            if (!itemId) {
                const body = {};
                body[data.type + '_id'] = data.id;
                
                const addResponse = await fetch('/api/planned/add_to_sidebar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(body)
                });
                const addData = await addResponse.json();
                if (!addData.success) return;
                itemId = addData.id;
            }
            
            const moveResponse = await fetch('/api/planned/move_to_grid/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    item_id: itemId,
                    start_datetime: startDateTime,
                    end_datetime: endDateTime
                })
            });
            
            if (moveResponse.ok) {
                const sourceItem = document.querySelector(`.sidebar-item[data-planned-id="${itemId}"]`);
                if (sourceItem) sourceItem.remove();
                
                cell.innerHTML = `
                    <div class="scheduled-item" data-planned-id="${itemId}" draggable="true">
                        <div class="scheduled-content">
                            <span class="scheduled-title">${data.title}</span>
                        </div>
                        <button class="remove-schedule-btn" data-id="${itemId}" title="Удалить">×</button>
                    </div>
                `;
                
                cell.querySelector('.remove-schedule-btn').addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await fetch(`/api/planned/delete/${itemId}/`, {
                        method: 'DELETE',
                        headers: { 'X-CSRFToken': getCookie('csrftoken') }
                    });
                    cell.innerHTML = '';
                });

                // Делаем запланированный элемент перемещаемым между ячейками
                initScheduledItemDrag(cell.querySelector('.scheduled-item'));
            }
        });
    });
}

// Перемещение запланированных элементов между ячейками
function initScheduledItemDrag(item) {
    item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', JSON.stringify({
            plannedId: item.dataset.plannedId,
            type: 'scheduled',
            title: item.querySelector('.scheduled-title').textContent,
            sourceCell: true,
            sourceCellDate: item.closest('.grid-cell').dataset.date,
            sourceCellHour: item.closest('.grid-cell').dataset.hour
        }));
        item.style.opacity = '0.4';
    });
    
    item.addEventListener('dragend', (e) => {
        item.style.opacity = '1';
        // Не удаляем здесь — удаление происходит в drop
    });
}

// Принимаем запланированные элементы в других ячейках
function initGridDropTargets() {
    document.querySelectorAll('.grid-cell').forEach(cell => {
        cell.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        
        cell.addEventListener('drop', async (e) => {
            e.preventDefault();
            
            const data = JSON.parse(e.dataTransfer.getData('text/plain'));
            
            if (!data.sourceCell) return;
            
            // Не даём бросить в ту же ячейку
            if (data.sourceCellDate === cell.dataset.date && data.sourceCellHour === cell.dataset.hour) {
                return;
            }
            
            if (cell.querySelector('.scheduled-item') && cell.querySelector('.scheduled-item').dataset.plannedId !== data.plannedId) {
                return;
            }
            
            const date = cell.dataset.date;
            const hour = cell.dataset.hour;
            const startDateTime = `${date}T${String(hour).padStart(2, '0')}:00:00`;
            const endDateTime = `${date}T${String(parseInt(hour) + 1).padStart(2, '0')}:00:00`;
            
            const response = await fetch(`/api/planned/update/${data.plannedId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    start_datetime: startDateTime,
                    end_datetime: endDateTime
                })
            });
            
            if (response.ok) {
                // Удаляем ВСЕ элементы с этим plannedId из ВСЕХ ячеек
                document.querySelectorAll(`.scheduled-item[data-planned-id="${data.plannedId}"]`).forEach(el => {
                    el.parentElement.innerHTML = '';
                });
                
                // Добавляем в новую ячейку
                cell.innerHTML = `
                    <div class="scheduled-item" data-planned-id="${data.plannedId}" draggable="true">
                        <div class="scheduled-content">
                            <span class="scheduled-title">${data.title}</span>
                        </div>
                        <button class="remove-schedule-btn" data-id="${data.plannedId}" title="Удалить">×</button>
                    </div>
                `;
                
                cell.querySelector('.remove-schedule-btn').addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await fetch(`/api/planned/delete/${data.plannedId}/`, {
                        method: 'DELETE',
                        headers: { 'X-CSRFToken': getCookie('csrftoken') }
                    });
                    cell.innerHTML = '';
                });
                
                initScheduledItemDrag(cell.querySelector('.scheduled-item'));
            } else {
                location.reload();
            }
        });
    });
}

function initSaveButton() {
    const saveBtn = document.getElementById('save-schedule-btn');
    if (!saveBtn) return;
    
    saveBtn.addEventListener('click', async () => {
        alert('Расписание сохранено!');
    });
}

function initNextButton() {
    const nextBtn = document.getElementById('next-step-btn');
    if (!nextBtn) return;
    nextBtn.addEventListener('click', () => window.location.href = '/materials/');
}

function initWeekNavigation() {
    const prevBtn = document.getElementById('prev-week-btn');
    const nextBtn = document.getElementById('next-week-btn');
    if (!prevBtn || !nextBtn) return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const currentOffset = parseInt(urlParams.get('week')) || 0;
    
    prevBtn.addEventListener('click', () => {
        urlParams.set('week', currentOffset - 1);
        window.location.search = urlParams.toString();
    });
    nextBtn.addEventListener('click', () => {
        urlParams.set('week', currentOffset + 1);
        window.location.search = urlParams.toString();
    });
}

// Вешаем drag на существующие scheduled-item
function initExistingScheduledItems() {
    document.querySelectorAll('.scheduled-item').forEach(item => {
        item.setAttribute('draggable', 'true');
        initScheduledItemDrag(item);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initDragAndDrop();
    initGridDropTargets();
    initExistingScheduledItems();
    initDeleteButtons();
    initSaveButton();
    initNextButton();
    initWeekNavigation();
});