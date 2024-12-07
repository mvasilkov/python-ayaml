use pyo3::{exceptions::PyValueError, prelude::*};
use pythonize::pythonize;
use serde::ser::{Serialize, SerializeMap, SerializeSeq, Serializer};
use yaml_rust2::{Yaml, YamlLoader};

struct _Yaml<'a>(&'a Yaml);

impl Serialize for _Yaml<'_> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self.0 {
            Yaml::Real(val) => serializer.serialize_f64(val.parse::<f64>().unwrap_or(f64::NAN)),
            Yaml::Integer(val) => serializer.serialize_i64(*val),
            Yaml::String(val) => serializer.serialize_str(val),
            Yaml::Boolean(val) => serializer.serialize_bool(*val),
            Yaml::Array(val) => {
                let mut seq = serializer.serialize_seq(Some(val.len()))?;
                for v in val {
                    seq.serialize_element(&_Yaml(v))?;
                }
                seq.end()
            }
            Yaml::Hash(val) => {
                let mut map = serializer.serialize_map(Some(val.len()))?;
                for (k, v) in val {
                    map.serialize_entry(&_Yaml(k), &_Yaml(v))?;
                }
                map.end()
            }
            Yaml::Alias(_) => serializer.serialize_none(),
            Yaml::Null => serializer.serialize_none(),
            Yaml::BadValue => serializer.serialize_none(),
        }
    }
}

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
