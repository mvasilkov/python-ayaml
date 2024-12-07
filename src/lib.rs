use pyo3::{exceptions::PyValueError, prelude::*};
use pythonize::pythonize;
use yaml_rust2::{Yaml, YamlLoader};

struct _Yaml<'a>(&'a Yaml);

fn _loads(s: String) -> Result<Vec<Yaml>, PyErr> {
    match YamlLoader::load_from_str(&s) {
        Ok(val) => Ok(val),
        Err(err) => Err(PyValueError::new_err(err.to_string())),
    }
}

fn _pythonize(py: Python, docs: &Vec<Yaml>) -> PyResult<PyObject> {
    let _docs: Vec<_Yaml> = docs.into_iter().map(_Yaml).collect();

    match pythonize(py, &_docs) {
        Ok(val) => Ok(val.unbind()),
        Err(err) => Err(PyValueError::new_err(err.to_string())),
    }
}

#[pyfunction]
fn loads(s: String) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        let docs: Vec<Yaml> = _loads(s)?;
        let val = _pythonize(py, &docs)?;
        Ok(val)
    })
}

/// A Python module implemented in Rust.
#[pymodule]
fn ayaml(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(loads, m)?)?;
    Ok(())
}
