
(function () {
  var input = document.getElementById('site-search');
  var box = document.getElementById('search-results');
  var root = window.SITE_ROOT || '';
  var data = null;

  function ensureData(cb) {
    if (data) return cb();
    fetch(root + 'products.json').then(function (r) { return r.json(); }).then(function (json) {
      data = json;
      cb();
    });
  }

  function render(query) {
    var q = query.trim().toLowerCase();
    if (!q) { box.classList.remove('open'); box.innerHTML = ''; return; }
    var matches = data.filter(function (p) {
      return p.name.toLowerCase().indexOf(q) !== -1 || p.category_label.toLowerCase().indexOf(q) !== -1;
    }).slice(0, 8);

    if (matches.length === 0) {
      box.innerHTML = '<div class="search-result-empty">Sin resultados para "' + query + '"</div>';
    } else {
      box.innerHTML = matches.map(function (p) {
        return '<a class="search-result-item" href="' + root + 'articulos/' + p.slug + '.html">' +
          '<img src="' + p.image_url + '" alt="">' +
          '<span><div>' + p.name + '</div><div class="search-result-meta">' + p.category_label + '</div></span>' +
          '<span class="search-result-price">' + p.price.toFixed(2) + '€</span>' +
          '</a>';
      }).join('');
    }
    box.classList.add('open');
  }

  input.addEventListener('input', function () {
    ensureData(function () { render(input.value); });
  });
  input.addEventListener('focus', function () {
    if (input.value) ensureData(function () { render(input.value); });
  });
  document.addEventListener('click', function (e) {
    if (!box.contains(e.target) && e.target !== input) box.classList.remove('open');
  });
})();
