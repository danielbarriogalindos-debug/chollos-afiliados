
(function () {
  var bar = document.querySelector('.filter-bar');
  if (!bar) return;
  var grid = document.querySelector('.card-grid');
  var buttons = Array.prototype.slice.call(bar.querySelectorAll('[data-min]'));
  var sortSelect = bar.querySelector('#sort-select');
  var loadMoreBtn = document.getElementById('load-more');
  var countEl = document.getElementById('result-count');
  var pageSize = 24;
  var shown = pageSize;

  function apply() {
    var activeBtn = bar.querySelector('[data-min].active') || buttons[0];
    var min = parseInt(activeBtn.dataset.min, 10);
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
    var visible = cards.filter(function (c) { return parseInt(c.dataset.discount, 10) >= min; });

    if (sortSelect) {
      var by = sortSelect.value;
      visible.sort(function (a, b) {
        if (by === 'discount') return parseInt(b.dataset.discount, 10) - parseInt(a.dataset.discount, 10);
        if (by === 'price-asc') return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
        if (by === 'price-desc') return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
        return 0;
      });
    }

    cards.forEach(function (c) { c.style.display = 'none'; });
    visible.forEach(function (c, i) {
      grid.appendChild(c);
      c.style.display = i < shown ? '' : 'none';
    });
    if (loadMoreBtn) loadMoreBtn.style.display = visible.length > shown ? '' : 'none';
    if (countEl) countEl.textContent = visible.length;
  }

  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      buttons.forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      shown = pageSize;
      apply();
    });
  });
  if (sortSelect) sortSelect.addEventListener('change', function () { shown = pageSize; apply(); });
  if (loadMoreBtn) loadMoreBtn.addEventListener('click', function () { shown += pageSize; apply(); });

  apply();
})();
