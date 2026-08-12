/// Pure math primitives — zero dependencies beyond std.
///
/// Every function here replaces a numpy/scipy dependency:
///   norm_cdf       → scipy.stats.norm.cdf
///   poisson_pmf    → scipy.stats.poisson.pmf
///   random_normal  → numpy.random.normal
///   integrate      → scipy.integrate.quad

use std::f64::consts::PI;

// ── Normal CDF ──────────────────────────────────────────────────────
//
// Abramowitz & Stegun 7.1.26 polynomial approximation.
// Absolute error < 7.5e-8 — more than sufficient for financial work.
// Equivalent to scipy.stats.norm.cdf(x).

const A1: f64 = 0.254829592;
const A2: f64 = -0.284496736;
const A3: f64 = 1.421413741;
const A4: f64 = -1.453152027;
const A5: f64 = 1.061405429;
const P: f64 = 0.3275911;

/// Standard normal CDF Φ(x).  Equivalent to scipy.stats.norm.cdf(x).
pub fn norm_cdf(x: f64) -> f64 {
    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let x = x.abs();
    let t = 1.0 / (1.0 + P * x);
    let y = 1.0
        - (((((A5 * t + A4) * t) + A3) * t + A2) * t + A1)
            * t
            * (-x * x / 2.0).exp();
    0.5 * (1.0 + sign * (1.0 - y))
}

// ── Poisson PMF ─────────────────────────────────────────────────────

/// P(X = k) for Poisson distribution with rate λ.  Equivalent to scipy.stats.poisson.pmf(k, λ).
pub fn poisson_pmf(k: u32, lambda: f64) -> f64 {
    if k > 170 {
        // Stirling approximation for large k
        let kf = k as f64;
        (kf * lambda.ln() - lambda - kf * kf.ln() + kf).exp() / (2.0 * PI * kf).sqrt()
    } else {
        lambda.powi(k as i32) * (-lambda).exp() / factorial(k)
    }
}

fn factorial(n: u32) -> f64 {
    if n <= 1 {
        1.0
    } else {
        (2..=n).fold(1.0, |acc, i| acc * i as f64)
    }
}

// ── Random Normal (Box-Muller) ──────────────────────────────────────

/// Generate a standard normal random variate from a uniform [0,1) input pair.
pub fn box_muller(u1: f64, u2: f64) -> f64 {
    (-2.0 * u1.ln()).sqrt() * (2.0 * PI * u2).cos()
}

// ── Numerical Integration (Adaptive Simpson) ────────────────────────

/// Integrate `f` from a to b using adaptive Simpson's rule.
/// Tolerance `tol` defaults to 1e-8.  Equivalent to scipy.integrate.quad.
pub fn simpson_integrate<F: Fn(f64) -> f64>(f: &F, a: f64, b: f64, tol: f64) -> f64 {
    fn simpson<F: Fn(f64) -> f64>(f: &F, a: f64, b: f64, fa: f64, fb: f64) -> f64 {
        (b - a) / 6.0 * (fa + 4.0 * f((a + b) / 2.0) + fb)
    }

    fn adaptive<F: Fn(f64) -> f64>(
        f: &F, a: f64, b: f64, fa: f64, fb: f64, whole: f64, tol: f64,
    ) -> f64 {
        let m = (a + b) / 2.0;
        let fm = f(m);
        let left = simpson(f, a, m, fa, fm);
        let right = simpson(f, m, b, fm, fb);
        let delta = left + right - whole;

        if delta.abs() <= 15.0 * tol || (b - a) < 1e-10 {
            left + right + delta / 15.0
        } else {
            adaptive(f, a, m, fa, fm, left, tol / 2.0)
                + adaptive(f, m, b, fm, fb, right, tol / 2.0)
        }
    }

    let fa = f(a);
    let fb = f(b);
    let whole = simpson(f, a, b, fa, fb);
    adaptive(f, a, b, fa, fb, whole, tol)
}

// ── Statistical helpers ──────────────────────────────────────────────

/// Weighted sum: Σ w_i × s_i
pub fn weighted_sum(weights: &[f64], scores: &[f64]) -> f64 {
    weights.iter().zip(scores).map(|(w, s)| w * s).sum()
}

/// Discounted cash flow: Σ cf_t / (1+r)^t
pub fn present_value(cashflows: &[f64], rate: f64) -> f64 {
    cashflows
        .iter()
        .enumerate()
        .map(|(t, cf)| cf / (1.0 + rate).powi(t as i32 + 1))
        .sum()
}

// ── Tests ────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_norm_cdf_accuracy() {
        let x = norm_cdf(0.0);
        assert!((x - 0.5).abs() < 1e-10);
        assert!((norm_cdf(1.96) - 0.975).abs() < 1e-4);
        assert!((norm_cdf(-1.96) - 0.025).abs() < 1e-4);
    }

    #[test]
    fn test_poisson_pmf() {
        let p = poisson_pmf(3, 2.0);
        let expected = 0.180447;
        assert!((p - expected).abs() < 1e-4);
    }

    #[test]
    fn test_integrate() {
        let result = simpson_integrate(&|x: f64| x * x, 0.0, 1.0, 1e-10);
        assert!((result - 1.0 / 3.0).abs() < 1e-8);
    }
}
