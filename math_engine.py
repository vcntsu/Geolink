"""
math_engine.py — Motor matemático simbólico con SymPy
"""
import sympy as sp
import numpy as np
from dataclasses import dataclass
from typing import Optional

x_sym = sp.Symbol('x', real=True)

_LOCAL_DICT = {
    'x': x_sym,
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'exp': sp.exp, 'log': sp.log, 'ln': sp.log,
    'sqrt': sp.sqrt, 'abs': sp.Abs,
    'pi': sp.pi, 'e': sp.E,
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
}


@dataclass
class DerivativeResult:
    original_expr: str
    derivative_expr: str
    critical_points: list
    latex_original: str
    latex_derivative: str
    steps: list
    slope_value: Optional[float] = None


@dataclass
class IntegralResult:
    original_expr: str
    integral_expr: str
    definite_value: Optional[float]
    latex_original: str
    latex_integral: str
    steps: list
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


def parse_function(func_str: str):
    try:
        expr = sp.sympify(func_str, locals=_LOCAL_DICT)
        return expr, None
    except Exception as e:
        return None, str(e)


def compute_derivative(func_str: str, eval_point: Optional[float] = None) -> DerivativeResult:
    expr, error = parse_function(func_str)
    if error:
        return DerivativeResult(
            original_expr=func_str, derivative_expr="Error",
            critical_points=[], latex_original=func_str,
            latex_derivative=f"\\text{{Error: {error}}}",
            steps=[f"No se pudo parsear: {error}"]
        )

    steps = []
    steps.append(f"Función original: $f(x) = {sp.latex(expr)}$")

    # Reglas aplicadas
    if expr.is_Add:
        steps.append("Regla de la Suma: $\\dfrac{{d}}{{dx}}[f+g] = f' + g'$")
    if expr.is_Mul:
        steps.append("Regla del Producto: $\\dfrac{{d}}{{dx}}[f \\cdot g] = f'g + fg'$")
    if isinstance(expr, sp.Pow):
        steps.append("Regla de la Potencia: $\\dfrac{{d}}{{dx}}[x^n] = n x^{{n-1}}$")
    if expr.has(sp.sin) or expr.has(sp.cos):
        steps.append("Derivada trigonométrica aplicada")
    if expr.has(sp.exp):
        steps.append("Regla exponencial: $\\dfrac{{d}}{{dx}}[e^x] = e^x$")
    if expr.has(sp.log):
        steps.append("Regla logarítmica: $\\dfrac{{d}}{{dx}}[\\ln x] = \\dfrac{{1}}{{x}}$")

    deriv = sp.simplify(sp.diff(expr, x_sym))
    steps.append(f"Derivada: $f'(x) = {sp.latex(deriv)}$")

    # Puntos críticos
    try:
        cpts = sp.solve(deriv, x_sym)
        cpts_real = []
        for pt in cpts:
            try:
                val = complex(pt.evalf())
                if abs(val.imag) < 1e-10:
                    cpts_real.append(round(val.real, 6))
            except Exception:
                pass
        if cpts_real:
            steps.append("Puntos críticos ($f'(x)=0$): " + ", ".join([f"$x={p:.4f}$" for p in cpts_real]))
        else:
            steps.append("No se encontraron puntos críticos reales.")
    except Exception:
        cpts_real = []

    # Evaluar en punto
    slope_val = None
    if eval_point is not None:
        try:
            slope_val = float(deriv.subs(x_sym, eval_point).evalf())
            direction = "creciente" if slope_val > 0 else ("decreciente" if slope_val < 0 else "estacionaria")
            steps.append(f"En $x={eval_point}$: $f'({eval_point}) = {slope_val:.6f}$ → función {direction}")
        except Exception:
            pass

    return DerivativeResult(
        original_expr=func_str, derivative_expr=str(deriv),
        critical_points=cpts_real,
        latex_original=sp.latex(expr), latex_derivative=sp.latex(deriv),
        steps=steps, slope_value=slope_val
    )


def compute_integral(func_str: str, lower: Optional[float] = None,
                     upper: Optional[float] = None) -> IntegralResult:
    expr, error = parse_function(func_str)
    if error:
        return IntegralResult(
            original_expr=func_str, integral_expr="Error",
            definite_value=None, latex_original=func_str,
            latex_integral=f"\\text{{Error: {error}}}",
            steps=[f"No se pudo parsear: {error}"]
        )

    steps = []
    steps.append(f"Función: $f(x) = {sp.latex(expr)}$")

    if lower is not None and upper is not None:
        steps.append(f"Integral definida en $[{lower}, {upper}]$:")
        steps.append(f"$\\displaystyle\\int_{{{lower}}}^{{{upper}}} {sp.latex(expr)}\\, dx$")
    else:
        steps.append(f"Integral indefinida: $\\displaystyle\\int {sp.latex(expr)}\\, dx$")

    # Técnica
    if expr.is_polynomial(x_sym):
        steps.append("Técnica: Regla de la Potencia $\\int x^n dx = \\dfrac{{x^{{n+1}}}}{{n+1}} + C$")
    if expr.has(sp.sin) or expr.has(sp.cos):
        steps.append("Técnica: Integración trigonométrica")
    if expr.has(sp.exp):
        steps.append("Técnica: $\\int e^x dx = e^x + C$")

    # Antiderivada
    try:
        antideriv = sp.simplify(sp.integrate(expr, x_sym))
        steps.append(f"Antiderivada: $F(x) = {sp.latex(antideriv)} + C$")
    except Exception as e:
        antideriv = sp.Symbol('?')
        steps.append(f"No se pudo calcular la antiderivada: {e}")

    # Valor definido
    definite_val = None
    if lower is not None and upper is not None:
        try:
            result = sp.integrate(expr, (x_sym, lower, upper))
            definite_val = float(result.evalf())
            steps.append(f"Teorema Fundamental del Cálculo:")
            steps.append(f"$F({upper}) - F({lower}) = {definite_val:.6f}$")
            sign = "positiva" if definite_val > 0 else ("negativa" if definite_val < 0 else "cero")
            steps.append(f"Área neta: **{definite_val:.4f} u²** ({sign})")
        except Exception as e:
            steps.append(f"No se pudo evaluar la integral definida: {e}")

    return IntegralResult(
        original_expr=func_str, integral_expr=str(antideriv),
        definite_value=definite_val,
        latex_original=sp.latex(expr), latex_integral=sp.latex(antideriv),
        steps=steps, lower_bound=lower, upper_bound=upper
    )


def get_terrain_derivative_analysis(terreno: np.ndarray, x_vals: np.ndarray) -> dict:
    dx = x_vals[1] - x_vals[0]
    d1 = np.gradient(terreno, dx)
    d2 = np.gradient(d1, dx)
    idx_max = int(np.argmax(terreno))
    idx_sp = int(np.argmax(d1))
    idx_sn = int(np.argmin(d1))
    return {
        'primera_deriv': d1,
        'segunda_deriv': d2,
        'x_max_altura': float(x_vals[idx_max]),
        'y_max_altura': float(terreno[idx_max]),
        'x_max_pendiente_pos': float(x_vals[idx_sp]),
        'pendiente_max_pos': float(d1[idx_sp]),
        'x_max_pendiente_neg': float(x_vals[idx_sn]),
        'pendiente_max_neg': float(d1[idx_sn]),
        'pendiente_en_max': float(d1[idx_max]),
    }


def taylor_expansion(func_str: str, point: float = 0, order: int = 4) -> dict:
    expr, error = parse_function(func_str)
    if error:
        return {'error': error, 'steps': [f"Error: {error}"], 'latex': '', 'taylor_expr': '',
                'terms': []}
    steps = []
    steps.append(f"Serie de Taylor de $f(x) = {sp.latex(expr)}$ en $x_0 = {point}$:")
    steps.append(
        f"$f(x) \\approx \\sum_{{n=0}}^{{{order}}} "
        f"\\dfrac{{f^{{(n)}}(x_0)}}{{n!}}(x - x_0)^n$"
    )

    # Compute each term individually for step-by-step display
    terms = []
    try:
        current = expr
        factorial = 1
        for n in range(order + 1):
            if n > 0:
                current = sp.diff(current, x_sym)
                factorial *= n
            coeff = current.subs(x_sym, point)
            coeff_val = sp.simplify(coeff)
            coeff_float = float(coeff_val.evalf())
            if abs(coeff_float) < 1e-12:
                steps.append(
                    f"Término $n={n}$: $\\dfrac{{f^{{({n})}}({point})}}{{{{n!}}}} = "
                    f"\\dfrac{{{sp.latex(coeff_val)}}}{{{factorial}}} = 0$ → omitido"
                )
                continue
            if point == 0:
                term_expr = sp.Rational(coeff_val, factorial) * x_sym**n if n > 0 else coeff_val / factorial
            else:
                term_expr = (coeff_val / factorial) * (x_sym - point)**n
            term_simplified = sp.simplify(term_expr)
            terms.append(term_simplified)
            steps.append(
                f"Término $n={n}$: $\\dfrac{{f^{{({n})}}({point})}}{{{{n!}}}} \\cdot (x-{point})^{{{n}}} = "
                f"\\dfrac{{{sp.latex(coeff_val)}}}{{{factorial}}} \\cdot (x-{point})^{{{n}}} = "
                f"{sp.latex(term_simplified)}$"
            )
    except Exception as e:
        steps.append(f"Error calculando términos: {e}")

    try:
        taylor = sp.series(expr, x_sym, point, order + 1).removeO()
        taylor_simplified = sp.expand(taylor)
        steps.append(f"Suma total: $f(x) \\approx {sp.latex(taylor_simplified)}$")
        return {
            'taylor_expr': str(taylor_simplified),
            'latex': sp.latex(taylor_simplified),
            'steps': steps,
            'terms': [sp.latex(t) for t in terms],
            'error': None
        }
    except Exception as e:
        return {'error': str(e), 'steps': [f"No se pudo calcular: {e}"],
                'latex': '', 'taylor_expr': '', 'terms': []}


def riemann_sum(func_str: str, a: float, b: float, n: int, method: str = 'midpoint') -> dict:
    """
    Compute Riemann sum with left, right, or midpoint method.
    Returns sum value, exact value, error, and step details.
    """
    expr, error = parse_function(func_str)
    if error:
        return {'error': error, 'suma': 0, 'exacto': 0, 'error_pct': 0, 'steps': []}

    try:
        f_lam = sp.lambdify(x_sym, expr, 'numpy')
        dx = (b - a) / n
        x_points = np.linspace(a, b, n + 1)

        if method == 'left':
            eval_pts = x_points[:-1]
            method_label = 'Izquierda'
        elif method == 'right':
            eval_pts = x_points[1:]
            method_label = 'Derecha'
        else:
            eval_pts = x_points[:-1] + dx / 2
            method_label = 'Punto Medio'

        y_vals = np.array([float(f_lam(xi)) for xi in eval_pts])
        suma = float(np.sum(y_vals) * dx)

        exact_result = sp.integrate(expr, (x_sym, a, b))
        exacto = float(exact_result.evalf())
        err_pct = abs(suma - exacto) / max(abs(exacto), 1e-10) * 100

        steps = [
            f"Método: Suma de Riemann — **{method_label}**",
            f"Intervalo $[{a}, {b}]$, $n = {n}$ rectángulos, $\\Delta x = {dx:.4f}$",
            f"$S = \\Delta x \\cdot \\sum_{{i=1}}^{{{n}}} f(x_i^*) = {dx:.4f} \\cdot \\sum f(x_i^*)$",
            f"Suma de Riemann: $S \\approx {suma:.6f}$",
            f"Valor exacto: $\\int_{{{a}}}^{{{b}}} f(x)\\,dx = {exacto:.6f}$",
            f"Error relativo: ${err_pct:.4f}\\%$",
        ]

        return {
            'suma': suma, 'exacto': exacto, 'error_pct': err_pct,
            'steps': steps, 'method': method, 'method_label': method_label,
            'error': None
        }
    except Exception as e:
        return {'error': str(e), 'suma': 0, 'exacto': 0, 'error_pct': 0, 'steps': []}
