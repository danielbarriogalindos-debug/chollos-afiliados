# Plan de torneo: The Leap (TradingView), edición julio-agosto 2026

> Todo lo cuantitativo de este documento sale de `sim/contest_sim.py` y
> `sim/orb_backtest.py`, que están en este repositorio y puedes volver a ejecutar.
> Los cortes de premio son **suposiciones** y están marcados como tales.

## 1. El terreno de juego

| Dato | Valor |
|---|---|
| Concurso | The Leap with TradeStation |
| Periodo | 20 jul 2026 08:00 UTC → 14 ago 2026 08:00 UTC |
| Cuenta | 100.000 $ de papel, idéntica para todos, parámetros no modificables |
| Instrumentos | Futuros seleccionados de CME |
| Puntuación | **Solo P/L realizado** durante el periodo |
| Premios | Los **250 primeros** por beneficio; 10.000 $ el primero |
| Requisito | Operar un mínimo de sesiones (5) para cualificar |
| Al cierre | Todas las posiciones abiertas se cierran automáticamente |

**Sesiones que te quedan: 11.** El 14 de agosto el concurso termina a las 08:00 UTC,
es decir, a las 04:00 ET, antes de la apertura regular. La última sesión operable
es el jueves 13 de agosto.

```
julio     30 (jue)  31 (vie)
agosto     3  4  5  6  7      (lun-vie)
agosto    10 11 12 13         (lun-jue)   ← 13 de agosto es el último día
```

## 2. Por qué esto no es "operar bien"

En una cuenta real tu función objetivo es el crecimiento compuesto a largo plazo
penalizado por la ruina, porque la ruina es permanente. Aquí no. Aquí:

- Acabar con 0 $ paga lo mismo que acabar con 99.000 $: **cero**.
- Acabar con 600.000 $ paga muchísimo más que acabar con 130.000 $.

Tu pago es una **opción call sobre tu rentabilidad**, y el valor de una call sube
con la volatilidad. La consecuencia es incómoda pero es matemática: la estrategia
óptima de torneo es asumir mucha más varianza de la que sería sensata con dinero
real. Este documento te dice cuánta, exactamente.

> **No traslades este dimensionamiento a una cuenta real.** Los números que
> siguen implican entre un 5% y un 40% de probabilidad de destruir la cuenta.
> En papel eso es el precio de la entrada; con tu dinero es el final del juego.

## 3. La matemática

### 3.1 Apalancamiento óptimo para un objetivo con fecha límite

Sea `W_t` la equity, `L` el apalancamiento sobre una estrategia con deriva anual
`μ` y volatilidad anual `σ`, y `T` el plazo en años. Con el modelo lognormal
habitual, el log-multiplicador final es normal:

```
X_T = ln(W_T / W_0) ~ N( (Lμ − L²σ²/2)·T ,  L²σ²·T )
```

Queremos maximizar `P(X_T ≥ b)`, donde `b = ln m` y `m` es el múltiplo objetivo.
Con `s = σ√T`, el argumento de la normal estándar es

```
z(L) = (LμT − L²σ²T/2 − b) / (Lσ√T)
     = μ√T/σ  −  L·s/2  −  b/(L·s)
```

Los dos últimos términos son la penalización por apalancarse y la penalización
por quedarse corto. Por la desigualdad AM–GM, `L·s/2 + b/(L·s) ≥ √(2b)`, con
igualdad exacta cuando ambos términos son iguales. De ahí:

```
                 ┌──────────────────────────┐
                 │   L* = √(2 ln m) / (σ√T)  │
                 └──────────────────────────┘

                 P* = Φ( S·√T − √(2 ln m) )        con S = μ/σ (Sharpe)
```

Dos lecturas que cambian cómo se juega esto:

1. **`L*` no depende de `μ`.** Tu ventaja no influye en lo agresivo que te
   conviene ser, solo en la probabilidad que consigues. Si te engañas sobre tu
   Sharpe, seguirás dimensionando bien; solo te equivocarás al estimar tus
   posibilidades. Es una propiedad muy cómoda, porque nadie conoce su Sharpe.
2. **El plazo entra como `1/√T`.** Cada día que pasa sin acercarte al objetivo,
   el apalancamiento óptimo *sube*. Ir por detrás obliga a ser más agresivo, no
   menos. Es lo contrario del instinto de "recuperar poco a poco".

Esto es la versión continua del resultado clásico de Dubins y Savage sobre juego
audaz: cuando el juego no es favorable y hay un objetivo que alcanzar, apostar
fuerte maximiza la probabilidad de llegar; cuando el juego es favorable, conviene
apostar poco (Kelly). Un concurso con 250 premios y decenas de miles de
participantes es, para casi todos, el primer caso.

### 3.2 Kelly no sirve aquí

Kelly (`L = S/σ`, que con Sharpe 1 y vol 20% son 5x) maximiza el crecimiento
esperado del logaritmo. Es la respuesta correcta a una pregunta que no es la
tuya. Con 11 sesiones por delante:

| Objetivo | `L*` óptimo | P* máxima | P con `L`=1x | P con Kelly (5x) |
|---|---|---|---|---|
| 1,50x | 21,6x | 24,5% | 0,00% | 3,3% |
| 2,00x | 28,2x | 16,6% | 0,00% | 0,07% |
| 3,00x | 35,5x | 10,1% | 0,00% | 0,00% |
| 6,00x | 45,3x | 4,6% | 0,00% | 0,00% |
| 11,0x | 52,4x | 2,4% | 0,00% | 0,00% |

*(σ=20%, Sharpe=1, T=11/252. Reproducible con `python3 sim/contest_sim.py --days 11`.)*

Operar "bien" (1x) te da una probabilidad **numéricamente cero** de duplicar en
11 sesiones. Kelly, un 0,07%. Ese es todo el argumento.

### 3.3 Qué significa eso en la práctica

`L* = 28x` no es una instrucción hasta que se traduce a la pantalla de órdenes:

| Objetivo | %/día compuesto | `L*` | Contratos MNQ | Riesgo/operación | Vol diaria de la cuenta |
|---|---|---|---|---|---|
| 1,50x | 3,75% | 21,6x | 43 | 6,5% | 27% |
| 2,00x | 6,50% | 28,2x | 56 | 8,5% | 36% |
| 3,00x | 10,50% | 35,5x | 71 | 10,6% | 45% |
| 6,00x | 17,69% | 45,3x | 91 | 13,6% | 57% |
| 11,0x | 24,36% | 52,4x | 105 | 15,7% | 66% |

*(MNQ a 25.000 = 50.000 $ de nocional por contrato; stop medio del 0,30%.)*

Traducción: apuntar a duplicar significa **56 contratos de MNQ y arriesgar 8.500 $
por operación**, con oscilaciones diarias de la cuenta del 36%. Si eso te parece
demencial, es porque lo es —para dinero real. Para un torneo es simplemente el
precio del billete.

### 3.4 El margen es la restricción que de verdad decide

Con margen `m` por contrato y nocional `n` por contrato, el máximo de contratos
es `equity/m`, luego el nocional máximo es `equity·n/m` y **el tope de
apalancamiento es `n/m`, independiente del tamaño de la cuenta**.

| Instrumento | Nocional/contrato | Margen | Tope | `L*` para 2x | ¿Alcanzable? |
|---|---|---|---|---|---|
| MNQ, margen overnight 2.500 $ | 50.000 $ | 2.500 $ | 20x | 28,2x | **No** |
| MNQ, margen intradía 1.200 $ | 50.000 $ | 1.200 $ | 41,7x | 28,2x | Sí |
| MNQ, margen intradía 500 $ | 50.000 $ | 500 $ | 100x | 28,2x | Sí |
| MBT (micro bitcoin) | 11.000 $ | ~4.000 $ | 2,8x | 8,1x | **No** |

Dos conclusiones que no se ven a ojo:

- **Micro cripto es peor, no mejor.** La volatilidad alta (70% anual) baja el
  `L*` necesario de 28x a 8x, pero el margen de cripto es ~36% del nocional
  frente al ~5% de MNQ, así que el tope se hunde a 2,8x. El hueco entre lo que
  necesitas y lo que puedes se *ensancha*. Micro índices es la elección correcta.
- **Lo primero que tienes que averiguar es el margen intradía de tu cuenta.**
  Es el único parámetro que decide si el óptimo está a tu alcance. Míralo en las
  especificaciones del contrato dentro de la cuenta del concurso y vuelve a
  correr el simulador con `--margin`.

## 4. Qué dice el Monte Carlo

La fórmula ignora la ruina discreta, las colas gruesas y el tope de margen.
`sim/contest_sim.py` los añade. Con 11 sesiones, σ=20%, Sharpe=1, margen intradía
de 1.200 $ y 300.000 recorridos:

| Política | `L` medio | Mediana | Ruina | P(top-250) | P(top-50) | P(top-10) | P(top-3) | E[premio] |
|---|---|---|---|---|---|---|---|---|
| Kelly (5x) | 5,0x | 1,03x | 0,0% | 1,5% | 0,0% | 0,0% | 0,0% | 3 $ |
| estático 10x | 10,0x | 1,02x | 0,3% | 12,4% | 0,4% | 0,0% | 0,0% | 26 $ |
| estático 20x | 20,0x | 0,91x | 5,4% | 24,1% | 6,1% | 0,6% | 0,05% | 75 $ |
| estático 28x | 28,0x | 0,74x | 16,2% | 25,7% | 10,7% | 2,6% | 0,5% | 128 $ |
| estático 45x | 41,7x | 0,33x | 39,7% | 23,7% | 13,8% | 6,2% | 2,5% | 237 $ |
| **adaptativo objetivo 2x** | 26,5x | **1,10x** | 24,3% | **44,6%** | 2,0% | 0,04% | 0,0% | 96 $ |
| adaptativo objetivo 6x | 39,5x | 0,38x | 38,0% | 26,3% | **17,0%** | **10,1%** | 0,2% | 213 $ |
| **adaptativo objetivo 11x** | 41,1x | 0,34x | 39,3% | 24,3% | 14,6% | 7,2% | **3,8%** | **295 $** |

*(Cortes supuestos: top-250 = +60%, top-50 = +200%, top-10 = +500%, top-3 = +1000%.
Ajústalos con `--cut` y `--prize` según lo que veas en la clasificación en vivo.)*

La política adaptativa recalcula `L*` cada día con el hueco y el tiempo que
quedan, y se pone a la defensiva en cuanto supera el objetivo. Gana en casi todo
porque hace lo correcto en cada estado en lugar de una sola apuesta fija.

### La decisión que tienes que tomar

El Monte Carlo no elige por ti, porque hay dos objetivos distintos y son
incompatibles:

- **Quieres cobrar algo con la máxima probabilidad** → adaptativo con objetivo
  **2x**: 44,6% de acabar en premio, mediana 1,10x (o sea, el escenario típico
  ni siquiera pierde dinero). Renuncias casi por completo al top-10.
- **Quieres el premio gordo** → adaptativo con objetivo **11x**: 3,8% de acabar
  en el top-3, el mayor valor esperado (295 $), pero con un 39% de ruina y una
  mediana de 0,34x. Casi siempre acabarás con la cuenta destrozada.

Mi recomendación: **objetivo 2x**. Triplica la probabilidad de premio frente a
apuntar al máximo, y es la única fila de la tabla cuyo escenario mediano no es
una cuenta arrasada. El valor esperado es más bajo, pero está dominado por
sucesos del 0,1% en los que no vas a poder confiar con 11 muestras.

## 5. Plan de ejecución, sesión a sesión

**Antes de la primera sesión (hoy):**
1. Comprueba el **margen intradía** de MNQ en la cuenta del concurso. Vuelve a
   correr `contest_sim.py --margin <valor>` y mira si `L*` está por debajo del tope.
2. Confirma cuántas **sesiones has operado ya**: hacen falta 5 para cualificar.
   Si vas justo, cualificar es prioritario sobre optimizar (un premio al que no
   optas vale cero, por buena que sea la rentabilidad).
3. Carga `pine/leap_orb_mnq.pine` en un gráfico de 5 min de MNQ1!, pon
   `Objetivo de cuenta = 2`, modo `Torneo (L* dinámico)` y fecha de fin del
   concurso. Backtestea ahí antes de mandar una sola orden en vivo.

**Cada sesión:**
1. Apunta el múltiplo de tu cuenta y las sesiones que quedan en
   `pine/leap_risk_panel.pine`. Te da los contratos y el riesgo de hoy.
2. Rango de apertura 09:30–09:45 ET. Órdenes stop a ambos lados del rango.
3. Solo una operación al día, y solo si el rango mide entre 0,15 y 1,20 veces el
   ATR diario. Un rango plano no rompe; un rango ya enorme no tiene recorrido.
4. **Sin entradas nuevas después de las 12:00 ET.** La tarde tiene menos
   continuación y más riesgo de quedarse atrapado.
5. **Todo cerrado antes de las 16:00 ET.** Solo puntúa el P/L realizado.
6. Freno de mano: si pierdes más del 25% de la cuenta en una sesión, cierra el
   día. El objetivo es no llegar al día 11 con cero, porque desde cero no hay
   fórmula que te saque.

**Los últimos tres días (11, 12 y 13 de agosto):**
- Si vas **por encima** de 2x: baja a riesgo de protección (0,5%) y no toques
  nada. Ya has ganado tu apuesta; el ranking solo puede empeorar.
- Si vas **por debajo**: el `L*` de la fórmula sube solo. Déjalo subir. Es el
  único momento en que apostar más fuerte es la decisión matemáticamente
  correcta, precisamente porque queda poco tiempo.
- El 13 de agosto cierra todo antes del cierre. No dejes nada abierto: se
  liquida automáticamente y no controlas a qué precio.

## 6. Los errores que arruinan el intento

1. **Terminar con posiciones abiertas y ganadoras.** No puntúan. Es el error más
   caro y el más fácil de evitar.
2. **No cualificar.** Menos de 5 sesiones operadas y el resto da igual.
3. **Borrar la subcuenta del concurso.** Se borran los resultados.
4. **Confiar en el backtest de papel.** En paper trading las órdenes limitadas se
   ejecutan en cuanto el precio toca el nivel; en un mercado real, con 56
   contratos, ni el precio ni el tamaño son gratis. Aquí eso juega a tu favor
   (es un concurso de papel), pero significa que **estos resultados no se
   trasladan a dinero real**.
5. **Creerte tu Sharpe.** La tabla usa Sharpe 1, que ya es optimista para un ORB
   intradía. Corre `--sharpe 0` y verás que `L*` no cambia: solo cae la
   probabilidad. Eso es información, no consuelo.

## 7. Lo que este plan no puede hacer

No puede garantizarte beneficio, y ninguna herramienta puede. Lo que hace es más
modesto y más honesto: dado que los premios van por ranking, calcula el nivel de
riesgo que maximiza tu probabilidad de entrar en premio, y te dice cuál es esa
probabilidad. **Con los supuestos de la tabla, la mejor política te da ~45% de
cobrar algo y ~4% de entrar en el top-3.** El resultado más probable de cualquier
concurso de trading, para cualquier participante, sigue siendo no ganar nada.

Quien gane The Leap de agosto será, casi con seguridad, alguien que asumió mucha
varianza y tuvo suerte. Este plan te pone en esa distribución de forma
deliberada, en vez de por accidente. Eso es todo lo que se puede hacer, y es más
de lo que hace la mayoría.
