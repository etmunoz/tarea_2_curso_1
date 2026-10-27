# tarea_2_curso_1

Proyecto Python administrado con [uv](https://docs.astral.sh/uv/).

## Preparación

Instalar `uv` en Windows (PowerShell), si no está disponible:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Instalar Python y crear el entorno virtual con las dependencias fijadas:

```powershell
uv python install
uv sync --locked
```

El archivo `.python-version` fija la versión de Python. El entorno local
se encuentra en `.venv` y no se incluye en Git.

## Uso

```powershell
uv run python --version
```

No es necesario activar el entorno para ejecutar comandos con `uv run`.

## Sincronización con GitHub

Antes de trabajar:

```powershell
git pull --ff-only
```

Para guardar y subir los cambios, revisarlos primero con `git diff`:

```powershell
git status
git diff
git add .
git commit -m "Describe los cambios realizados"
git push
```
