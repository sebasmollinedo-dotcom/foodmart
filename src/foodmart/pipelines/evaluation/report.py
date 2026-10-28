"""Reporte HTML interactivo (tema supermercado) con todo el proyecto, generado por ``kedro run``."""
import json
import math
from html import escape

import pandas as pd

from .icons import icon
from .report_assets import CSS, JS


def _p(p: float | None) -> str:
    """Formatea un p-valor."""
    if p is None:
        return "n/d"
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def _aisle(anchor: str, num: int, title: str, ic: str, body: str) -> str:
    return (f'<section class="aisle reveal" id="{anchor}"><div class="sign"><span class="n">Pasillo {num}</span>'
            f'<h2>{icon(ic, 28)}{title}</h2></div><div class="shelf">{body}</div></section>')


def _chapin(text: str) -> str:
    return (f'<div class="chapin">{icon("lightbulb", 22)}<div><b class="l">Dicho en chapín</b>{text}</div></div>')


def _acc(ic: str, title: str, body: str, opened: bool = False) -> str:
    return (f'<details class="acc"{" open" if opened else ""}><summary>{icon(ic, 20)}{title}</summary>'
            f'<div class="bd">{body}</div></details>')


def _bars(rows: list[tuple[str, float, str, str]], peak: float) -> str:
    """Barras horizontales animadas: (etiqueta, valor, clase, tooltip)."""
    return "".join(
        f'<div class="bar {cls}" data-tip="{escape(tip)}"><span>{escape(lab)}</span>'
        f'<div class="tr"><i style="--w:{max(abs(v), 0) / peak * 100:.0f}%"></i></div><span>{v:+.2f}</span></div>'
        for lab, v, cls, tip in rows
    )


def _corr_bars(corr: list[dict]) -> str:
    if not corr:
        return ""
    peak = max(abs(c["r"]) for c in corr)
    rows = [(c["variable"], c["r"], "ns" if c["p"] >= 0.05 else ("neg" if c["r"] < 0 else ""),
             f"p = {_p(c['p'])}" + (" · no distinguible de cero" if c["p"] >= 0.05 else ""))
            for c in sorted(corr, key=lambda d: -abs(d["r"]))]
    return _bars(rows, peak)


def _importance_bars(imp: pd.DataFrame, n: int = 6) -> str:
    top = imp.head(n)
    peak = max(float(top["caida_r2"].max()), 1e-9)
    return "".join(
        f'<div class="bar{"" if v >= 0.02 * peak else " ns"}" data-tip="Caída del R² al desordenar esta variable">'
        f'<span>{escape(str(k))}</span><div class="tr"><i style="--w:{max(v, 0) / peak * 100:.0f}%"></i></div>'
        f"<span>{v:.3f}</span></div>"
        for k, v in zip(top["variable"], top["caida_r2"])
    )


def _classification_table(cls: pd.DataFrame, final: str) -> str:
    rows = "".join(
        f'<tr class="{"final" if r.modelo == final else ""}"><td>{escape(r.modelo)}</td>'
        f"<td>{r.accuracy:.2f}</td><td>{r.precision:.2f}</td><td>{r.recall:.2f}</td><td>{r.F1:.2f}</td></tr>"
        for r in cls.itertuples())
    return ('<div class="tw"><table><tr><th>Modelo</th><th>Exactitud</th><th>Precisión</th><th>Recall</th><th>F1</th></tr>'
            f"{rows}</table></div>")


def _confusion(cm: pd.DataFrame) -> str:
    low, high = cm.iloc[0], cm.iloc[1]

    def cell(cls: str, n: int, label: str, info: str) -> str:
        return (f'<div class="c {cls}" tabindex="0" data-info="{escape(info)}">'
                f'<span class="n">{int(n)}</span>{label}</div>')

    return (
        '<div class="cm"><div></div><div class="h">Predicho: baja</div><div class="h">Predicho: alta</div>'
        '<div class="h">Real: baja</div>'
        + cell("ok", low.pred_baja, "acierto",
               "Tiendas de baja utilidad que el modelo también marcó como baja. ¡Cabal! Se evitó abrir una tienda que no iba a dejar pisto.")
        + cell("bad", low.pred_alta, "falso positivo",
               "Falso positivo: el modelo dijo «esto va a dar buen pisto» y la tienda resultó de baja utilidad. Es el error más caro: abrir una tienda que no rinde.")
        + '<div class="h">Real: alta</div>'
        + cell("bad", high.pred_baja, "falso negativo",
               "Falso negativo: el modelo descartó una ubicación que sí era buena. Se pierde la oportunidad, pero no se pierde plata.")
        + cell("ok", high.pred_alta, "acierto",
               "Tiendas de alta utilidad bien detectadas. ¡Chilero! Aquí el modelo acertó.")
        + "</div>"
    )


def _kpis(comp: dict, f1: float, thr: float) -> str:
    items = [
        (f"{comp['corr']:.2f}", f"{comp['corr']:.2f}", 2, "", "", "correlación entre competidores y utilidad"),
        (f"{comp['r2'] * 100:.0f}%", f"{comp['r2'] * 100:.0f}", 0, "", "%", "de la variación de la utilidad la explica solo el número de competidores"),
        (f"−${abs(comp['slope']) * 1000:.0f} mil", f"{abs(comp['slope']) * 1000:.0f}", 0, "−$", " mil", "de utilidad se lleva cada competidor adicional"),
        (f"{f1:.2f}", f"{f1:.2f}", 2, "", "", f"F1 al detectar tiendas de alta utilidad (≥ ${thr:g}M)"),
    ]
    return '<div class="tags">' + "".join(
        f'<div class="ptag"><b data-count="{v}" data-dec="{d}" data-pre="{pre}" data-suf="{suf}">{shown}</b><span>{txt}</span></div>'
        for shown, v, d, pre, suf, txt in items) + "</div>"


def _calculator(thr: float, n: int) -> str:
    return f"""<div class="sim">
<div><label for="sim"><b>¿Cuántos competidores tienes cerca?</b></label>
<input id="sim" type="range" min="0" max="7" value="2" step="1">
<div class="rack" id="sim-rack" aria-hidden="true"></div>
<p class="note" id="sim-real"></p></div>
<div aria-live="polite"><div class="note">Con <b id="sim-n">2</b> competidores, la recta de las {n} tiendas espera</div>
<div class="big" id="sim-u">$0 mil</div>
<div class="meter"><i id="sim-m"></i><u id="sim-thr" data-tip="Umbral de alta utilidad: ${thr:g}M"></u></div>
<span class="verdict" id="sim-v">{icon("shopping-cart", 18)}<span></span></span>
<p class="note">La raya vertical marca el umbral de «alta utilidad» (${thr:g}M).</p></div></div>"""


def _problem() -> str:
    cards = [
        ("store", "Contexto", "FOODmart es una cadena de supermercados; el Head Office decide dónde abrir y cómo operar las tiendas."),
        ("users", "Stakeholder", "Dirección de operaciones y expansión."),
        ("search", "Pregunta", "¿Qué factores operativos y de ubicación explican la utilidad bruta de una tienda, y se puede predecirla?"),
        ("target", "Objetivo analítico", "Regresión: predecir la utilidad bruta ($ millones). Vista extra de clasificación: ¿alta o baja utilidad?"),
        ("chart-column", "Métrica de éxito", "MAE, RMSE y R² en datos de prueba, superando a la línea base (predecir la media)."),
        ("badge-dollar-sign", "Impacto", "Priorizar ubicaciones y decisiones (horario, publicidad) que aumenten la utilidad."),
    ]
    html = "".join(f'<div class="mini">{icon(i, 26)}<b>{t}</b><span>{d}</span></div>' for i, t, d in cards)
    return (f'<div class="cards4">{html}</div><div class="find warn">Decisión clave: <b>no</b> se usan ventas ni salarios '
            "como predictores, porque son resultados del negocio y no decisiones que la gerencia pueda tomar.</div>")


def _process(eda: dict, params: dict) -> str:
    q, sp = eda["quality"], eda["split"]
    combos = math.prod(len(v) for v in params["rf_param_grid"].values())
    steps = [
        ("database", "Datos", f"{q['rows']} tiendas × {q['columns']} columnas (Excel de Kaggle)."),
        ("sparkles", "Limpieza", "Nombres en snake_case, sin duplicados ni filas sin objetivo, outliers recortados con IQR."),
        ("layers", "Variables", "Se crea <code>basket_growth_pct</code>; se excluyen ventas, salarios e ID."),
        ("percent", "Partición", f"{sp['train']} tiendas para entrenar y {sp['test']} para probar (80/20, semilla {params['random_state']})."),
        ("scale", "Modelos", f"Línea base, regresión simple, Ridge y Random Forest ({combos} combinaciones × {params['cv_folds']} folds)."),
        ("target", "Evaluación", "MAE, RMSE y R²; F1 y matriz de confusión; importancia por permutación."),
        ("receipt", "Reporte", "Esta página, generada por <code>kedro run</code>."),
    ]
    flow = "".join(f'<div class="step"><i>{n}</i><b>{icon(i, 18)}{t}</b>{d}</div>'
                   for n, (i, t, d) in enumerate(steps, 1))
    return (f'<div class="flow">{flow}</div><p class="note">Todo es reproducible: un solo comando (<code>kedro run</code>) '
            "ejecuta los tres pipelines (<code>data_processing</code> → <code>training</code> → <code>evaluation</code>) y cada "
            "push se valida con pruebas y Ruff en GitHub Actions.</p>")


def _eda(eda: dict, params: dict) -> str:
    q, comp, bk, cv = eda["quality"], eda["competitors"], eda["baskets"], eda["cv"]
    pct = q["outliers"] / q["outlier_cells"]
    top = ", ".join(f"<code>{escape(k)}</code> ({n})" for k, n in q["outliers_top"].items())
    strong = [c for c in eda["correlations"] if c["p"] < 0.05 and abs(c["r"]) >= 0.5]
    strong_txt = ", ".join(f"<code>{escape(c['variable'])}</code> {c['r']:+.2f}" for c in strong)
    k = params["outlier_iqr_factor"]
    complete = ("el dataset viene completo, pero es <b>pequeño</b>, así que conviene preferir modelos simples."
                if q["missing"] == 0 and q["duplicates"] == 0
                else "se limpiaron antes de entrenar; además el dataset es <b>pequeño</b>, así que conviene preferir modelos simples.")
    out = [_chapin("Los números no mienten: de todas las variables, solo dos se mueven fuerte con la utilidad "
                   "(competidores y horas), y las horas resultan ser puro reflejo de la competencia.")]

    out.append(_acc("database", "Calidad de los datos y outliers", f"""
<div class="find"><b>{q['missing']} faltantes y {q['duplicates']} duplicados</b> en {q['rows']} tiendas: {complete}
El código de limpieza maneja ambos casos, por si llegan datos nuevos.</div>
<div class="find"><b>Outliers: {q['outliers']} valores de {q['outlier_cells']} ({pct:.1%})</b> según la regla del IQR
(fuera de [Q1 − {k}·IQR, Q3 + {k}·IQR]); los más frecuentes: {top or 'ninguno'}. Son pocos y plausibles, entonces se
<b>recortan al límite</b> en vez de botar tiendas.</div>""", True))

    out.append(_acc("chart-column", "¿Qué se relaciona con la utilidad?", f"""
<p class="note">Correlación de Pearson con la utilidad bruta (pasa el mouse para ver el p-valor). En gris: no distinguible de cero.</p>
{_corr_bars(eda["correlations"])}
<div class="find"><b>{len(strong)} variable{'s' if len(strong) != 1 else ''} con relación fuerte</b>
({strong_txt or 'ninguna'}). Las demás son débiles o indistinguibles de cero.</div>""", True))

    out.append(_acc("users", "La competencia lo explica casi todo", f"""
<label class="chk"><input type="checkbox" id="c-pts" checked> Tiendas</label>
<label class="chk"><input type="checkbox" id="c-avg" checked> Promedio por grupo</label>
<label class="chk"><input type="checkbox" id="c-mod" checked> Recta del modelo</label>
<div id="sc"></div>
<p class="note">Cada punto es una tienda (pasa el mouse). Línea negra: promedio por número de competidores; línea roja punteada: el modelo.</p>
<div class="find"><b>Cada competidor adicional resta ≈ ${abs(comp['slope']) * 1000:.0f} mil</b>
(utilidad ≈ {comp['intercept']:.2f} − {abs(comp['slope']):.3f} × competidores) y esa sola variable explica el <b>{comp['r2']:.0%}</b> de la variación.</div>""", True))

    out.append(_acc("clock", "Las horas de operación no son la vara", f"""
<div class="stats3"><div class="s"><b>{comp['corr_hours_competitors']:.2f}</b><span class="note">correlación horas ↔ competidores</span></div>
<span class="arrow">{icon('arrow-right', 22)}</span>
<div class="s"><b>{comp['corr_hours_profit']:+.2f}</b><span class="note">horas ↔ utilidad (aparente)</span></div>
<span class="arrow">{icon('arrow-right', 22)}</span>
<div class="s"><b>{comp['corr_hours_profit_adjusted']:+.2f}</b><span class="note">horas ↔ utilidad sin el efecto de la competencia</span></div></div>
{_chapin("Abrir más horas no es la vara. Las tiendas con mucha competencia abren más tiempo para defenderse, pero eso no les trae más pisto.")}"""))

    reales = [c["variable"] for c in eda["categoricals"] if c["p"] is not None and c["p"] < 0.05]
    cat_txt = ("Con p &lt; 0.05 solo se detecta diferencia en: " + ", ".join(f"<code>{escape(v)}</code>" for v in reales) + "."
               if reales else "Ninguna variable categórica muestra diferencias detectables.")
    rows = ""
    for c in eda["categoricals"]:
        real = c["p"] is not None and c["p"] < 0.05
        rows += (f'<tr><td>{escape(c["variable"])}</td><td>{c["groups"]}</td><td>{c["min_group"]}</td><td>{_p(c["p"])}</td>'
                 f'<td><span class="tag {"yes" if real else ""}">{"diferencia real" if real else "no detectable"}</span></td></tr>')
    out.append(_acc("tag", "Variables categóricas", f"""
<p class="note">Prueba de Kruskal-Wallis: ¿la utilidad cambia entre grupos? {cat_txt}</p>
<div class="tw"><table><tr><th>Variable</th><th>Grupos</th><th>Grupo menor</th><th>p-valor</th><th></th></tr>{rows}</table></div>"""))

    sex = eda["manager_sex"]
    if sex:
        cs = sex["competitors_by_sex"]
        out.append(_acc("triangle-alert", "El sexo del gerente: un espejismo", f"""
<div class="find warn">En bruto, las tiendas con gerente mujer ({sex['female_stores']} tiendas) rinden {sex['raw_effect']:+.2f}
(t = {sex['raw_t']:.1f}), pero enfrentan más competidores ({cs.get('Female', float('nan')):.2f} contra {cs.get('Male', float('nan')):.2f}).
Controlando por competidores el efecto baja a {sex['adj_effect']:+.2f} (t = {sex['adj_t']:.1f}) y deja de ser significativo.</div>
{_chapin("Ojo con esto: parece que a las tiendas con gerente mujer les va peor, pero es puro cuento de la competencia, no de ellas. No sirve para decidir quién dirige una tienda.")}"""))

    vif = ", ".join(f"<code>{escape(v['variable'])}</code> {v['vif']:.0f}" for v in eda["vif"])
    out.append(_acc("shopping-basket", "Canastas de precios y colinealidad", f"""
<div class="find">Las canastas 2013 y 2014 son casi la misma variable (correlación {bk['corr_2013_2014']:.3f}; el precio sube entre
{bk['growth_min']:.1f} % y {bk['growth_max']:.1f} %, ≈ {bk['growth_mean']:.1f} % en promedio). VIF más altos (&gt; 10 = colinealidad fuerte): {vif}.
Por eso conviene un modelo simple o regularizado.</div>
<div class="find">Ventas y salarios casi no se relacionan con la utilidad y van pegados entre sí: son resultados del tamaño de la tienda,
no decisiones, y por eso quedan fuera.</div>"""))

    out.append(_acc("scale", "¿Cuánto aportan las demás variables?", f"""
<div class="find">Con validación cruzada ({cv['splits']} particiones), la regresión con <b>solo competidores</b> logra un R² de
<b>{cv['r2_simple']:.2f}</b> frente a <b>{cv['r2_ridge']:.2f}</b> del Ridge con todas las variables, y gana en
<b>{cv['simple_wins']:.0%}</b> de las particiones. Las demás variables no aportan señal medible con solo {q['rows']} tiendas.</div>
<p class="note">Ojo: el modelo simple se eligió después de ver estos mismos datos, así que la ventaja es orientativa y no una prueba definitiva.</p>
<p class="note">EDA completo, con todos los gráficos: <code>notebooks/eda.html</code>.</p>"""))
    return "".join(out)


def _models(eda: dict, final: str, params: dict) -> str:
    combos = math.prod(len(v) for v in params["rf_param_grid"].values())
    test = eda["split"]["test"]
    cards = [
        ("package", "baseline_media", "Predice siempre la media de la utilidad: el piso que cualquier modelo debe superar."),
        ("trending-down", "regresion_simple", "Una recta de la utilidad contra el número de competidores. Fácil de explicar y sin sobreajuste."),
        ("layers", "ridge", "Regresión lineal con todas las variables estandarizadas y penalización (alpha = 1); ayuda con la colinealidad."),
        ("workflow", "random_forest", f"Conjunto de árboles; hiperparámetros elegidos con GridSearchCV ({combos} combinaciones × {params['cv_folds']} folds)."),
    ]
    html = "".join(f'<div class="mini">{icon(i, 26)}<b>{t}{" ★" if t == final else ""}</b><span>{d}</span></div>' for i, t, d in cards)
    return f"""<div class="cards4">{html}</div>
<h3>{icon("chart-column", 20)}Resultados sobre las {test} tiendas de prueba</h3>
<div class="seg" id="mseg"><button class="on" data-m="MAE">MAE</button><button data-m="RMSE">RMSE</button><button data-m="R2">R²</button></div>
<p class="note" id="mnote"></p><div id="mbars"></div>
<div class="find warn"><b>Cómo leerlo.</b> Con solo {test} tiendas de prueba el resultado depende de cuáles caen ahí y los modelos quedan
parejos. Con validación cruzada (Pasillo 3) el modelo simple rinde igual o mejor; por eso el modelo final es <b>{escape(final)}</b>.</div>
{_chapin("Para qué complicarse: una recta con una sola variable rinde igual o mejor que los modelos sofisticados. Con solo 150 tiendas, lo simple es lo chilero.")}"""


def _classification(cls: pd.DataFrame, cm: pd.DataFrame, final: str, thr: float) -> str:
    n = int(cm[["pred_baja", "pred_alta"]].to_numpy().sum())
    acc = float(cls.loc[cls["modelo"] == final, "accuracy"].iloc[0])
    return f"""<p class="note">Vista complementaria: la predicción se convierte en «alta» (utilidad ≥ ${thr:g}M) o «baja». Se calcula con
predicciones fuera de muestra (validación cruzada de 5 folds sobre las {n} tiendas): cada tienda se evalúa con un modelo que no la vio al entrenar.</p>
<div class="grid2"><div><h3>{icon("target", 20)}Matriz de confusión ({escape(final)})</h3>{_confusion(cm)}
<div id="cm-info">Pasa el mouse o toca un cuadro para ver qué significa.</div></div>
<div><h3>{icon("calculator", 20)}Métricas de clasificación</h3>{_classification_table(cls, final)}
<p class="note"><b>F1</b> equilibra precisión (de las que dije «alta», ¿cuántas lo eran?) y recall (de las altas reales, ¿cuántas detecté?).</p></div></div>
<p class="note">Nota: el Random Forest usa hiperparámetros elegidos con el conjunto de entrenamiento, así que su cifra puede ser algo optimista.</p>
{_chapin(f"De cada 100 tiendas, el modelo acierta en {acc * 100:.0f} si va a dar buen pisto o no. No es una bola de cristal, pero para comparar ubicaciones sirve y bastante.")}"""


def _ticket(slope: float, mae: float, n: int) -> str:
    def line(txt: str, val: str) -> str:
        return f'<div class="t-l"><b>{txt}</b><span class="dots"></span><span>{val}</span></div>'

    return f"""<div class="ticket"><div class="t-h">★ TICKET DE RECOMENDACIONES ★</div><div class="t-sep"></div>
{line("1× Revisar la competencia antes de abrir", f"−${abs(slope) * 1000:.0f} mil c/u")}
{line("1× Usar el modelo como filtro, no como oráculo", f"±${mae * 1000:.0f} mil")}
{line("1× Probar con un piloto antes de mover horarios o publicidad", "gratis")}
{line("1× Juntar más datos (más tiendas, más años, tráfico)", "inversión")}
<div class="t-sep"></div><div class="t-tot"><span>TOTAL: la competencia manda</span><span>{n} tiendas</span></div>
<div class="barcode"></div></div>"""


def build_report(
    stores: pd.DataFrame,
    eda: dict,
    metrics: pd.DataFrame,
    importance: pd.DataFrame,
    cls: pd.DataFrame,
    cm: pd.DataFrame,
    params: dict,
) -> str:
    """Arma el reporte HTML interactivo a partir de los resultados del pipeline.

    Args:
        stores: Tabla limpia de tiendas.
        eda: Resumen del EDA calculado por ``summarize_eda``.
        metrics: Métricas de regresión en prueba.
        importance: Importancia de variables del modelo final.
        cls: Métricas de clasificación (alta vs baja utilidad).
        cm: Matriz de confusión del modelo final.
        params: Parámetros del proyecto.

    Returns:
        str: Documento HTML completo y autocontenido (sin recursos externos).

    """
    final, thr = params["final_model"], params["profitable_threshold"]
    comp = eda["competitors"]
    f1 = float(cls.loc[cls["modelo"] == final, "F1"].iloc[0])
    mae = float(metrics.loc[metrics["modelo"] == final, "MAE"].iloc[0])
    slope, n = comp["slope"], len(stores)

    data = {
        "thr": thr, "final": final,
        "comp": {"intercept": comp["intercept"], "slope": slope, "groups": comp["groups"], "points": comp["points"]},
        "metrics": metrics.to_dict("records"),
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    nav = "".join(f'<a href="#{a}">{icon(i, 15)}{t}</a>' for a, i, t in [
        ("calculadora", "calculator", "Calculadora"), ("problema", "search", "Problema"), ("proceso", "workflow", "Proceso"),
        ("eda", "chart-column", "EDA"), ("modelos", "scale", "Modelos"), ("clasificacion", "target", "F1"),
        ("variables", "tag", "Variables"), ("recomendaciones", "receipt", "Ticket")])

    imp_note = ('<p class="note">El resto de variables no aporta: el modelo final solo usa los competidores.</p>'
                if final == "regresion_simple" else "")
    aisles = "".join([
        _aisle("calculadora", 0, "La calculadora del Head Office", "calculator",
               _calculator(thr, n) + _chapin(
                   f"Lo que más le pega al pisto de una tienda es la competencia. Entre más supermercados rivales tiene cerca, menos gana, "
                   f"así de claro: cada competidor extra se lleva como ${abs(slope) * 1000:.0f} mil. Mueve la palanca y míralo tú mismo.")),
        _aisle("problema", 1, "El problema de negocio", "search", _problem()),
        _aisle("proceso", 2, "El proceso, de la bodega al reporte", "workflow", _process(eda, params)),
        _aisle("eda", 3, "Lo que dicen los datos (EDA)", "chart-column", _eda(eda, params)),
        _aisle("modelos", 4, "Los modelos", "scale", _models(eda, final, params)),
        _aisle("clasificacion", 5, "¿Esta tienda dará buen pisto? (F1)", "target", _classification(cls, cm, final, thr)),
        _aisle("variables", 6, "Las variables que sí cuentan", "tag",
               '<p class="note">Caída del R² al desordenar cada variable en el modelo final (importancia por permutación).</p>'
               f'{_importance_bars(importance)}{imp_note}'),
        _aisle("recomendaciones", 7, "Caja: recomendaciones finales", "receipt", f"""{_ticket(slope, mae, n)}
<div class="grid2"><div><h3>{icon("circle-x", 20)}Qué no hacer</h3><ul class="no">
<li>{icon("circle-x", 18)}<span>No alargar horarios esperando más utilidad: solo reflejan la competencia.</span></li>
<li>{icon("circle-x", 18)}<span>No decidir por el sexo del gerente: el efecto aparente es la competencia.</span></li>
<li>{icon("circle-x", 18)}<span>No guiarse por ventas o salarios: son resultados, no palancas.</span></li></ul></div>
<div><h3>{icon("triangle-alert", 20)}Limitaciones</h3><ul>
<li>Solo {n} tiendas y un año: resultados con mucha varianza.</li>
<li>Fuera de muestra el modelo explica cerca del {eda['cv']['r2_simple']:.0%} de la variación: queda mucho sin explicar.</li>
<li>Datos ficticios; correlación no implica causalidad.</li></ul></div></div>
{_chapin(f"Tómese con pinzas: son {n} tiendas de un solo año y datos de mentira (ficticios). Úselo para comparar ubicaciones, no como palabra santa.")}"""),
    ])

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FoodMart – Utilidad bruta</title>
<link rel="icon" href="data:,">
<script>try{{var t=localStorage.getItem('fm-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');document.documentElement.dataset.theme=t}}catch(e){{}}document.documentElement.classList.add('js')</script>
<style>{CSS}</style></head>
<body>
<div id="prog"><i></i></div><div id="cart">{icon("shopping-cart", 22)}</div>
<header class="hero"><div class="awning"></div><div class="hero-in">
<div class="brand">{icon("store", 20)}Súper FoodMart</div>
<h1>¿Qué decide cuánto <em>pisto</em> deja una tienda?</h1>
<p class="sub">Machine Learning for Business · CRISP-DM + Kedro · {n} tiendas · modelo final: <b>{escape(final)}</b></p>
{_kpis(comp, f1, thr)}
</div></header>
<nav aria-label="Pasillos">{nav}<span class="sp"></span><button id="theme" type="button" aria-label="Cambiar tema">{icon("sun", 16)}{icon("moon", 16)}</button></nav>
<main>{aisles}</main>
<footer>{icon("shopping-basket", 20)}<br>¡Gracias por su visita! Todo lo de arriba sale de un solo comando:
<br><span class="pill">{icon("play", 15)}<code>kedro run</code></span><br>Proyecto 1 · Machine Learning for Business</footer>
<div class="tip" id="tip"></div>
<template id="tpl-store">{icon("store", 26)}</template>
<script id="data" type="application/json">{payload}</script>
<script>{JS}</script>
</body></html>
"""
