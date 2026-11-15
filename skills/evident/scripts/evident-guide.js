// Overlay Claude injects into the Evident app to point at things.
// Usage from Claude:
//   evidentGuide.show({ guide: "settings-approvals-download", match: "Approve before download", text: "..." })
// `guide` is a data-guide id; `match` is visible text, used when the id is not on the page.
// Returns { ok: true, via } or { ok: false, reason }. "not ready" means call again shortly.
(() => {
  if (window.evidentGuide) return;

  const style = document.createElement("style");
  style.textContent = `
    #eg-ring { position: fixed; z-index: 2147483646; border-radius: 10px; pointer-events: none;
      box-shadow: 0 0 0 4px #d9be7e, 0 0 0 9999px rgba(0,0,0,.55); transition: all .25s ease; }
    #eg-bubble { position: fixed; z-index: 2147483647; max-width: 320px; background: #fffaf0; color: #1a1a1a;
      font: 14px/1.45 system-ui, sans-serif; padding: 12px 14px; border-radius: 10px;
      box-shadow: 0 8px 30px rgba(0,0,0,.35); }
    #eg-bubble b { display: block; margin-bottom: 4px; }
    #eg-bubble .eg-actions { margin-top: 10px; display: flex; gap: 8px; justify-content: flex-end; }
    #eg-bubble button { font: inherit; border: 0; border-radius: 6px; padding: 4px 10px; cursor: pointer; }
    #eg-bubble .eg-primary { background: #1a1a1a; color: #fff; }
    #eg-bubble .eg-tag { font-size: 11px; color: #8a6d2b; letter-spacing: .04em; text-transform: uppercase; }
  `;
  document.head.appendChild(style);

  // Find the smallest visible element whose own text matches, then climb to a sensible container.
  function findByText(text) {
    if (!text) return null;
    const want = text.toLowerCase();
    let best = null;
    for (const el of document.querySelectorAll("body *")) {
      if (el.closest("#eg-bubble")) continue;
      const t = (el.innerText || "").trim().toLowerCase();
      if (!t.includes(want)) continue;
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) continue;
      if (!best || t.length < (best.innerText || "").length) best = el;
    }
    return best;
  }

  // A data-guide id first, then a selector, then visible text.
  function target(opts) {
    if (opts.guide) {
      const el = document.querySelector(`[data-guide="${CSS.escape(opts.guide)}"]`);
      if (el) return { el, via: "guide" };
    }
    if (opts.selector) {
      const el = document.querySelector(opts.selector);
      if (el) return { el, via: "selector" };
    }
    let el = findByText(opts.match);
    for (let i = 0; el && i < (opts.climb || 0); i++) el = el.parentElement;
    return el ? { el, via: "text" } : null;
  }

  // The app sets window.evidentGuideReady once the route has loaded its data. Builds without
  // guide hooks never set it, so only wait for it when the page has data-guide hooks.
  function ready() {
    return window.evidentGuideReady === true || !document.querySelector("[data-guide]");
  }

  function clear() {
    document.getElementById("eg-ring")?.remove();
    document.getElementById("eg-bubble")?.remove();
  }

  function node(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text) el.textContent = text;
    return el;
  }

  let lastAnswer = null;

  function show(opts) {
    if (!ready()) return { ok: false, reason: "not ready" };
    clear();
    const found = target(opts);
    if (!found) return { ok: false, reason: "target not found" };
    const el = found.el;
    el.scrollIntoView({ block: "center" });
    const r = el.getBoundingClientRect();
    const pad = 6;

    const ring = node("div");
    ring.id = "eg-ring";
    Object.assign(ring.style, {
      left: `${r.left - pad}px`, top: `${r.top - pad}px`,
      width: `${r.width + pad * 2}px`, height: `${r.height + pad * 2}px`,
    });
    document.body.appendChild(ring);

    // Text goes in as text: it names the user's own data, which must never run as markup.
    const b = node("div");
    b.id = "eg-bubble";
    if (opts.tag) b.appendChild(node("div", "eg-tag", opts.tag));
    if (opts.title) b.appendChild(node("b", "", opts.title));
    b.appendChild(node("div", "", opts.text));
    const actions = node("div", "eg-actions");
    (opts.buttons || ["Got it"]).forEach((label, i) => {
      const btn = node("button", i === 0 ? "eg-primary" : "", label);
      btn.addEventListener("click", () => { lastAnswer = label; clear(); });
      actions.appendChild(btn);
    });
    b.appendChild(actions);
    document.body.appendChild(b);

    // Place the bubble below the target, or above if there is no room.
    const bh = b.offsetHeight, bw = b.offsetWidth;
    const below = r.bottom + 14 + bh < innerHeight;
    b.style.top = `${below ? r.bottom + 14 : Math.max(8, r.top - bh - 14)}px`;
    b.style.left = `${Math.min(Math.max(8, r.left), innerWidth - bw - 8)}px`;
    return { ok: true, via: found.via, rect: { x: r.left, y: r.top, w: r.width, h: r.height } };
  }

  // Claude polls this to learn which button the user pressed.
  function answer() { const a = lastAnswer; lastAnswer = null; return a; }

  window.evidentGuide = { show, clear, answer, ready };
})();
