#!/bin/bash
# Script para subir a GitHub
# Uso: bash push_to_github.sh

echo "🚀 Casa Abuelos IA - GitHub Push Helper"
echo "======================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto"
    echo "   Usa: cd /home/oficina_ia/oficina_abuelos"
    exit 1
fi

echo ""
echo "📋 Verificando estado del repositorio..."
git status

echo ""
echo "📊 Commit pendiente:"
git log --oneline -1

echo ""
echo "🔗 Remote configurado:"
git remote -v

echo ""
echo "======================================="
echo ""
echo "🔐 Opciones de autenticación:"
echo ""
echo "1️⃣ HTTPS con Token (Recomendado)"
echo "   - URL: https://github.com/zoreza/casa_abuelos_IA.git"
echo "   - Usuario: tu-usuario-github"
echo "   - Password: tu-token-generado"
echo ""
echo "2️⃣ SSH Key"
echo "   - Requiere SSH key en GitHub"
echo "   - URL: git@github.com:zoreza/casa_abuelos_IA.git"
echo ""
echo "3️⃣ GitHub CLI"
echo "   - Instala: sudo apt install gh"
echo "   - Autentica: gh auth login"
echo ""
echo "======================================="
echo ""
read -p "Selecciona opción (1/2/3) o presiona ENTER para usar HTTPS: " option

case $option in
    1|"")
        echo ""
        echo "📤 Subiendo con HTTPS..."
        git branch -M main
        git push -u origin main
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ ¡Subida exitosa!"
            echo "🌐 Verifica en: https://github.com/zoreza/casa_abuelos_IA"
        else
            echo ""
            echo "❌ Error en push. Verifica:"
            echo "   - Token de acceso válido"
            echo "   - URL correcta"
            echo "   - Permisos en el repositorio"
        fi
        ;;
    2)
        echo ""
        echo "🔑 Configurando SSH..."
        git remote set-url origin git@github.com:zoreza/casa_abuelos_IA.git
        echo "📤 Subiendo con SSH..."
        git branch -M main
        git push -u origin main
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ ¡Subida exitosa!"
            echo "🌐 Verifica en: https://github.com/zoreza/casa_abuelos_IA"
        else
            echo ""
            echo "❌ Error: SSH key no configurada"
            echo "   Ve a: https://github.com/settings/keys"
        fi
        ;;
    3)
        echo ""
        echo "📦 Instalando GitHub CLI..."
        if command -v gh &> /dev/null; then
            echo "✅ GitHub CLI ya instalado"
        else
            echo "Instalando..."
            sudo apt-get update && sudo apt-get install -y gh
        fi
        echo ""
        echo "🔐 Autenticando..."
        gh auth login
        echo ""
        echo "📤 Subiendo..."
        git branch -M main
        git push -u origin main
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ ¡Subida exitosa!"
            echo "🌐 Verifica en: https://github.com/zoreza/casa_abuelos_IA"
        fi
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac
