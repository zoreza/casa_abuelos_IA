# 📚 Instrucciones para Upload a GitHub

## ✅ Estado Actual

El proyecto está completamente preparado para GitHub:

```bash
✅ Repositorio Git inicializado: /home/oficina_ia/oficina_abuelos
✅ Remote configurado: https://github.com/zoreza/casa_abuelos_IA.git
✅ Archivos en staging: 24 archivos
✅ Commit realizado: "🚀 Inicial commit: Sistema optimizado v2.0..."
```

## 🔐 Autenticación GitHub

### Opción 1: Token de Acceso (Recomendado)

```bash
# 1. Generar token en GitHub
# Ve a: https://github.com/settings/tokens
# Click "Generate new token (classic)"
# Selecciona scopes: repo, workflow
# Copia el token

# 2. Cuando git pida contraseña, usa el token
cd /home/oficina_ia/oficina_abuelos
git push -u origin main
# Username: tu-usuario-github
# Password: tu-token-generado
```

### Opción 2: SSH Key

```bash
# 1. Generar clave SSH (si no existe)
ssh-keygen -t ed25519 -C "tu-email@gmail.com"

# 2. Agregar SSH key a GitHub
# Ve a: https://github.com/settings/keys
# Allí copiar contenido de ~/.ssh/id_ed25519.pub

# 3. Cambiar URL del remote
git remote set-url origin git@github.com:zoreza/casa_abuelos_IA.git

# 4. Push
git push -u origin main
```

### Opción 3: GitHub CLI

```bash
# 1. Instalar GitHub CLI
# En macOS: brew install gh
# En Ubuntu: sudo apt install gh
# En Windows: choco install gh

# 2. Autenticar
gh auth login
# Sigue las instrucciones interactivas

# 3. Push
git push -u origin main
```

---

## 🚀 Comando Final para Push

Una vez autenticado, ejecuta:

```bash
cd /home/oficina_ia/oficina_abuelos
git branch -M main
git push -u origin main
```

---

## 📋 Archivos a Subir (24 Total)

### Infraestructura (6)
- ✅ `.env.example` - Plantilla de configuración
- ✅ `.gitignore` - Archivos a ignorar
- ✅ `scripts/config.py` - Configuración centralizada
- ✅ `scripts/utils.py` - Utilidades
- ✅ `scripts/database.py` - Persistencia
- ✅ `scripts/logger_config.py` - Logging

### Aplicación (8)
- ✅ `scripts/oficina_nueva.py` - **PRINCIPAL REFACTORIZADA**
- ✅ `scripts/oficina.py` - Original (respaldo)
- ✅ `scripts/oficina_v2.py` - Experimental
- ✅ `scripts/test_oficina.py` - Tests
- ✅ `scripts/debug_ia.py` - Verificación
- ✅ `scripts/bunker_2026.py` - Fallback
- ✅ `scripts/list_models.py` - Modelos
- ✅ `scripts/stress_test.py` - Testing

### Datos (4)
- ✅ `conocimiento/casa_abuelos.json` - Propiedades
- ✅ `conocimiento/disponibilidad.json` - Calendario
- ✅ `conocimiento/politicas.txt` - Políticas
- ✅ `conocimiento/propiedad.txt` - Resumen

### Documentación (5)
- ✅ `README.md` - Documentación principal
- ✅ `INICIO_RAPIDO.md` - Guía rápida
- ✅ `OPTIMIZACIONES_REALIZADAS.md` - Detalles
- ✅ `ANTES_Y_DESPUES.md` - Comparación
- ✅ `GITHUB_README.md` - Para GitHub

### Otros (1)
- ✅ `requirements.txt` - Dependencias

---

## 🔍 Verificar Antes de Push

```bash
cd /home/oficina_ia/oficina_abuelos

# Ver estado
git status

# Ver commit pendiente
git log --oneline -1

# Ver archivos a subir
git diff --cached --name-only
```

---

## ⚠️ IMPORTANTE: .env NO se incluye

El archivo `.env` (con credenciales reales) **NO** se sube a GitHub porque:

1. ✅ Está en `.gitignore`
2. ✅ Contiene `GOOGLE_API_KEY` sensible
3. ✅ Los usuarios harán `cp .env.example .env` y llenarán sus credenciales

---

## ✨ Después del Push (En GitHub)

### 1. Verificar el repositorio
- Ve a: https://github.com/zoreza/casa_abuelos_IA
- Verifica que todos los archivos están allí
- Revisa que `.env` NO aparece (✅ correcto)

### 2. Agregar descripción
En la página del repositorio:
- Click en "Edit" (ícono lápiz) al lado del nombre
- Agrega descripción: "Sistema inteligente multiagente para gestión de reservas"
- Selecciona lenguaje: Python

### 3. Agregar temas
- Add topics: `python`, `crewai`, `ai`, `multiagent`, `chatbot`

### 4. Configurar GitHub Pages (Opcional)
- Settings → Pages
- Source: Main branch
- Folder: / (root)

---

## 📊 Estructura en GitHub

```
casa_abuelos_IA/
├── .env.example              ← Copiar para .env
├── .gitignore                ← Protege .env
├── README.md                 ← Home del repo
├── requirements.txt          ← pip install -r
├── scripts/
│   ├── oficina_nueva.py      ← EJECUTABLE PRINCIPAL
│   ├── config.py             ← Importar
│   ├── utils.py              ← Importar
│   ├── database.py           ← Importar
│   └── test_oficina.py       ← pytest
├── conocimiento/
│   ├── casa_abuelos.json
│   └── disponibilidad.json
└── (Documentación)
    ├── INICIO_RAPIDO.md
    ├── OPTIMIZACIONES_REALIZADAS.md
    └── ANTES_Y_DESPUES.md
```

---

## 🔄 Próximos Commits

Después del primer push, para futuros cambios:

```bash
# 1. Editar archivos
nano scripts/config.py

# 2. Crear commit
git add scripts/config.py
git commit -m "🔧 Actualizar configuración"

# 3. Push
git push
```

---

## 💡 Comandos Git Útiles

```bash
# Ver historial
git log --oneline

# Ver diferencias
git diff

# Deshacer cambios
git restore archivo.py

# Crear rama de feature
git checkout -b feature/nueva-caracteristica

# Merge de rama
git merge feature/nueva-caracteristica
```

---

## ✅ Checklist Final

- [ ] GitHub CLI o SSH key configurado
- [ ] Token de acceso generado (si usas HTTPS)
- [ ] `.env` está en `.gitignore` ✅
- [ ] `git status` muestra todo limpio
- [ ] `git log` muestra el commit inicial
- [ ] `git remote -v` muestra origin correcto

Luego ejecuta:
```bash
git push -u origin main
```

---

**¡Listo para GitHub! 🚀**

Si tienes problemas con autenticación, usa GitHub CLI:
```bash
gh auth login
```

