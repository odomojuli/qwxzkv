//! Acceleration kernel for `typosquat`.
//!
//! Every function here mirrors the pure-Python reference in
//! `python/typosquat/_pyref.py` *exactly* (same edit operations, same Optimal
//! String Alignment recurrence, same neighborhood closure). `tests/test_parity.py`
//! asserts agreement whenever this extension is installed. Operate on `Vec<char>`
//! so indexing matches Python's per-codepoint string semantics.

use pyo3::prelude::*;
use std::collections::HashSet;

/// Classic Levenshtein distance.
#[pyfunction]
fn levenshtein(a: &str, b: &str) -> usize {
    let a: Vec<char> = a.chars().collect();
    let b: Vec<char> = b.chars().collect();
    if a == b {
        return 0;
    }
    if a.is_empty() {
        return b.len();
    }
    if b.is_empty() {
        return a.len();
    }
    let mut prev: Vec<usize> = (0..=b.len()).collect();
    for (i, &ca) in a.iter().enumerate() {
        let mut cur = vec![i + 1];
        for (j, &cb) in b.iter().enumerate() {
            let cost = if ca == cb { 0 } else { 1 };
            let v = (prev[j + 1] + 1).min(cur[j] + 1).min(prev[j] + cost);
            cur.push(v);
        }
        prev = cur;
    }
    *prev.last().unwrap()
}

/// Damerau-Levenshtein, Optimal String Alignment variant (adjacent transposition).
#[pyfunction]
fn damerau_levenshtein(a: &str, b: &str) -> usize {
    let a: Vec<char> = a.chars().collect();
    let b: Vec<char> = b.chars().collect();
    let (la, lb) = (a.len(), b.len());
    if la == 0 {
        return lb;
    }
    if lb == 0 {
        return la;
    }
    let mut d = vec![vec![0usize; lb + 1]; la + 1];
    for (i, row) in d.iter_mut().enumerate() {
        row[0] = i;
    }
    for j in 0..=lb {
        d[0][j] = j;
    }
    for i in 1..=la {
        for j in 1..=lb {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            let mut v = (d[i - 1][j] + 1)
                .min(d[i][j - 1] + 1)
                .min(d[i - 1][j - 1] + cost);
            if i > 1 && j > 1 && a[i - 1] == b[j - 2] && a[i - 2] == b[j - 1] {
                v = v.min(d[i - 2][j - 2] + 1);
            }
            d[i][j] = v;
        }
    }
    d[la][lb]
}

/// All strings exactly one edit from `s` (delete / adjacent-transpose /
/// substitute / insert over `alphabet`). Mirrors `_pyref.one_edits`.
fn one_edits(s: &[char], alphabet: &[char], out: &mut HashSet<String>) {
    let n = s.len();
    // deletions
    for i in 0..n {
        let mut t: Vec<char> = Vec::with_capacity(n.saturating_sub(1));
        t.extend_from_slice(&s[..i]);
        t.extend_from_slice(&s[i + 1..]);
        out.insert(t.into_iter().collect());
    }
    // adjacent transpositions (only when the two chars differ)
    if n >= 2 {
        for i in 0..n - 1 {
            if s[i] != s[i + 1] {
                let mut t = s.to_vec();
                t.swap(i, i + 1);
                out.insert(t.into_iter().collect());
            }
        }
    }
    // substitutions
    for i in 0..n {
        for &c in alphabet {
            if c != s[i] {
                let mut t = s.to_vec();
                t[i] = c;
                out.insert(t.into_iter().collect());
            }
        }
    }
    // insertions
    for i in 0..=n {
        for &c in alphabet {
            let mut t: Vec<char> = Vec::with_capacity(n + 1);
            t.extend_from_slice(&s[..i]);
            t.push(c);
            t.extend_from_slice(&s[i..]);
            out.insert(t.into_iter().collect());
        }
    }
}

/// BFS closure of `one_edits` to radius `k`. Mirrors `_pyref.edit_neighborhood`.
#[pyfunction]
fn edit_neighborhood(name: &str, k: usize, alphabet: &str) -> Vec<String> {
    let mut seen_alpha: HashSet<char> = HashSet::new();
    let alpha: Vec<char> = alphabet.chars().filter(|c| seen_alpha.insert(*c)).collect();

    let name_s = name.to_string();
    let mut seen: HashSet<String> = HashSet::new();
    seen.insert(name_s.clone());
    let mut frontier: HashSet<String> = HashSet::new();
    frontier.insert(name_s.clone());

    for _ in 0..k {
        let mut next: HashSet<String> = HashSet::new();
        for s in &frontier {
            let sc: Vec<char> = s.chars().collect();
            let mut edits: HashSet<String> = HashSet::new();
            one_edits(&sc, &alpha, &mut edits);
            for e in edits {
                if !seen.contains(&e) {
                    seen.insert(e.clone());
                    next.insert(e);
                }
            }
        }
        frontier = next;
        if frontier.is_empty() {
            break;
        }
    }
    seen.remove(&name_s);
    seen.into_iter().collect()
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(levenshtein, m)?)?;
    m.add_function(wrap_pyfunction!(damerau_levenshtein, m)?)?;
    m.add_function(wrap_pyfunction!(edit_neighborhood, m)?)?;
    Ok(())
}
