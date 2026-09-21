# Tsumugy-Narrative

**Languages:** [English](README.md) · [日本語](README.ja.md) · [中文](README.zh.md) · [한국어](README.ko.md) · [العربية](README.ar.md) · **Español (aquí)** · [Français](README.fr.md) · [Русский](README.ru.md)

## Qué es esto

https://github.com/user-attachments/assets/82d17d1e-6d3e-4422-b317-80a751a913e5

Mismo vídeo como archivo del repositorio: [demo-claude.mp4](docs/assets/demo-claude.mp4)

> Una skill sencilla que convierte texto en historias de alta calidad. Crea una Historia: un cuerpo de historia, una explicación breve y un marcador de Fuente.

Soy estudiante de medicina. Necesitaba una forma de entender conceptos difíciles en poco tiempo. Intenté dibujar para recordarlos. Le pedí a la IA que dibujara las imágenes por mí. Pero la IA no podía dibujar imágenes exactas. Entonces tuve una idea nueva: convierto una escena que se siente como una imagen en una Historia. Funcionó muy bien. Me ayudó de verdad a entender conceptos complejos. Compartí mis historias con amigos. Dijeron que la estadística en salud pública les resultó muy fácil. Una instrucción simple da un resultado distinto cada vez, así que siempre hay que decirle «hazlo más divertido» o «no entiendo la metáfora». Esta skill incluye un script de autocomprobación. Revisa cada Historia. Así cada Historia mantiene alta calidad, siempre.

Ejemplo de entrada:

```
Buenos días a todas y todos. Hoy cerramos la serie de clases de farmacología. El examen parcial es la semana que viene. Como siempre, responderé vuestras preguntas sobre la marcha. Muchos me habéis pedido un fármaco que quite la somnolencia diurna. Yo también quiero uno. Los antihistamínicos de primera generación cruzan la barrera hematoencefálica, así que provocan somnolencia, sequedad de boca y dificultad para orinar. Los de segunda generación casi no llegan al cerebro, así que calman los síntomas de la alergia sin dar sueño...
(Extracto. Grabación de una clase de 90 minutos.)
```

<details>
<summary>Ejemplo de salida:</summary>

```
## Historia

### Los pequeños fuegos artificiales de la nariz

En una tranquila tarde de primavera, «nieve de polen primaveral»🌸(polen) cayó sin hacer ruido hasta el fondo de la nariz.

Dentro de la nariz, «fuegos artificiales de la nariz»🎆(estornudo) estallaron con un chasquido brillante, y el sonido seco resonó agudo por la cabeza dolorida.

De la «nariz grifo abierto»🚰(rinorrea) el agua goteó gota a gota como lágrimas, y su tacto frío llegó hasta los labios secos.

Un invisible «teléfono de cuerda que zumba»📞(nervio parasimpático) zumbaba detrás del dulce olor de las flores.

Entonces «ladrillos del atasco»🧱(leucotrieno) se apilaron altos a lo ancho del camino de la nariz, y la «linterna bloqueada»🏮(congestión nasal) brilló en rojo intenso.

No culpes a la nariz. Solo quienes conocen al equipo entre bambalinas sobreviven a la larga primavera.

## Explicación

Una triste pequeña historia de la fiebre del heno: estornudos, rinorrea y congestión nasal. Los fuegos artificiales representan el estornudo, el grifo la rinorrea, los ladrillos el leucotrieno.

> Fuente: clase de farmacología 30:12

voice: DA (fragile-confession style)

## Historia

### El grasiento camino viejo y el tren bala

En un mercado bordeado de puestos de medicamentos, un «grasiento camino viejo»🛢️(antihistamínicos de primera generación) se extendía largo, oliendo a aceite.

El camino viejo cruzó con facilidad el «control cerebral»🚧(barrera hematoencefálica) y nubló hasta la blanca luz del mediodía.

Un viajero se hundió en el «cojín del sueño»🛋️(somnolencia) y cayó profundo, oyendo a lo lejos el viento frío.

Solo una «cantimplora seca»🥤(sequedad de boca) quedó en la boca, y un sabor amargo extendió un lento malestar por la lengua.

El «grifo oxidado»🔩(dificultad para orinar) no giraba en absoluto, y las voces de reproche llenaban la calle.

Elige las horas estables de vigilia antes que la somnolencia barata. El «billete del tren bala»🎫(antihistamínicos de segunda generación) es la verdadera respuesta.

## Explicación

Una historia animada de los antihistamínicos viejos y nuevos. El camino viejo representa la primera generación, el billete la segunda, el cojín la somnolencia.

> Fuente: clase de farmacología 48:52

voice: MA (crowded-street style)
```

</details>

## Inicio rápido (1 minuto)

Elige tu camino. Ambos caminos duran alrededor de un minuto.

### App de Claude (sin terminal)

1. Descarga el paquete: [narrative-formatter.skill](dist/narrative-formatter.skill).
2. Abre la app de Claude. Abre el menú hamburguesa. Ve a Personalizar. Pulsa Añadir.
3. Arrastra y suelta el archivo. Activa la ejecución de código.
4. Pregunta en el chat. Da el material y el modo.

https://github.com/user-attachments/assets/e70f9b9c-9f10-4012-85fe-a42d782cffb6

Mismo vídeo como archivo del repositorio: [install-claude.mp4](docs/assets/install-claude.mp4)

Si la subida falla, descarga el paquete de nuevo. Si no ves ningún elemento de Skills, activa la ejecución de código.

### Agente de programación (terminal)

Primera opción para todos los agentes de programación: Npx. Npx viene con Node.js. Instálalo primero: https://nodejs.org/

```bash
npx skills add Karimuto/tsumugy-narrative
npx skills list
```

## Uso

Crear una historia solo requiere una llamada a la skill. En la app de Claude o en un agente de programación como ClaudeCode, Codex, Pi u OpenCode. Escribe:

```
/narrative-formatter <input file>. mode: <mode (optional)>.
```

Ejemplo, escribiendo junto a la entrada:

```
/narrative-formatter "pharmacology2Lect3.pdf" (or drug and drop some files). mode: serial.
```

Tres modos (por defecto `fable`):

- **episodic**: fiel al texto, una historia autoconclusiva por capítulo.
- **serial**: un protagonista y un mundo continuados a lo largo de los episodios. La memoria se conserva en el ledger.
- **fable** (por defecto): la impresión primero, tolerando cierta imprecisión para que sea memorable.

## Cómo funciona

Seis pasos. Cada paso es sencillo. Un lector de secundaria puede seguirlos.

1. Lee el texto difícil. Encuentra las ideas clave y cómo se conectan.
2. Construye una escena pequeña. Usa personas que hacen cosas y sienten cosas.
3. Envuelve cada palabra difícil en una metáfora. Márcala con corchetes.
4. Da a cada persona y cosa un emoji. Usa el mismo emoji cada vez que aparezca.
5. Escribe el borrador de la Historia: título, cuerpo de la historia, explicación breve, marcador de Fuente.
6. Ejecuta el script de autocomprobación. Lee PASS, CONDITIONAL PASS o FAIL. Corrige lo que señale. Entrega solo trabajo PASS o CONDITIONAL PASS.

Un Thread serial conserva un Ledger. El Ledger guarda el mundo y las personas. Cada nuevo episodio lee primero el Ledger.

## Contribución

Lee [CONTRIBUTING.md](CONTRIBUTING.md) (canónico; [日本語](CONTRIBUTING.ja.md) · [中文](CONTRIBUTING.zh.md)). Los issues y pull requests son bienvenidos en japonés o inglés.

## Licencia

![MIT](https://img.shields.io/badge/license-MIT-green) ![version](https://img.shields.io/badge/version-0.1.0-blue)

MIT ([LICENSE](LICENSE)).
