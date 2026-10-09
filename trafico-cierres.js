/* Controles de trafico, ruido y cierre de calles (solo en la actualidad).
   Todo el calculo vive en modulo-08-3d.js (window.__trafico); aqui solo estan los botones, los contadores y los iconos de "cerrado". */
(function () {
  "use strict";
  function h(tag, attrs) {
    const e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(k => { if (k === "text") e.textContent = attrs[k]; else if (k === "class") e.className = attrs[k]; else e.setAttribute(k, attrs[k]); });
    for (let i = 2; i < arguments.length; i++) { const c = arguments[i]; if (c != null) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); }
    return e;
  }
  const ic = n => h("i", { class: "fa-solid " + n, "aria-hidden": "true" });

  function iniciar() {
    const host = document.querySelector(".main") || document.body;
    const bTraf = h("button", { type: "button", class: "tf-ic", "aria-pressed": "false", title: "Carros en movimiento", "aria-label": "Carros en movimiento" }, ic("fa-car"));
    const bRuido = h("button", { type: "button", class: "tf-ic", "aria-pressed": "false", title: "Mapa de ruido", "aria-label": "Mapa de ruido" }, ic("fa-volume-high"));
    const nCarros = h("b", { text: "0" }), nRet = h("b", { text: "0" });
    const chipCarros = h("span", { class: "tf-chip", title: "Carros circulando" }, ic("fa-car"), nCarros);
    const chipRet = h("span", { class: "tf-chip tf-ret", title: "Carros retirados por las calles cerradas" }, ic("fa-ban"), nRet);
    const bCali = h("button", { type: "button", class: "tf-btn", "aria-pressed": "false" }, ic("fa-ban"), ic("fa-road"), h("span", { text: "Cerrar Cali y Américas" }));
    const bCalle = h("button", { type: "button", class: "tf-btn", "aria-pressed": "false" }, ic("fa-hand-pointer"), h("span", { text: "Cerrar una calle" }));
    const bReab = h("button", { type: "button", class: "tf-ic", title: "Reabrir todas las calles", "aria-label": "Reabrir todas las calles" }, ic("fa-rotate-left"));
    const ayuda = h("div", { class: "tf-ayuda", role: "status" });
    const panel = h("aside", { id: "traficoPanel", class: "tf", "aria-label": "Tráfico y ruido" },
      h("div", { class: "tf-fila" }, bTraf, bRuido, chipCarros, chipRet),
      bCali,
      h("div", { class: "tf-fila" }, bCalle, bReab),
      ayuda,
      h("div", { class: "tf-leyenda", title: "Nivel de ruido: de bajo (amarillo) a alto (rojo)" }, ic("fa-volume-low"), h("span", { class: "barra" }), ic("fa-volume-high")),
      h("div", { class: "tf-nota" }, ic("fa-circle-info"), h("span", { text: "Los carros de las calles cerradas se retiran; no se simula el desvío del tráfico." })));
    panel.style.display = "none";
    host.appendChild(panel);
    const capa = h("div", { id: "marcasCierre" }); host.appendChild(capa);
    const T = () => window.__trafico;
    bTraf.addEventListener("click", () => T() && T().alternarActivo());
    bRuido.addEventListener("click", () => T() && T().alternarRuido());
    bCali.addEventListener("click", () => T() && T().alternarCaliAmericas());
    bCalle.addEventListener("click", () => T() && T().alternarModoCierre());
    bReab.addEventListener("click", () => T() && T().reabrirTodo());
    const eraActual = () => { const a = document.querySelector(".year-btn.active"); return a ? Number(a.dataset.year) : 0; };

    function actualizar() {
      const t = T(); if (!t) return;
      const e = t.estado(), vis = eraActual() === 2024;
      panel.style.display = vis ? "" : "none";
      if (!vis) { capa.style.display = "none"; return; }
      capa.style.display = "";
      bTraf.setAttribute("aria-pressed", String(e.activo)); bRuido.setAttribute("aria-pressed", String(e.ruido));
      const ambas = ["cali", "americas"].every(k => e.cierres.some(c => c.grupo === k));
      bCali.setAttribute("aria-pressed", String(ambas)); bCali.querySelector("span").textContent = ambas ? "Reabrir Cali y Américas" : "Cerrar Cali y Américas";
      bCali.disabled = !e.presets;
      bCalle.setAttribute("aria-pressed", String(e.modoCierre));
      nCarros.textContent = String(e.carros); nRet.textContent = String(e.retirados);
      chipRet.style.display = e.cierres.length ? "" : "none";
      bReab.disabled = !e.cierres.length;
      ayuda.textContent = e.modoCierre ? "Haz clic sobre una calle del mapa. Otro clic sobre ella la reabre." : "";
      ayuda.style.display = e.modoCierre ? "" : "none";
      // un icono de "cerrado" en cada marca; al hacer clic se reabre esa calle
      const marcas = [];
      e.cierres.forEach(c => c.marcas.forEach(m => marcas.push({ id: c.id, nombre: c.nombre, x: m[0], z: m[1] })));
      while (capa.children.length < marcas.length) {
        const b = h("button", { type: "button", class: "tf-marca" }, ic("fa-ban"));
        b.addEventListener("click", () => { const id = Number(b.dataset.id); if (T() && T().reabrir) T().reabrir(id); });
        capa.appendChild(b);
      }
      while (capa.children.length > marcas.length) capa.removeChild(capa.lastChild);
      marcas.forEach((m, i) => { const b = capa.children[i]; b.dataset.id = String(m.id); b.dataset.x = String(m.x); b.dataset.z = String(m.z); b.title = m.nombre + " cerrada (clic para reabrir)"; b.setAttribute("aria-label", m.nombre + " cerrada; clic para reabrir"); });
    }
    function colocar() {
      requestAnimationFrame(colocar);
      if (!window.__proyectarAPantalla || capa.style.display === "none") return;
      const W = window.innerWidth, H = window.innerHeight;
      for (let i = 0; i < capa.children.length; i++) {
        const b = capa.children[i], q = window.__proyectarAPantalla(Number(b.dataset.x), 3, Number(b.dataset.z));
        const fuera = q[0] < 335 || q[0] > W - 14 || q[1] < 20 || q[1] > H - 90;
        b.style.display = fuera ? "none" : "";
        if (!fuera) b.style.transform = "translate(" + Math.round(q[0]) + "px," + Math.round(q[1]) + "px) translate(-50%,-50%)";
      }
    }
    window.addEventListener("trafico:cambio", actualizar);
    document.querySelectorAll(".year-btn").forEach(b => new MutationObserver(actualizar).observe(b, { attributes: true, attributeFilter: ["class"] }));
    setInterval(actualizar, 500);
    requestAnimationFrame(colocar); actualizar();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
})();
