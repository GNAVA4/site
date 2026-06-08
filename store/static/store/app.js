// ── Степпер количества (−/+) + живой пересчёт суммы в липкой панели ───────────
function updateLineTotals() {
  var input = document.querySelector('#buyForm .qty-input');
  var qty = input ? Math.max(1, parseInt(input.value || '1', 10)) : 1;
  document.querySelectorAll('[data-line-total]').forEach(function (el) {
    var unit = parseInt(el.dataset.unit || '0', 10);
    el.textContent = (unit * qty).toLocaleString('ru-RU') + ' ₽';
  });
}

document.addEventListener('click', function (e) {
  var btn = e.target.closest('.stepper [data-dir]');
  if (!btn) return;
  var box = btn.closest('.stepper');
  var input = box.querySelector('.qty-input');
  if (!input) return;
  var min = parseInt(input.min || '1', 10);
  var max = parseInt(input.max || '999999', 10);
  var val = parseInt(input.value || '1', 10) + parseInt(btn.dataset.dir, 10);
  if (isNaN(val)) val = min;
  input.value = Math.max(min, Math.min(max, val));
  updateLineTotals();
});

document.addEventListener('input', function (e) {
  if (e.target.classList && e.target.classList.contains('qty-input')) updateLineTotals();
});

document.addEventListener('DOMContentLoaded', updateLineTotals);

// ── Toast-уведомления ─────────────────────────────────────────────────────────
function showToast(text, kind) {
  var host = document.getElementById('toastHost');
  if (!host) return;
  var icon = kind === 'warn' ? 'fa-triangle-exclamation' : 'fa-circle-check';
  var t = document.createElement('div');
  t.className = 'toastx';
  t.innerHTML = '<i class="fas ' + icon + ' toastx__i"></i>' +
    '<span class="toastx__txt"></span>' +
    '<button class="toastx__x" aria-label="Закрыть">&times;</button>';
  t.querySelector('.toastx__txt').textContent = text;
  host.appendChild(t);
  requestAnimationFrame(function () { t.classList.add('show'); });

  var timer = setTimeout(close, 3500);
  function close() {
    clearTimeout(timer);
    t.classList.remove('show');
    setTimeout(function () { t.remove(); }, 250);
  }
  t.querySelector('.toastx__x').addEventListener('click', close);
}

function setCartCount(n) {
  document.querySelectorAll('.js-cart-count').forEach(function (el) {
    el.textContent = n;
    el.style.display = n > 0 ? '' : 'none';
  });
}

function setCartTotal(total, count) {
  document.querySelectorAll('.js-cart-total').forEach(function (el) {
    el.textContent = total;
  });
  document.querySelectorAll('.js-cart-widget').forEach(function (el) {
    el.classList.toggle('is-shown', count > 0);  // выезжает справа (CSS-анимация)
  });
}

// ── Автоподстановка имени/телефона на оформлении (только в браузере, не на сервере) ──
(function () {
  var name = document.querySelector('input[name="customer_name"]');
  var phone = document.querySelector('input[name="customer_phone"]');
  if (!name || !phone) return; // не страница оформления
  try {
    if (!name.value) name.value = localStorage.getItem('buyer_name') || '';
    if (!phone.value) phone.value = localStorage.getItem('buyer_phone') || '';
  } catch (e) {}
  var form = name.closest('form');
  if (form) form.addEventListener('submit', function () {
    try {
      localStorage.setItem('buyer_name', name.value || '');
      localStorage.setItem('buyer_phone', phone.value || '');
    } catch (e) {}
  });
})();

// ── AJAX-добавление в корзину (без перезагрузки и прыжка наверх) ───────────────
document.addEventListener('submit', function (e) {
  var form = e.target.closest('form.js-add');
  if (!form) return;
  e.preventDefault();

  fetch(form.action, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: new FormData(form),
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (typeof data.cart_count === 'number') setCartCount(data.cart_count);
      if (typeof data.cart_total === 'number') setCartTotal(data.cart_total, data.cart_count);
      showToast(data.message || 'Добавлено в корзину', data.ok === false ? 'warn' : 'ok');
    })
    .catch(function () { form.submit(); }); // если что-то пошло не так — обычная отправка
});
