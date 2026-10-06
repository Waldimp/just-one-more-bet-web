/* Just One More Bet — web oficial. Sin dependencias.
 *
 * Piezas, en el orden de la pagina:
 *   hero()      el parqueo de noche en un canvas: paneo, zoom a la boca del leon, bombillas
 *   topbar()    la barra se vuelve solida al salir del hero
 *   reveals()   revelados al entrar en pantalla y carretes de los encabezados
 *   odometer()  la deuda que sube digito a digito
 *   day()       el HUD del dia: reloj de 150 s, acciones y plata ligados al scroll
 *   casinoMap() el plano del casino: arrastrar, zoom y viaje a cada sala
 *   viewer()    capturas a pantalla completa en un <dialog>
 *   trailer()   el video solo se carga al pulsar; si aun no existe, lo dice
 *   coins()     lluvia de monedas en la llamada final y palanca del boton
 *
 * Todo respeta prefers-reduced-motion: sin paneo ni zoom, bombillas fijas, sin lluvia.
 */
(() => {
	"use strict";

	const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
	let reduced = motionQuery.matches;
	const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
	const lerp = (a, b, t) => a + (b - a) * t;
	const smooth = (t) => t * t * (3 - 2 * t);

	/* ------------------------------------------------------------------ hero */

	function hero() {
		const root = document.querySelector(".hero");
		if (!root) return;
		const canvas = root.querySelector(".hero__canvas");
		const copy = root.querySelector(".hero__copy");
		const enter = root.querySelector(".hero__enter");
		const curtain = root.querySelector(".hero__curtain");
		const ctx = canvas.getContext("2d", { alpha: false });
		if (!ctx) return;

		// Coordenadas de arte (pixeles del juego). La capa de fondo es 160 px mas ancha por
		// cada lado; el resto empieza en x = 0.
		const ART = { w: 640, h: 1088, margin: 160, mouthX: 320, mouthY: 487, facadeTop: 290 };
		const base = root.dataset.art || "/assets/img/hero/";
		const domImg = (cls) => root.querySelector(cls);
		const layers = {
			back: domImg(".l-back"),
			sign: domImg(".l-sign"),
			front: domImg(".l-front"),
			bulbs: { sign: [], band: [] },
		};
		for (const g of ["sign", "band"]) {
			for (let i = 0; i < 3; i++) {
				const im = new Image();
				im.decoding = "async";
				im.src = `${base}hero-bulbs-${g}-${i}.webp`;
				layers.bulbs[g].push(im);
			}
		}

		let vw = 0, vh = 0, dpr = 1, scale = 1;
		let camY0 = 0, camY1 = 0, cx0 = ART.mouthX;
		let progress = 0;
		let phase = 0;
		let mouse = { x: 0, y: 0 }, mouseTarget = { x: 0, y: 0 };
		let raf = 0, ticking = null, visible = true;

		const ready = (im) => im.complete && im.naturalWidth > 0;
		const loaded = (im) =>
			ready(im) ? Promise.resolve() : new Promise((ok) => {
				im.addEventListener("load", ok, { once: true });
				im.addEventListener("error", ok, { once: true });
			});

		function measure() {
			vw = window.innerWidth;
			vh = root.querySelector(".hero__sticky").clientHeight;
			dpr = Math.min(window.devicePixelRatio || 1, 2);
			canvas.width = Math.round(vw * dpr);
			canvas.height = Math.round(vh * dpr);
			// Escala entera: el pixel del juego nunca se reparte entre dos tamanos en reposo.
			// Y que debajo de la cornisa quepan al menos ~200 filas de arte: la cara y la boca del
			// leon tienen que verse antes de hacer scroll. En pantallas bajas se acepta 2 igual.
			scale = clamp(Math.round(vw / 700), 1, 4);
			scale = Math.min(scale, Math.max(2, Math.floor((0.48 * vh) / 200)));
			while (scale > 1 && vh / scale < 300) scale--;
			const visW = vw / scale;
			// En pantallas estrechas el encuadre se corre a la izquierda para que quepa el cartel.
			cx0 = visW < 640 ? ART.mouthX - (640 - visW) * 0.22 : ART.mouthX;
			// La cornisa de la fachada cae justo debajo del texto del hero (o a media pantalla si
			// el texto es corto): el titulo queda sobre el tejado, que de noche es oscuro.
			const copyBottom = copy.offsetTop + copy.offsetHeight;
			const anchor = Math.max(vh * (vw < 760 ? 0.46 : 0.52), copyBottom + 18);
			camY0 = ART.facadeTop - anchor / scale;
			camY1 = ART.mouthY - vh / 2 / scale;
			if (camY1 < camY0) camY1 = camY0;
			draw();
		}

		function readProgress() {
			if (reduced) return 0;
			const span = root.offsetHeight - vh;
			if (span <= 0) return 0;
			return clamp(-root.getBoundingClientRect().top / span);
		}

		// Dibuja una capa con su rectangulo de origen recortado a lo visible: con el zoom, la
		// capa entera mediria decenas de miles de pixeles.
		function drawLayer(im, artX, artY, z, ox, oy) {
			if (!ready(im)) return;
			const W = canvas.width, H = canvas.height;
			const k = z * dpr;
			let sx = (0 - ox) / k - artX, sy = (0 - oy) / k - artY;
			let sw = W / k, sh = H / k;
			let dx = 0, dy = 0, dw = W, dh = H;
			if (sx < 0) { dx = -sx * k; dw -= dx; sw += sx; sx = 0; }
			if (sy < 0) { dy = -sy * k; dh -= dy; sh += sy; sy = 0; }
			if (sx + sw > im.naturalWidth) { const cut = sx + sw - im.naturalWidth; sw -= cut; dw -= cut * k; }
			if (sy + sh > im.naturalHeight) { const cut = sy + sh - im.naturalHeight; sh -= cut; dh -= cut * k; }
			if (sw <= 0 || sh <= 0 || dw <= 0 || dh <= 0) return;
			ctx.drawImage(im, sx, sy, sw, sh, dx, dy, dw, dh);
		}

		function draw() {
			raf = 0;
			progress = readProgress();
			const p = progress;
			const tPan = smooth(clamp(p / 0.3));
			const tZoom = clamp((p - 0.3) / 0.62);

			// Camara: centro (cx, cy) en pixeles de arte y zoom z en px CSS por pixel de arte.
			const cx = lerp(cx0, ART.mouthX, tPan);
			const camY = lerp(camY0, camY1, tPan);
			const zEnd = Math.max(vw / 26, vh / 34);
			const z = scale * Math.pow(zEnd / scale, Math.pow(tZoom, 1.7));
			const cy = camY + vh / 2 / scale;

			// Origen de la capa (arte x=0, y=0) en pixeles del canvas. Redondeado en reposo.
			let ox = (vw / 2 - cx * z) * dpr;
			let oy = (vh / 2 - cy * z) * dpr;
			if (tZoom === 0) { ox = Math.round(ox); oy = Math.round(oy); }

			// Parallax: el cartel y el primer plano se mueven algo mas que la fachada.
			const pan = camY - camY0;
			const fade = 1 - tZoom;
			const signX = -mouse.x * 4 * fade, signY = (-pan * 0.08 - mouse.y * 2) * fade;
			const frontX = -mouse.x * 9 * fade, frontY = (-pan * 0.22 - mouse.y * 4) * fade;

			ctx.imageSmoothingEnabled = false;
			ctx.fillStyle = "#06080d";
			ctx.fillRect(0, 0, canvas.width, canvas.height);
			// Las bombillas de la fachada van con la fachada; las del cartel, con el cartel.
			const on = reduced ? [0, 1, 2] : [0, 1, 2].filter((i) => i !== phase);
			drawLayer(layers.back, -ART.margin, 0, z, ox, oy);
			for (const i of on) drawLayer(layers.bulbs.band[i], 0, 0, z, ox, oy);
			drawLayer(layers.sign, signX, signY, z, ox, oy);
			for (const i of on) drawLayer(layers.bulbs.sign[i], signX, signY, z, ox, oy);
			drawLayer(layers.front, frontX, frontY, z, ox, oy);

			// Texto, flecha y cortina a negro.
			const copyFade = clamp(p / 0.2);
			copy.style.opacity = String(1 - copyFade);
			copy.style.transform = `translate3d(0, ${(-p * 220).toFixed(1)}px, 0)`;
			copy.style.visibility = copyFade >= 1 ? "hidden" : "visible";
			enter.style.opacity = String(1 - clamp(p / 0.06));
			curtain.style.opacity = String(clamp((p - 0.84) / 0.12));

			// Sigue moviendo el parallax del raton hasta que llegue.
			if (Math.abs(mouse.x - mouseTarget.x) > 0.002 || Math.abs(mouse.y - mouseTarget.y) > 0.002) {
				mouse.x = lerp(mouse.x, mouseTarget.x, 0.08);
				mouse.y = lerp(mouse.y, mouseTarget.y, 0.08);
				request();
			}
		}

		function request() {
			if (!raf && visible) raf = requestAnimationFrame(draw);
		}

		// Persecucion de la marquesina: tres fases, una apagada cada vez.
		function startBulbs() {
			if (ticking || reduced) return;
			ticking = setInterval(() => {
				phase = (phase + 1) % 3;
				request();
			}, 320);
		}

		function stopBulbs() {
			clearInterval(ticking);
			ticking = null;
		}

		Promise.all([layers.back, layers.sign, layers.front].map(loaded)).then(() => {
			measure();
			root.classList.add("is-live");
			startBulbs();
		});
		[...layers.bulbs.sign, ...layers.bulbs.band].forEach((im) =>
			im.addEventListener("load", request, { once: true }));

		window.addEventListener("scroll", request, { passive: true });
		window.addEventListener("resize", () => measure(), { passive: true });
		if (window.matchMedia("(pointer: fine)").matches) {
			window.addEventListener("pointermove", (e) => {
				if (reduced || progress > 0.3) return;
				mouseTarget = { x: (e.clientX / vw) * 2 - 1, y: (e.clientY / vh) * 2 - 1 };
				request();
			}, { passive: true });
		}
		new IntersectionObserver(([entry]) => {
			visible = entry.isIntersecting;
			if (visible) { startBulbs(); request(); } else { stopBulbs(); }
		}).observe(root);
		motionQuery.addEventListener("change", (e) => {
			reduced = e.matches;
			if (reduced) stopBulbs(); else startBulbs();
			measure();
		});
	}

	/* ------------------------------------------------------------------ barra superior */

	function topbar() {
		const bar = document.querySelector(".topbar");
		const hero = document.querySelector(".hero");
		if (!bar) return;
		const update = () => {
			const limit = hero ? hero.offsetHeight - window.innerHeight * 0.15 : 10;
			bar.classList.toggle("is-solid", window.scrollY > limit);
		};
		update();
		window.addEventListener("scroll", update, { passive: true });
		window.addEventListener("resize", update, { passive: true });
	}

	/* ------------------------------------------------------------------ revelados y carretes */

	function reels() {
		document.querySelectorAll(".reel[data-pin]").forEach((reel) => {
			const strip = reel.querySelector(".reel__strip");
			const final = Number(reel.dataset.pin);
			const spins = 9;
			const icons = [];
			let seed = final * 7 + 3;
			for (let i = 0; i < spins; i++) {
				seed = (seed * 13 + 5) % 32;
				icons.push(seed === final ? (seed + 1) % 32 : seed);
			}
			const frag = document.createDocumentFragment();
			for (const n of icons) {
				const i = document.createElement("i");
				i.style.setProperty("--x", String(n % 8));
				i.style.setProperty("--y", String(Math.floor(n / 8)));
				frag.appendChild(i);
			}
			strip.prepend(frag);
			strip.style.setProperty("--stop", String(spins));
		});
	}

	function reveals() {
		const targets = document.querySelectorAll(
			".reveal, .kicker, .contract, .ladder, .screen, .smoke, .is-drunk, .collector, .strip"
		);
		if (!("IntersectionObserver" in window)) {
			targets.forEach((el) => el.classList.add("is-in"));
			return;
		}
		const io = new IntersectionObserver((entries) => {
			for (const e of entries) {
				if (!e.isIntersecting) continue;
				e.target.classList.add("is-in");
				io.unobserve(e.target);
				if (e.target.querySelector(".odometer")) runOdometer(e.target);
			}
		}, { threshold: 0.2, rootMargin: "0px 0px -8% 0px" });
		targets.forEach((el) => io.observe(el));
	}

	/* ------------------------------------------------------------------ odometro de la deuda */

	function odometer() {
		document.querySelectorAll(".odometer").forEach((el) => {
			const text = el.dataset.text || el.textContent.trim();
			el.textContent = "";
			const label = document.createElement("span");
			label.className = "visually-hidden";
			label.textContent = text;
			const reelBox = document.createElement("span");
			reelBox.setAttribute("aria-hidden", "true");
			reelBox.style.display = "inline-flex";
			let digitIndex = 0;
			const digits = [...text].filter((c) => /\d/.test(c)).length;
			for (const ch of text) {
				if (!/\d/.test(ch)) {
					const s = document.createElement("span");
					s.textContent = ch;
					reelBox.appendChild(s);
					continue;
				}
				const d = document.createElement("span");
				d.className = "digit";
				const inner = document.createElement("span");
				// Dos vueltas de 0 a 9 y luego el digito: gira como un carrete y para.
				const seq = [];
				for (let r = 0; r < 2; r++) for (let n = 0; n < 10; n++) seq.push(n);
				seq.push(Number(ch));
				inner.innerHTML = seq.map((n) => `<span>${n}</span>`).join("");
				inner.dataset.stop = String(seq.length - 1);
				// Para de izquierda a derecha, como los carretes.
				inner.style.setProperty("--t", `${1.1 + (digitIndex / digits) * 1.4}s`);
				d.appendChild(inner);
				reelBox.appendChild(d);
				digitIndex++;
			}
			el.append(label, reelBox);
			if (reduced) settleOdometer(el);
		});
	}

	function settleOdometer(el) {
		el.querySelectorAll(".digit > span").forEach((inner) => {
			inner.style.transform = `translateY(-${Number(inner.dataset.stop) * 1.1}em)`;
		});
	}

	function runOdometer(scope) {
		scope.querySelectorAll(".odometer").forEach(settleOdometer);
	}

	/* ------------------------------------------------------------------ el dia */

	function day() {
		const section = document.querySelector(".day");
		if (!section) return;
		const hud = section.querySelector(".hud");
		const steps = section.querySelector(".steps");
		const clock = hud.querySelector(".hud__clock");
		const bar = hud.querySelector(".hud__bar");
		const chips = [...hud.querySelectorAll(".hud__chip")];
		const money = hud.querySelector(".hud__money");
		const note = hud.querySelector(".hud__note");
		const actions = [...section.querySelectorAll("[data-action]")];
		const notes = [...section.querySelectorAll("[data-note]")];
		const startMoney = money.textContent;
		const total = Number(hud.dataset.seconds || 150);
		let raf = 0;

		const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

		function update() {
			raf = 0;
			// 0 cuando el primer paso cruza la mitad de la pantalla; 1 cuando la cruza el ultimo,
			// el del cobrador: ahi el reloj marca 0:00.
			const mid = window.innerHeight * 0.55;
			const items = steps.children;
			const a = items[0].getBoundingClientRect().top;
			const b = items[items.length - 1].getBoundingClientRect().top;
			const p = clamp((mid - a) / Math.max(1, b - a));
			const left = Math.round(total * (1 - p));
			clock.textContent = fmt(left);
			bar.style.setProperty("--left", String(1 - p));
			hud.classList.toggle("is-late", left <= 30 && left > 0);
			hud.classList.toggle("is-over", left === 0);

			let spent = 0, cash = startMoney;
			for (const a of actions) {
				if (a.getBoundingClientRect().top < mid) {
					spent++;
					cash = a.dataset.money || cash;
				}
			}
			chips.forEach((c, i) => c.classList.toggle("is-spent", i >= chips.length - spent));
			money.textContent = cash;

			let current = notes[0];
			for (const n of notes) if (n.getBoundingClientRect().top < mid) current = n;
			if (current && note.textContent !== current.dataset.note) note.textContent = current.dataset.note;
		}

		const request = () => { if (!raf) raf = requestAnimationFrame(update); };
		window.addEventListener("scroll", request, { passive: true });
		window.addEventListener("resize", request, { passive: true });
		update();
	}

	/* ------------------------------------------------------------------ plano del casino */

	function casinoMap() {
		const box = document.querySelector(".map");
		if (!box) return;
		const view = box.querySelector(".map__view");
		const img = box.querySelector(".map__img");
		const marks = box.querySelector(".map__marks");
		const buttons = [...box.querySelectorAll(".rooms button")];
		const card = box.querySelector(".room-card");
		const cardTitle = card.querySelector("h3");
		const cardText = card.querySelector("p");
		const cardShot = card.querySelector("img");
		const cardZoom = card.querySelector(".zoomable");
		const MAP_W = Number(img.getAttribute("width"));
		const MAP_H = Number(img.getAttribute("height"));
		const zooms = [0, 1, 2]; // 0 = el casino entero
		let zi = 1, s = 1, tx = 0, ty = 0;

		for (const b of buttons) {
			const m = document.createElement("div");
			m.className = "map__mark";
			m.dataset.room = b.dataset.room;
			m.style.cssText = `left:${b.dataset.x}px;top:${b.dataset.y}px;width:${b.dataset.w}px;height:${b.dataset.h}px`;
			const label = document.createElement("span");
			label.textContent = b.dataset.label || b.textContent;
			m.appendChild(label);
			marks.appendChild(m);
		}
		marks.style.width = `${MAP_W}px`;
		marks.style.height = `${MAP_H}px`;

		const fitScale = () => Math.min(view.clientWidth / MAP_W, view.clientHeight / MAP_H);
		const scaleFor = (i) => (zooms[i] === 0 ? fitScale() : zooms[i]);

		function apply(glide) {
			const W = view.clientWidth, H = view.clientHeight;
			const mw = MAP_W * s, mh = MAP_H * s;
			tx = mw <= W ? (W - mw) / 2 : clamp(tx, W - mw, 0);
			ty = mh <= H ? (H - mh) / 2 : clamp(ty, H - mh, 0);
			tx = Math.round(tx);
			ty = Math.round(ty);
			const t = `translate(${tx}px, ${ty}px) scale(${s})`;
			img.classList.toggle("is-gliding", glide && !reduced);
			marks.classList.toggle("is-gliding", glide && !reduced);
			marks.style.transition = glide && !reduced ? "transform .9s cubic-bezier(.2,.8,.2,1)" : "none";
			img.style.transform = t;
			marks.style.transform = t;
			img.style.imageRendering = s < 1 ? "auto" : "pixelated";
		}

		function centerOn(x, y, glide) {
			tx = view.clientWidth / 2 - x * s;
			ty = view.clientHeight / 2 - y * s;
			apply(glide);
		}

		function select(b, glide = true) {
			buttons.forEach((o) => o.setAttribute("aria-pressed", String(o === b)));
			marks.querySelectorAll(".map__mark").forEach((m) =>
				m.classList.toggle("is-active", m.dataset.room === b.dataset.room));
			if (zooms[zi] === 0) { zi = 1; s = 1; }
			const x = Number(b.dataset.x) + Number(b.dataset.w) / 2;
			const y = Number(b.dataset.y) + Number(b.dataset.h) / 2;
			centerOn(x, y, glide);
			cardTitle.textContent = b.dataset.label || b.textContent;
			cardText.textContent = b.dataset.desc;
			cardShot.src = b.dataset.shot;
			cardShot.srcset = `${b.dataset.shot.replace(".webp", "-1x.webp")} 640w, ${b.dataset.shot} 1280w`;
			cardShot.alt = b.dataset.alt;
			cardZoom.dataset.full = b.dataset.shot;
			cardZoom.dataset.caption = b.dataset.alt;
		}

		function zoomTo(i) {
			const W = view.clientWidth, H = view.clientHeight;
			const cxArt = (W / 2 - tx) / s, cyArt = (H / 2 - ty) / s;
			zi = clamp(i, 0, zooms.length - 1);
			s = scaleFor(zi);
			centerOn(cxArt, cyArt, true);
		}

		buttons.forEach((b) => b.addEventListener("click", () => select(b)));
		box.querySelector("[data-zoom='in']").addEventListener("click", () => zoomTo(zi + 1));
		box.querySelector("[data-zoom='out']").addEventListener("click", () => zoomTo(zi - 1));

		// Arrastrar para recorrerlo. En tactil solo en horizontal: el vertical es del scroll.
		let drag = null;
		view.addEventListener("pointerdown", (e) => {
			if (e.button !== 0 || e.target.closest("button")) return;
			drag = { x: e.clientX, y: e.clientY, tx, ty, touch: e.pointerType === "touch" };
			view.setPointerCapture(e.pointerId);
			view.classList.add("is-dragging");
		});
		view.addEventListener("pointermove", (e) => {
			if (!drag) return;
			tx = drag.tx + (e.clientX - drag.x);
			ty = drag.touch ? drag.ty : drag.ty + (e.clientY - drag.y);
			apply(false);
		});
		const end = () => { drag = null; view.classList.remove("is-dragging"); };
		view.addEventListener("pointerup", end);
		view.addEventListener("pointercancel", end);
		view.addEventListener("keydown", (e) => {
			const step = 80;
			const moves = { ArrowLeft: [step, 0], ArrowRight: [-step, 0], ArrowUp: [0, step], ArrowDown: [0, -step] };
			if (moves[e.key]) {
				tx += moves[e.key][0];
				ty += moves[e.key][1];
				apply(true);
				e.preventDefault();
			} else if (e.key === "+" || e.key === "=") {
				zoomTo(zi + 1);
			} else if (e.key === "-") {
				zoomTo(zi - 1);
			}
		});
		window.addEventListener("resize", () => { if (zooms[zi] === 0) s = fitScale(); apply(false); });

		const first = buttons.find((b) => b.getAttribute("aria-pressed") === "true") || buttons[0];
		s = 1;
		select(first, false);
	}

	/* ------------------------------------------------------------------ visor */

	function viewer() {
		const dialog = document.querySelector(".viewer");
		if (!dialog || typeof dialog.showModal !== "function") return;
		const img = dialog.querySelector("img");
		const caption = dialog.querySelector("p");
		document.addEventListener("click", (e) => {
			const trigger = e.target.closest(".zoomable");
			if (!trigger) return;
			e.preventDefault();
			img.src = trigger.dataset.full;
			img.alt = trigger.dataset.caption || "";
			caption.textContent = trigger.dataset.caption || "";
			// Escala entera que quepa: 1280 o 640 de ancho.
			const fits2 = window.innerWidth >= 1310 && window.innerHeight >= 860;
			img.style.width = fits2 ? "1280px" : "";
			dialog.showModal();
		});
		dialog.addEventListener("click", (e) => {
			if (e.target === dialog) dialog.close();
		});
		dialog.querySelector(".viewer__close").addEventListener("click", () => dialog.close());
	}

	/* ------------------------------------------------------------------ trailer */

	function trailer() {
		const screen = document.querySelector(".screen");
		if (!screen) return;
		const video = screen.querySelector("video");
		const button = screen.querySelector(".screen__play");
		const note = screen.querySelector(".screen__note");
		const missing = () => {
			note.hidden = false;
			button.querySelector(".screen__label").textContent = screen.dataset.soon;
		};
		const source = video.querySelector("source");
		if (source) source.addEventListener("error", missing);
		button.addEventListener("click", () => {
			const play = video.play();
			if (play && play.then) {
				play.then(() => {
					screen.classList.add("is-playing");
					video.focus();
				}).catch((err) => {
					if (err && err.name === "NotAllowedError") return;
					missing();
				});
			}
		});
		video.addEventListener("error", missing);
	}

	/* ------------------------------------------------------------------ monedas y palanca */

	function coins() {
		document.querySelectorAll(".btn--play").forEach((b) => {
			b.addEventListener("click", () => {
				b.classList.remove("is-pulled");
				void b.offsetWidth;
				b.classList.add("is-pulled");
				const host = b.closest(".final");
				if (host) rain(host.querySelector(".coins"), 18);
			});
		});
		const final = document.querySelector(".final");
		if (!final || !("IntersectionObserver" in window)) return;
		const io = new IntersectionObserver(([e]) => {
			if (!e.isIntersecting) return;
			rain(final.querySelector(".coins"), 22);
			io.disconnect();
		}, { threshold: 0.45 });
		io.observe(final);
	}

	function rain(host, n) {
		if (!host || reduced) return;
		for (let i = 0; i < n; i++) {
			const c = document.createElement("span");
			c.className = "coin";
			c.style.setProperty("--x", `${Math.random() * 96}%`);
			c.style.setProperty("--dx", `${(Math.random() - 0.5) * 120}px`);
			c.style.setProperty("--t", `${1.6 + Math.random() * 1.6}s`);
			c.style.setProperty("--d", `${Math.random() * 0.9}s`);
			c.style.setProperty("--r", `${(Math.random() - 0.5) * 60}deg`);
			c.addEventListener("animationend", (e) => { if (e.animationName === "coin-fall") c.remove(); });
			host.appendChild(c);
		}
	}

	/* ------------------------------------------------------------------ pines */

	function pins() {
		const caption = document.querySelector(".pins-caption");
		if (!caption) return;
		const show = (b) => { caption.textContent = `${b.dataset.name} · ${b.dataset.rarity}`; };
		document.querySelectorAll(".pin").forEach((b) => {
			b.addEventListener("click", () => show(b));
			b.addEventListener("focus", () => show(b));
			b.addEventListener("pointerenter", () => show(b));
		});
	}

	/* ------------------------------------------------------------------ arranque */

	reels();
	odometer();
	hero();
	topbar();
	reveals();
	day();
	casinoMap();
	viewer();
	trailer();
	coins();
	pins();
})();
