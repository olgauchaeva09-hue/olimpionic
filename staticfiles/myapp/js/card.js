function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length == 2) return parts.pop().split(";").shift();
}

(function() {
    document.body.addEventListener('click', function(e) {
        var btn = e.target.closest('.action-btn');
        if (!btn) return;
        
        e.preventDefault();
        e.stopPropagation();
        
        var action = btn.dataset.action;
        var card = btn.closest('.material-card');
        var cardId = card ? card.getAttribute('data-card-id') : null;
        
        if (!action || !cardId) return;
        
        fetch('/api/toggle/' + action + '/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                card_id: cardId,
                set_active: !btn.classList.contains('active')
            })
        }).then(function(res) {
            if (res.ok) {
                btn.classList.toggle('active');
            }
        });
    });
})();