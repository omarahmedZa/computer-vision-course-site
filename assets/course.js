/* Computer Vision course — progress, theme, readbar, grading. No dependencies. */
(function () {
  "use strict";

  var KEY = "cv-course.progress.v1";
  var store = { lessons: {}, theme: null };

  try {
    var raw = localStorage.getItem(KEY);
    if (raw) {
      var parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") store = parsed;
    }
  } catch (e) {}
  if (!store.lessons) store.lessons = {};

  function persist() {
    try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {}
  }
  function lessonState(id) {
    if (!store.lessons[id]) store.lessons[id] = { sections: {}, quiz: {}, ts: 0 };
    if (!store.lessons[id].sections) store.lessons[id].sections = {};
    if (!store.lessons[id].quiz) store.lessons[id].quiz = {};
    return store.lessons[id];
  }

  var root = document.documentElement;
  if (store.theme) root.setAttribute("data-theme", store.theme);
  function themeLabel() {
    if (!store.theme) return "◐ auto";
    return store.theme === "dark" ? "● dark" : "○ light";
  }
  function applyTheme(mode) {
    if (mode === "auto") { root.removeAttribute("data-theme"); store.theme = null; }
    else { root.setAttribute("data-theme", mode); store.theme = mode; }
    persist();
    var btn = document.querySelector("[data-theme-toggle]");
    if (btn) btn.textContent = themeLabel();
  }
  function bindThemeButton() {
    var btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    btn.textContent = themeLabel();
    btn.addEventListener("click", function () {
      applyTheme(!store.theme ? "dark" : store.theme === "dark" ? "light" : "auto");
    });
  }

  function readbar() {
    var bar = document.createElement("div");
    bar.className = "readbar";
    document.body.appendChild(bar);
    function update() {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var p = max > 0 ? (h.scrollTop || document.body.scrollTop) / max : 0;
      bar.style.width = Math.max(0, Math.min(1, p)) * 100 + "%";
    }
    addEventListener("scroll", update, { passive: true });
    addEventListener("resize", update);
    update();
  }

  function gradeOf(points, total) {
    if (!total) return { pct: 0, letter: "–" };
    var pct = Math.round((points / total) * 100);
    var letter = pct >= 90 ? "A" : pct >= 80 ? "B" : pct >= 70 ? "C" : pct >= 60 ? "D" : "F";
    return { pct: pct, letter: letter };
  }

  function buttons(group, current, onPick) {
    [["2", "✓ got it"], ["1", "~ partly"], ["0", "✗ missed"]].forEach(function (pair) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "gbtn";
      b.dataset.v = pair[0];
      b.textContent = pair[1];
      b.setAttribute("aria-pressed", String(String(current) === pair[0]));
      b.addEventListener("click", function () {
        var pressed = b.getAttribute("aria-pressed") === "true";
        [].forEach.call(group.querySelectorAll(".gbtn"), function (x) { x.setAttribute("aria-pressed", "false"); });
        if (!pressed) b.setAttribute("aria-pressed", "true");
        onPick(pressed ? null : Number(pair[0]));
      });
      group.appendChild(b);
    });
  }

  function initLesson() {
    var id = document.body.getAttribute("data-lesson");
    if (!id) return;
    var st = lessonState(id);
    bindThemeButton();
    readbar();

    var chip = document.createElement("div");
    chip.className = "scorechip";
    chip.innerHTML = '<span>lesson</span><strong data-score>0%</strong><span class="grade" data-grade>–</span><span data-count>0/0</span>';
    document.body.appendChild(chip);

    var totalItems = 0, earned = 0;
    function refresh() {
      var g = gradeOf(earned, totalItems * 2);
      chip.querySelector("[data-score]").textContent = earned ? g.pct + "%" : "–";
      var gradeEl = chip.querySelector("[data-grade]");
      gradeEl.textContent = earned ? g.letter : "–";
      gradeEl.setAttribute("data-g", earned ? g.letter : "");
      chip.querySelector("[data-count]").textContent = earned + "/" + (totalItems * 2);
      st.ts = Date.now();
      persist();
    }

    var h2s = [].slice.call(document.querySelectorAll("main h2"));
    h2s.forEach(function (h2, i) {
      var text = (h2.textContent || "").toLowerCase();
      if (text.indexOf("retrieval") !== -1 || text.indexOf("next") !== -1 || text.indexOf("lab") !== -1) return;
      var node = h2.nextElementSibling, last = h2;
      while (node && node.tagName !== "H2" && !(node.classList && node.classList.contains("next"))) {
        last = node; node = node.nextElementSibling;
      }
      var row = document.createElement("div");
      row.className = "blockcheck";
      var lab = document.createElement("span");
      lab.className = "grow";
      lab.textContent = "can you explain this without looking?";
      row.appendChild(lab);
      var group = document.createElement("span");
      row.appendChild(group);
      totalItems++;
      var cur = st.sections[i];
      if (cur != null) earned += cur;
      buttons(group, cur, function (v) {
        var prev = st.sections[i];
        if (v == null) { if (prev != null) earned -= prev; delete st.sections[i]; }
        else { if (prev != null) earned -= prev; st.sections[i] = v; earned += v; }
        refresh();
      });
      if (last && last.parentNode) last.parentNode.insertBefore(row, last.nextSibling);
    });

    var quiz = [].slice.call(document.querySelectorAll("ol.quiz > li"));
    quiz.forEach(function (li, i) {
      var row = document.createElement("div");
      row.className = "grade-row";
      var qlab = document.createElement("span");
      qlab.className = "q"; qlab.textContent = "your call";
      row.appendChild(qlab);
      li.appendChild(row);
      totalItems++;
      var cur = st.quiz[i];
      if (cur != null) earned += cur;
      buttons(row, cur, function (v) {
        var prev = st.quiz[i];
        if (v == null) { if (prev != null) earned -= prev; delete st.quiz[i]; }
        else {
          if (prev != null) earned -= prev; st.quiz[i] = v; earned += v;
          var d = li.querySelector("details"); if (d && !d.open) d.open = true;
        }
        refresh();
      });
    });

    refresh();
    store.last = id; persist();
  }

  function initLab() {
    var id = document.body.getAttribute("data-lesson");
    if (!id) return;
    var st = lessonState(id);
    bindThemeButton();
    readbar();

    var quiz = [].slice.call(document.querySelectorAll("ol.quiz > li"));
    var chip = document.createElement("div");
    chip.className = "scorechip";
    chip.innerHTML = '<span>lab</span><strong data-score>0</strong><span class="grade" data-grade style="display:none"></span><span data-count>0/0 pts</span>';
    document.body.appendChild(chip);
    var total = quiz.length * 2, earned = 0;
    function refresh() {
      chip.querySelector("[data-score]").textContent = earned + " pts";
      chip.querySelector("[data-count]").textContent = earned + "/" + total + " pts";
      st.ts = Date.now(); persist();
    }
    quiz.forEach(function (li, i) {
      var row = document.createElement("div");
      row.className = "grade-row";
      var qlab = document.createElement("span");
      qlab.className = "q"; qlab.textContent = "your call";
      row.appendChild(qlab);
      li.appendChild(row);
      var cur = st.quiz[i];
      if (cur != null) earned += cur;
      buttons(row, cur, function (v) {
        var prev = st.quiz[i];
        if (v == null) { if (prev != null) earned -= prev; delete st.quiz[i]; }
        else {
          if (prev != null) earned -= prev; st.quiz[i] = v; earned += v;
          var d = li.querySelector("details"); if (d && !d.open) d.open = true;
        }
        refresh();
      });
    });
    refresh();
  }

  function initIndex() {
    bindThemeButton();
    readbar();
    var rows = [].slice.call(document.querySelectorAll("li.topic[data-lesson]"));
    var total = 0, done = 0, points = 0, possible = 0;
    var unitAgg = {};

    rows.forEach(function (row) {
      var id = row.getAttribute("data-lesson");
      var unit = row.getAttribute("data-unit") || "0";
      var st = store.lessons[id] || { sections: {}, quiz: {} };
      var secVals = Object.keys(st.sections || {}).map(function (k) { return st.sections[k]; });
      var quizVals = Object.keys(st.quiz || {}).map(function (k) { return st.quiz[k]; });
      var items = secVals.length + quizVals.length;
      var pts = secVals.concat(quizVals).reduce(function (a, b) { return a + b; }, 0);
      var expected = 16; /* ~8 items * 2 */
      total++;
      if (items >= 6) { done++; row.querySelector(".dot").className = "dot done"; }
      else if (items > 0) { row.querySelector(".dot").className = "dot part"; }
      points += pts; possible += expected;
      if (!unitAgg[unit]) unitAgg[unit] = { p: 0, e: 0 };
      unitAgg[unit].p += pts; unitAgg[unit].e += expected;
      var meta = row.querySelector(".topic-meta");
      if (meta && items > 0) {
        var g = gradeOf(pts, expected);
        var mins = meta.getAttribute("data-mins") || meta.textContent;
        meta.innerHTML = '<span class="badge ready">' + g.letter + " · " + g.pct + "%</span><br>" + mins;
      }
    });

    var labRows = [].slice.call(document.querySelectorAll("li.topic[data-lab]"));
    var labsDone = 0, labPts = 0, labMax = labRows.length * 4;
    labRows.forEach(function (row) {
      var id = row.getAttribute("data-lab");
      var st = store.lessons[id];
      var vals = st ? Object.keys(st.quiz || {}).map(function (k) { return st.quiz[k]; }) : [];
      var pts = vals.reduce(function (a, b) { return a + b; }, 0);
      var meta = row.querySelector(".topic-meta");
      if (vals.length) {
        meta.innerHTML = '<span class="badge ready">' + pts + " / 4 pts</span>";
        row.querySelector(".dot").className = "dot " + (vals.length >= 2 ? "done" : "part");
        if (vals.length >= 2) labsDone++;
      }
      labPts += pts;
    });
    var labCnt = document.querySelector("[data-labs-count]");
    if (labCnt) labCnt.textContent = labsDone + " / " + labRows.length;
    var labBar = document.querySelector("[data-labs-bar]");
    if (labBar && labMax) labBar.style.width = Math.round((labPts / labMax) * 100) + "%";

    var pct = possible ? Math.round((points / possible) * 100) : 0;
    var ring = document.querySelector(".ring");
    if (ring) {
      ring.style.setProperty("--p", pct);
      var pEl = ring.querySelector(".pct"); if (pEl) pEl.textContent = pct + "%";
      var cEl = ring.querySelector(".cap"); if (cEl) cEl.textContent = done + " of " + total + " done";
    }
    Object.keys(unitAgg).forEach(function (u) {
      var bar = document.querySelector('.unit[data-unit="' + u + '"] .bar i');
      if (bar) bar.style.width = Math.round((unitAgg[u].p / unitAgg[u].e) * 100) + "%";
    });

    var cont = document.querySelector("[data-continue]");
    if (cont && rows.length) {
      var next = rows.filter(function (r) { return (r.querySelector(".dot").className || "").indexOf("done") === -1; })[0];
      var target = next || rows[rows.length - 1];
      var link = target.querySelector("a.topic-link");
      if (link) {
        cont.href = link.getAttribute("href");
        cont.textContent = (next ? "Continue → " : "Review → ") + link.textContent;
      }
    }

    var exp = document.querySelector("[data-export]");
    if (exp) exp.addEventListener("click", function () { exportRecord(rows); });
    var reset = document.querySelector("[data-reset]");
    if (reset) reset.addEventListener("click", function () {
      if (confirm("Erase all scores on this device? This cannot be undone.")) {
        store = { lessons: {}, theme: store.theme }; persist(); location.reload();
      }
    });
  }

  function exportRecord(rows) {
    var lines = ["# Learning record — Computer Vision course", "", "Generated " + new Date().toISOString().slice(0, 10) + " from self-assessed checks.", "",
      "| # | Topic | Points | Score | Grade | Status |", "|---|-------|--------|-------|-------|--------|"];
    rows.forEach(function (row) {
      var id = row.getAttribute("data-lesson");
      var st = store.lessons[id];
      var titleEl = row.querySelector(".topic-link, .topic-title");
      var title = titleEl ? titleEl.textContent.trim() : id;
      if (!st) { lines.push("| " + id + " | " + title + " | 0/16 | 0% | – | not started |"); return; }
      var vals = Object.keys(st.sections || {}).map(function (k) { return st.sections[k]; })
        .concat(Object.keys(st.quiz || {}).map(function (k) { return st.quiz[k]; }));
      var pts = vals.reduce(function (a, b) { return a + b; }, 0);
      var g = gradeOf(pts, 16);
      var status = vals.length >= 6 ? "complete" : vals.length > 0 ? "in progress" : "not started";
      lines.push("| " + id + " | " + title + " | " + pts + "/16 | " + g.pct + "% | " + g.letter + " | " + status + " |");
    });
    lines.push("", "Scores are self-assessed confidence checks, not verified ability.");
    var blob = new Blob([lines.join("\n")], { type: "text/markdown" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "cv-learning-record-" + new Date().toISOString().slice(0, 10) + ".md";
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  function esc(t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function highlightCode() {
    var KW = /^(import|from|for|in|while|if|elif|else|def|return|class|with|as|and|or|not|None|True|False|lambda|print|range|len|yield|pass|break|continue|try|except|raise)$/;
    [].forEach.call(document.querySelectorAll("pre code"), function (block) {
      if (block.getAttribute("data-hl")) return;
      var src = block.textContent, out = "", last = 0;
      var re = /(#[^\n]*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\b)|([A-Za-z_]\w*)|(\S)/g, m;
      while ((m = re.exec(src))) {
        if (m.index > last) out += esc(src.slice(last, m.index));
        if (m[1]) out += '<span class="tok-c">' + esc(m[1]) + '</span>';
        else if (m[2]) out += '<span class="tok-s">' + esc(m[2]) + '</span>';
        else if (m[3]) out += '<span class="tok-n">' + esc(m[3]) + '</span>';
        else if (m[4]) {
          var w = m[4], after = src.slice(re.lastIndex, re.lastIndex + 1);
          if (KW.test(w)) out += '<span class="tok-k">' + esc(w) + '</span>';
          else if (after === '(') out += '<span class="tok-f">' + esc(w) + '</span>';
          else out += esc(w);
        } else out += /[=+\-*/%<>!]/.test(m[5]) ? '<span class="tok-o">' + esc(m[5]) + '</span>' : esc(m[5]);
        last = re.lastIndex;
      }
      out += esc(src.slice(last));
      block.innerHTML = out; block.setAttribute("data-hl", "1");
    });
  }

  function initFigureZoom() {
    [].forEach.call(document.querySelectorAll(".fig svg"), function (svg) {
      svg.addEventListener("click", function () {
        var fig = svg.closest(".fig");
        var on = fig.classList.toggle("zoomed");
        document.body.classList.toggle("zoom-lock", on);
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var z = document.querySelector(".fig.zoomed");
      if (z) { z.classList.remove("zoomed"); document.body.classList.remove("zoom-lock"); }
    });
  }

  highlightCode();
  initFigureZoom();
  var page = document.body.getAttribute("data-page");
  if (page === "index") initIndex();
  else if (page === "lab") initLab();
  else initLesson();
})();
