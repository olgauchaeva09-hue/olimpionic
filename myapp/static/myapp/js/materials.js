window.addEventListener('load', function() {
    var typeSelect = document.querySelector('#type-filter + .select-wrapper select');
    var olympiadSelect = document.querySelector('#olympiad-filter + .select-wrapper select');
    var cardsContainer = document.querySelector('.materials-list');
    
    if (!cardsContainer) return;
    
    function renderCard(card) {
        var isActive = (card.is_solved || card.is_read) ? 'active' : '';
        var isFavorite = card.is_favorite ? 'active' : '';
        var isPlanned = card.is_planned ? 'active' : '';
        var isTask = card.is_task ? 'active' : '';
        var xp = card.xp || 10;
        var title = escapeHtml(card.title);
        var cardType = escapeHtml(card.type);
        var source = card.source ? escapeHtml(card.source) : '';
        var link = card.link ? '<div class="material-link"><a href="' + escapeHtml(card.link) + '" target="_blank">' + escapeHtml(card.link) + '</a></div>' : '';
        
        return '<div class="material-card" data-card-id="' + card.id + '">' +
            '<div class="card-header">' +
                '<div class="xp-badge ' + isActive + '"><span>+' + xp + ' XP</span></div>' +
                '<div class="action-buttons">' +
                    '<button class="action-btn complete ' + isActive + '" data-action="complete" title="Отметить как выполненное"></button>' +
                    '<button class="action-btn planned ' + isPlanned + '" data-action="planned" title="Отметить как запланированное"></button>' +
                    '<button class="action-btn task ' + isTask + '" data-action="task" title="Переместить в задачи"></button>' +
                    '<button class="action-btn favorite ' + isFavorite + '" data-action="favorite" title="Отметить как избранное"></button>' +
                '</div>' +
            '</div>' +
            '<div class="material-title">' + title + '</div>' +
            '<div class="material-meta">' +
                '<span class="meta-tag">Тип: ' + cardType + '</span>' +
                (source ? '<span class="meta-tag">Олимпиада: ' + source + '</span>' : '') +
            '</div>' +
            link +
        '</div>';
    }
    
    function loadCards() {
        var type = typeSelect ? typeSelect.value : 'types_all';
        var olympiad = olympiadSelect ? olympiadSelect.value : 'olympiads_all';
        
        var url = '/api/cards/';
        var params = [];
        
        if (type !== 'types_all') params.push('type=' + encodeURIComponent(type));
        if (olympiad !== 'olympiads_all') params.push('source=' + encodeURIComponent(olympiad));
        if (params.length) url += '?' + params.join('&');
        
        if (window.history && window.history.replaceState) {
            var newUrl = window.location.pathname;
            if (params.length) newUrl += '?' + params.join('&');
            window.history.replaceState({}, '', newUrl);
        }
        
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var cards = data.results || data;
                if (cards.length > 0) {
                    var html = '';
                    cards.forEach(function(card) {
                        html += renderCard(card);
                    });
                    cardsContainer.innerHTML = html;
                } else {
                    cardsContainer.innerHTML = '<p>Материалы не найдены</p>';
                }
            })
            .catch(function(err) {
                console.error(err);
            });
    }
    
    if (typeSelect) typeSelect.addEventListener('change', loadCards);
    if (olympiadSelect) olympiadSelect.addEventListener('change', loadCards);
});