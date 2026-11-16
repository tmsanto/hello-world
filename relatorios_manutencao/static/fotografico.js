(function () {
  function renumerar() {
    document.querySelectorAll('.grade-fotos').forEach(function (lista) {
      lista.querySelectorAll('.item-foto').forEach(function (el, i) {
        el.querySelector('.numero').textContent = (i + 1) + '.';
      });
    });
  }

  function ligar(item) {
    var arquivo = item.querySelector('.js-arquivo');
    var preview = item.querySelector('.js-preview');
    var placeholder = item.querySelector('.placeholder');
    var flag = item.querySelector('.js-remover-flag');

    arquivo.addEventListener('change', function () {
      if (!arquivo.files.length) return;
      preview.src = URL.createObjectURL(arquivo.files[0]);
      preview.hidden = false;
      placeholder.hidden = true;
      flag.value = '0';
    });
    item.querySelector('.js-tirar-foto').addEventListener('click', function () {
      arquivo.value = '';
      preview.removeAttribute('src');
      preview.hidden = true;
      placeholder.hidden = false;
      flag.value = '1';
    });
    item.querySelector('.js-excluir').addEventListener('click', function () {
      if (confirm('Excluir este item?')) { item.remove(); renumerar(); }
    });
    item.querySelector('.js-subir').addEventListener('click', function () {
      var ant = item.previousElementSibling;
      if (ant) { item.parentNode.insertBefore(item, ant); renumerar(); }
    });
    item.querySelector('.js-descer').addEventListener('click', function () {
      var prox = item.nextElementSibling;
      if (prox) { item.parentNode.insertBefore(prox, item); renumerar(); }
    });
  }

  document.querySelectorAll('.item-foto').forEach(ligar);

  document.querySelectorAll('.js-adicionar').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var secao = btn.dataset.secao;
      var chave = 'n' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      var html = document.getElementById('modelo-' + secao).innerHTML.split('__CHAVE__').join(chave);
      var wrap = document.createElement('div');
      wrap.innerHTML = html.trim();
      var item = wrap.firstElementChild;
      item.querySelector('input[name="item_legenda"]').value = btn.dataset.legenda || '';
      document.getElementById('lista-' + secao).appendChild(item);
      ligar(item);
      renumerar();
      item.querySelector('input[name="item_legenda"]').focus();
    });
  });

  renumerar();
})();
