# Política de privacidad: Just One More Bet

**Versión 1.0 — vigente desde el 2026-10-05**

### En resumen

- Si **aceptas**, al terminar cada partida el juego envía un resumen de esa partida para que
  podamos **balancear el juego**. Si no aceptas, no se envía nada.
- **No** enviamos tu nombre, tu correo ni ningún dato de cuenta. El juego no tiene cuentas.
- Cada resumen va con un **número aleatorio** que identifica esta instalación del juego, no a ti.
  Como ese número se repite entre partidas, estos datos **no son totalmente anónimos**: son
  seudónimos.
- Los datos se guardan en **Supabase**, en servidores de **Estados Unidos**.
- No hay anuncios, no vendemos datos y no los compartimos con nadie para publicidad.
- Puedes cambiar de opinión cuando quieras en **Configuración → Enviar estadísticas de partida**.

### Quiénes somos y cómo contactarnos

Somos **Walter Daniel Mejía Palacios** y **Samuel Fernando Calderón Reyes**, los desarrolladores
de *Just One More Bet*. No somos una empresa: somos dos personas que hacen este juego.
Respondemos juntos de estos datos.

Para cualquier pregunta o solicitud sobre tus datos, escribe a cualquiera de los dos; los dos
atendemos solicitudes:

- waltermejia61@hotmail.com
- sfernandocalderon@gmail.com

### Qué datos se envían

Solo si aceptaste, se envía **una fila por partida** con lo siguiente:

| Dato | Qué es |
|---|---|
| ID de partida | Un número aleatorio que se crea al empezar la partida. Sirve para no guardar la misma partida dos veces |
| ID de instalación (`jugador_id`) | Un número aleatorio que se crea la primera vez que aceptas y se guarda en tu dispositivo. Sirve para saber cuántas partidas juega la misma instalación (si "vuelve a jugar"). No sale de tu nombre, tu correo ni ningún dato de tu aparato |
| Inicio y fin de la partida | La hora según el reloj de tu dispositivo, en UTC |
| Hora de recepción | La hora en que llegó a nuestro servidor |
| Tiempo jugado | Segundos en los que controlaste al personaje. No cuenta la introducción, la pausa ni el juego minimizado |
| Introducción | Si la viste, la saltaste o no correspondía |
| Día y casino alcanzados | Hasta dónde llegaste |
| Cómo terminó | Deuda pagada, sin dinero, pago incompleto o partida abandonada |
| Semilla | El número que genera tu partida; sirve para reproducirla y buscar errores |
| Dinero final y deuda pagada | En colones del juego (moneda ficticia) |
| Mesas | Por cada juego (tragamonedas, ruleta, blackjack, carreras): cuántas veces jugaste, cuánto apostaste y cuánto ganaste, en moneda ficticia |
| Versión del juego | Por ejemplo, `0.9.0` |
| Plataforma | Windows, Android, web u otra |
| Tipo de compilación | De lanzamiento o de pruebas |

**No enviamos:** nombre, correo, contraseñas, contactos, fotos, ubicación precisa, identificadores
de publicidad ni identificadores de hardware del dispositivo. Nuestra tabla no tiene ninguna
columna para tu dirección IP.

### Lo que registra nuestro proveedor (Supabase)

Como cualquier servidor de internet, Supabase recibe la **dirección IP** desde la que llega cada
envío y guarda registros técnicos con esa IP y una **ubicación aproximada** (país y ciudad
deducidos de la IP). En nuestro plan actual, esos registros se borran a **1 día**.

No usamos esos registros para identificar a nadie ni los cruzamos con las filas de partidas.

### Qué se guarda en tu dispositivo

- **Tu elección** (si aceptaste o no), para no preguntarte en cada partida.
- **El ID de instalación**, solo después de que aceptes.
- **Una cola de envíos pendientes**: si no hay conexión, las filas esperan en tu dispositivo (como
  máximo 200; si se llena, se descartan las más viejas) y se reintentan al abrir el juego y al
  terminar cada partida.
- **Una partida en curso**: si cierras el juego a mitad de partida o se cierra solo, la próxima vez
  se envía como "abandonada" con lo que alcanzaste a jugar (solo si aceptaste).
- **Estadísticas locales** de tus partidas, que el juego usa sin enviarlas a ninguna parte.

En la versión web, todo esto vive en el almacenamiento de tu navegador. Si lo borras, o tu
navegador lo borra (por ejemplo, en modo privado), el juego te volverá a preguntar y, si aceptas,
creará un ID nuevo.

### Para qué usamos los datos

Solo para **balancear y mejorar el juego**: ver dónde se atasca la gente, si la deuda es
demasiado dura o demasiado fácil, si un juego de mesa paga de más o de menos, y si la gente vuelve
a jugar. No los usamos para publicidad, no hacemos perfiles para tomar decisiones sobre ti y no
los vendemos.

### Por qué podemos tratarlos (base legal)

Tu **consentimiento**, que das al pulsar "Sí, enviar". Puedes retirarlo en cualquier momento, tan
fácil como lo diste, en Configuración. Retirarlo no afecta a lo que se envió antes, pero puedes
pedirnos que lo borremos (ver "Tus derechos").

### Cuándo se envían

Al terminar cada partida (deuda pagada, sin dinero, pago incompleto o al abandonarla desde el
menú), y al abrir el juego si quedó algo pendiente. El juego nunca espera a la red: si el envío
falla, sigues jugando y se reintenta más tarde.

### Quién recibe los datos y dónde están

- **Supabase** guarda la base de datos por cuenta nuestra (actúa como encargado del tratamiento).
  El proyecto está alojado en **Estados Unidos** (región `us-west-2`). Supabase usa a su vez
  otros proveedores (por ejemplo, Amazon Web Services y Cloudflare); su lista está en
  https://supabase.com/legal/customer-resources/subprocessor-list.
- Nuestro contrato con Supabase incluye su acuerdo de tratamiento de datos, con las **cláusulas
  contractuales tipo** de la Comisión Europea para los datos que salen de la UE o del Reino Unido:
  https://supabase.com/legal/customer-resources/data-processing-addendum.
- Nadie más recibe los datos. Con la llave pública que lleva el juego solo se puede **añadir**
  filas: nadie puede leerlas, cambiarlas ni borrarlas con ella.
- Si descargas o juegas *Just One More Bet* en **itch.io**, itch.io trata tus datos según su
  propia política: https://itch.io/docs/legal/privacy-policy. Esta política solo cubre lo que
  envía nuestro juego.

### Cuánto tiempo los guardamos

- **Filas de partidas:** **24 meses** desde que llegan al servidor. Después se
  borran automáticamente. Podemos conservar sin límite **totales agregados** (por ejemplo, "media
  de días alcanzados en la versión 0.9"), que ya no tienen ningún ID y no se pueden relacionar
  con nadie.
- **Registros técnicos de Supabase (con IP):** 1 día en nuestro plan actual.
- **En tu dispositivo:** hasta que apagues el envío, borres los datos del juego o lo desinstales.

### Tus opciones

- **No aceptar:** no se envía nada y no se crea ningún ID.
- **Apagar el envío** en Configuración: se vacía la cola de envíos pendientes y no se envía nada
  más. también se borra el ID de tu dispositivo; si vuelves a activarlo, se
  crea uno nuevo.
- **Desinstalar el juego** o, en la web, borrar los datos del sitio: se borra todo lo que el juego
  guardó en tu dispositivo.

### Tus derechos

Según dónde vivas (por ejemplo, en la Unión Europea, el Espacio Económico Europeo o el Reino
Unido), tienes derecho a **acceder** a tus datos, **corregirlos**, **borrarlos**, **oponerte** a su
uso, **limitarlo**, **llevártelos** y **retirar tu consentimiento**.

Como no sabemos quién eres, solo podemos encontrar tus datos si nos das el **ID de instalación**.
lo ves en Configuración, junto al interruptor, con un botón para copiarlo.
Escríbenos a cualquiera de los dos correos con ese ID y lo que quieres que hagamos. Te
responderemos en un plazo máximo de **un mes**. Si ya borraste el ID de tu dispositivo, no
podemos saber qué filas eran tuyas; en ese caso esos datos solo se borran al cumplirse el plazo
de conservación.

Si crees que no tratamos bien tus datos, puedes reclamar ante la autoridad de protección de datos
de tu país.

### Menores

*Just One More Bet* es un juego **para mayores de 18 años**: tiene apuestas simuladas, alcohol y
tabaco. No está pensado para menores ni dirigido a ellos, y no preguntamos la edad. Si eres madre,
padre o tutor y crees que un menor nos envió datos, escríbenos con el ID de instalación y los
borramos.

### Seguridad

Los datos viajan cifrados (HTTPS). La base de datos solo admite añadir filas con la llave pública
del juego; leerlas o borrarlas requiere una llave privada que no está en el juego ni en el código
publicado. Supabase cifra los datos guardados.

### Cambios en esta política

Si cambiamos lo que recoge el juego, actualizaremos esta política **antes** de publicar esa
versión, cambiaremos la fecha de arriba y lo anunciaremos en el devlog de la página de itch.io. Si
el cambio es importante, el juego te volverá a preguntar.

Dirección de esta política: https://just-one-more-bet-web.vercel.app/privacidad
