# Fast‑Start Python Project Recipe 📄

Use this checklist **once per new repo** to avoid the Black ↔ isort loop and “imports‑at‑top” errors forever.

---

## 1 · Add a single *pyproject.toml*

```toml
[tool.black]
line-length = 88

[tool.isort]
profile      = "black"   # makes isort generate Black‑compatible imports
line_length  = 88
```

*Why?*  Using the “black” profile keeps isort & Black in sync—no more endless re‑formatting.

---

## 2 · Install & activate pre‑commit hooks

```bash
pip install pre-commit
pre-commit install          # one‑time per repo
```

### Daily workflow

```bash
pre-commit run --all-files  # format before staging
git add .
git commit -m "feat: …"
```

(optional alias)
```bash
git config --global alias.pc "!pre-commit run --all-files"
```

---

## 3 · Keep scripts **inside** the package

```
myproject/
│
└─ app/
   ├─ __init__.py
   ├─ orchestrator.py
   └─ agents/…
```

Run scripts with:

```bash
python -m app.orchestrator
```

→ No `sys.path` hacks, no E402 warnings.

---

## 4 · Skip hooks only when truly necessary

```bash
git commit -m "wip: scratch" --no-verify
```

---

## 5 · One‑line push that always sets upstream

```bash
git config --global alias.pushup "!git push -u origin $(git symbolic-ref --short HEAD)"

git pushup   # works on any branch
```

---

## 6 · After editing *pyproject.toml* or *.pre‑commit‑config.yaml*

```bash
pre-commit clean          # clear cached virtualenvs
pre-commit run --all-files
git add .
git commit -m "chore: refresh lint config"
```

---

### Quick Cheat‑Sheet 📝

```bash
# format everything
git pc

# stage & commit
git add .
git commit -m "refactor: tidy" 

# push current branch
git pushup
```

Print this page and keep it next to your keyboard for new projects. 🚀
