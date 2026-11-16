// Overlay Claude injects into the Evident app to point at things.
// Usage from Claude:
//   evidentGuide.show({ guide: "settings-approvals-download", match: "Approve before download", text: "..." })
// `guide` is a data-guide id; `match` is visible text, used when the id is not on the page.
// Pass step and steps to number the bubble ("2 of 4"). Every bubble says "Evident is showing this"
// and has a close button; answer() returns "dismissed" after the user closes it.
// Returns { ok: true, via } or { ok: false, reason }. "not ready" means call again shortly;
// pass force: true to draw anyway when the page never reports ready. "not evident" means this page
// is not Evident's own app: the guide never draws over anyone else's site.
(() => {
  // Evident's own app only: production, dev and a local build. Never a customer's portal or any other site.
  // Checked before anything else, so a page that defines its own evidentGuide cannot skip it.
  const host = location.hostname;
  const onEvident = host.endsWith(".evident.security") || host.endsWith(".trustmind.com") ||
    host === "localhost" || host === "127.0.0.1";
  if (!onEvident) {
    const refuse = () => ({ ok: false, reason: "not evident" });
    window.evidentGuide = { show: refuse, clear() {}, answer: () => null, ready: () => false };
    return;
  }
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
    #eg-bubble .eg-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
    #eg-bubble .eg-head .eg-tag { flex: 1; }
    #eg-bubble .eg-count { font-size: 11px; color: #6b6b6b; }
    #eg-bubble .eg-close { background: none; padding: 0 4px; font-size: 16px; line-height: 1; color: #6b6b6b; }
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
    if (!opts.force && !ready()) return { ok: false, reason: "not ready" };
    lastAnswer = null;
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
    const head = node("div", "eg-head");
    head.appendChild(node("div", "eg-tag", "Evident is showing this"));
    if (opts.step && opts.steps) head.appendChild(node("span", "eg-count", `${opts.step} of ${opts.steps}`));
    const close = node("button", "eg-close", "\u00d7");
    close.setAttribute("aria-label", "Close");
    close.addEventListener("click", () => { lastAnswer = "dismissed"; clear(); });
    head.appendChild(close);
    b.appendChild(head);
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
