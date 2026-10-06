// Menu de la cabecera. Es un popover nativo: abre y cierra sin JavaScript (la hamburguesa lleva
// popovertarget). Esto solo lo cierra al elegir un enlace, porque un ancla de la misma pagina no
// navega y el popover se quedaria abierto encima del contenido.
(() => {
	"use strict";
	const menu = document.getElementById("menu");
	if (!menu || typeof menu.hidePopover !== "function") return;
	menu.addEventListener("click", (e) => {
		if (e.target.closest("a") && menu.matches(":popover-open")) menu.hidePopover();
	});
})();
