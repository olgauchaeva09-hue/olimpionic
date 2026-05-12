function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

document.querySelectorAll('.notification-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', async function(e) {
        const olympiadId = this.dataset.olympiadId;
        const isActive = this.checked;
        
        try {
            const response = await fetch('/api/toggle/olympiad/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    olympiad_id: olympiadId,
                    set_active: isActive
                })
            });
            
            if (!response.ok) {
                this.checked = !isActive;
            }
        } catch(err) {
            this.checked = !isActive;
        }
    });
});