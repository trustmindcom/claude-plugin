// Prototype overlay Claude injects into the Evident app to point at things.
// Usage from Claude: evidentGuide.show({ text: "...", match: "Answer approval" }) or { selector: "..." }
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

  function target(opts) {
    if (opts.selector) return document.querySelector(opts.selector);
    if (opts.guide) return document.querySelector(`[data-guide="${opts.guide}"]`);
    let el = findByText(opts.match);
    for (let i = 0; el && i < (opts.climb || 0); i++) el = el.parentElement;
    return el;
  }

  function clear() {
    document.getElementById("eg-ring")?.remove();
    document.getElementById("eg-bubble")?.remove();
  }

  let lastAnswer = null;

  function show(opts) {
    clear();
    const el = target(opts);
    if (!el) return { ok: false, reason: "target not found" };
    el.scrollIntoView({ block: "center" });
    const r = el.getBoundingClientRect();
    const pad = 6;

    const ring = document.createElement("div");
    ring.id = "eg-ring";
    Object.assign(ring.style, {
      left: `${r.left - pad}px`, top: `${r.top - pad}px`,
      width: `${r.width + pad * 2}px`, height: `${r.height + pad * 2}px`,
    });
    document.body.appendChild(ring);

    const b = document.createElement("div");
    b.id = "eg-bubble";
    b.innerHTML = `${opts.tag ? `<div class="eg-tag">${opts.tag}</div>` : ""}
      ${opts.title ? `<b>${opts.title}</b>` : ""}<div>${opts.text}</div>
      <div class="eg-actions">${(opts.buttons || ["Got it"])
        .map((x, i) => `<button class="${i === 0 ? "eg-primary" : ""}" data-v="${x}">${x}</button>`)
        .join("")}</div>`;
    document.body.appendChild(b);
    b.addEventListener("click", (e) => {
      const v = e.target.dataset && e.target.dataset.v;
      if (!v) return;
      lastAnswer = v;
      clear();
    });

    // Place the bubble below the target, or above if there is no room.
    const bh = b.offsetHeight, bw = b.offsetWidth;
    const below = r.bottom + 14 + bh < innerHeight;
    b.style.top = `${below ? r.bottom + 14 : Math.max(8, r.top - bh - 14)}px`;
    b.style.left = `${Math.min(Math.max(8, r.left), innerWidth - bw - 8)}px`;
    return { ok: true, rect: { x: r.left, y: r.top, w: r.width, h: r.height } };
  }

  // Claude polls this to learn which button the user pressed.
  function answer() { const a = lastAnswer; lastAnswer = null; return a; }

  window.evidentGuide = { show, clear, answer };
})();
