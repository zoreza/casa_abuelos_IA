#!/bin/bash
# 🚀 PUSH A GITHUB - INSTRUCCIONES FINALES

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🎉 CASA ABUELOS IA - LISTO PARA GITHUB 🎉                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd /home/oficina_ia/oficina_abuelos

# Mostrar estado
echo "📊 ESTADO ACTUAL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Archivos creados: 25"
echo "✅ Repositorio Git: Inicializado"
echo "✅ Commit #1: Realizado"
echo "✅ Remote origin: git@github.com:zoreza/casa_abuelos_IA.git"
echo "✅ Rama principal: main"
echo ""
echo "📋 CONTENIDO DEL COMMIT:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git log --oneline -1
echo ""

# Contar archivos por tipo
echo "📂 ARCHIVOS POR CATEGORÍA:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  📄 Scripts Python (.py):"
find scripts -maxdepth 1 -name "*.py" | wc -l | xargs echo "    Cantidad:"
echo ""
echo "  📚 Documentación (.md):"
find . -maxdepth 1 -name "*.md" | wc -l | xargs echo "    Cantidad:"
echo ""
echo "  📋 Datos JSON (.json):"
find conocimiento -name "*.json" | wc -l | xargs echo "    Cantidad:"
echo ""
echo "  🔧 Configuración:"
echo "    - requirements.txt"
echo "    - .env.example"
echo "    - .gitignore"
echo ""

# Ver si gh está disponible
echo "🔐 VERIFICACIÓN DE AUTENTICACIÓN:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI instalado"
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI autenticado"
        echo ""
        echo "🚀 PUSH CON UN COMANDO:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "  git push -u origin main"
        echo ""
        echo "Presiona ENTER para ejecutar el push..."
        read
        echo ""
        git push -u origin main
        if [ $? -eq 0 ]; then
            echo ""
            echo "╔════════════════════════════════════════════════════════════════╗"
            echo "║  ✅ ¡PUSH EXITOSO! 🎉                                          ║"
            echo "╚════════════════════════════════════════════════════════════════╝"
            echo ""
            echo "🌐 Repositorio disponible en:"
            echo "   https://github.com/zoreza/casa_abuelos_IA"
            echo ""
            echo "📖 Archivos principales:"
            echo "   • scripts/oficina_nueva.py (EJECUTABLE)"
            echo "   • README.md (Documentación)"
            echo "   • INICIO_RAPIDO.md (Quick start)"
            echo "   • requirements.txt (pip install)"
            echo ""
        else
            echo ""
            echo "❌ Error en el push:"
            echo "   - Verifica que tienes acceso al repositorio"
            echo "   - Confirma que el repositorio existe en GitHub"
            echo "   - Intenta: gh auth login"
            echo ""
        fi
    else
        echo "⚠️ GitHub CLI no autenticado"
        echo ""
        echo "🔑 Autentica con:"
        echo "   gh auth login"
        echo ""
        echo "Sigue las instrucciones interactivas en pantalla"
    fi
else
    echo "⚠️ GitHub CLI no instalado"
    echo ""
    echo "Instalando GitHub CLI..."
    sudo apt-get update && sudo apt-get install -y gh
    echo ""
    echo "Iniciando autenticación..."
    gh auth login
    echo ""
    echo "Ejecuta de nuevo este script"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Más información en: LISTO_PARA_GITHUB.md                      ║"
echo "║  Documentación en: README.md                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
