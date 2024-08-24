# Asistente Evaluacion Ambiental para proyectos fotovoltaicos


## Preparacion del ambiente

Crear un ambiente
```bash
conda create -n hackathon python=3.12
pip install poetry


poetry install
```

## Correr streamlit

```bash
streamlit  run  --server.runOnSave true ui/Home.py
```