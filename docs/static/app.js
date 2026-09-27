/* ===== 成语吧 app.js ===== */
(function () {
  "use strict";

  /* ---------- 主题切换 ---------- */
  var themeBtn = document.getElementById("themeToggle");
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    if (themeBtn) themeBtn.textContent = t === "dark" ? "☀️" : "🌙";
  }
  var saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  applyTheme(saved || (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }

  /* ---------- 年份 ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- 搜索（依赖 static/search-index.js） ---------- */
  var ROOT = document.body.getAttribute("data-root") || "";
  var INDEX = window.SEARCH_INDEX || [];

  function match(q) {
    q = q.trim().toLowerCase();
    if (!q) return [];
    return INDEX.filter(function (x) {
      return x.n.indexOf(q) > -1 || x.p.toLowerCase().indexOf(q) > -1 || x.m.indexOf(q) > -1;
    }).slice(0, 10);
  }

  function card(x) {
    return '<a class="card idiom-card" href="' + ROOT + x.u + '">' +
      "<h3>" + x.n + '</h3><p class="py">' + x.p + '</p><p class="meaning">' + x.m + "…</p></a>";
  }

  var inputs = document.querySelectorAll("#globalSearch");
  inputs.forEach(function (input) {
    var box = input.closest(".search-box");
    var results = box ? box.querySelector(".search-results") : null;
    if (!results) return;

    function render(q) {
      var hits = match(q);
      if (!q.trim()) { results.classList.remove("show"); results.innerHTML = ""; return; }
      if (!hits.length) {
        results.innerHTML = '<div class="search-empty">未找到相关成语，试试「守株待兔」或「画蛇」</div>';
      } else {
        results.innerHTML = hits.map(function (x) {
          return '<a href="' + ROOT + x.u + '"><span class="sr-name">' + x.n + '</span>' +
            '<span class="sr-py">' + x.p + '</span><span class="sr-mean">' + x.m + "…</span></a>";
        }).join("");
      }
      results.classList.add("show");
    }

    input.addEventListener("input", function () { render(input.value); });
    input.addEventListener("focus", function () { if (input.value.trim()) render(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { results.classList.remove("show"); input.blur(); }
      if (e.key === "Enter") {
        var first = results.querySelector("a");
        if (first) window.location.href = first.getAttribute("href");
      }
    });
    document.addEventListener("click", function (e) {
      if (!box.contains(e.target)) results.classList.remove("show");
    });
  });

  /* ---------- 搜索页整页结果 ---------- */
  var pageResults = document.getElementById("searchPageResults");
  if (pageResults) {
    var q = (new URLSearchParams(window.location.search)).get("q") || "";
    var input = document.querySelector("#globalSearch");
    function renderPage(q) {
      if (!q.trim()) { pageResults.innerHTML = '<p class="muted">输入关键词开始搜索，共 ' + INDEX.length + ' 条数据。</p>'; return; }
      var hits = INDEX.filter(function (x) {
        var qq = q.trim().toLowerCase();
        return x.n.indexOf(qq) > -1 || x.p.toLowerCase().indexOf(qq) > -1 || x.m.indexOf(qq) > -1;
      });
      pageResults.innerHTML = hits.length
        ? hits.map(card).join("")
        : '<p class="muted">没有找到相关成语，换个关键词试试。</p>';
    }
    if (input) {
      input.value = q;
      input.addEventListener("input", function () { renderPage(input.value); });
    }
    renderPage(q);
  }
})();
