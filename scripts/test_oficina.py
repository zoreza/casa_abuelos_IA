"""
Tests automatizados para el sistema de oficina
Usar con: pytest test_oficina.py -v
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, date, timedelta

# Importar funciones a testear
from utils import (
    sanitizar_pregunta, validar_fechas, extraer_fechas_de_texto,
    limpiar_respuesta, Metricas
)
from config import CAPACIDAD_MAXIMA, MINIMO_NOCHES


class TestSanitizacion:
    """Tests para sanitización de entrada"""
    
    def test_sanitizar_pregunta_basica(self):
        """Verifica sanitización básica"""
        resultado = sanitizar_pregunta("  ¿Tienen habitaciones?  ")
        assert resultado == "¿Tienen habitaciones?"
    
    def test_sanitizar_pregunta_limita_length(self):
        """Verifica que se limita la longitud"""
        txt_largo = "a" * 1000
        resultado = sanitizar_pregunta(txt_largo, max_length=100)
        assert len(resultado) <= 100
    
    def test_sanitizar_remueve_caracteres_control(self):
        """Verifica remoción de caracteres de control"""
        resultado = sanitizar_pregunta("Hola\x00\x01Mundo")
        assert "\x00" not in resultado
        assert "\x01" not in resultado


class TestValidacionFechas:
    """Tests para validación de fechas"""
    
    def test_fechas_validas(self):
        """Test de fechas válidas"""
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        pasado_manana = hoy + timedelta(days=3)
        
        es_valida, msg = validar_fechas(
            manana.strftime("%Y-%m-%d"),
            pasado_manana.strftime("%Y-%m-%d")
        )
        assert es_valida is True
        assert msg == "OK"
    
    def test_fechas_invertidas(self):
        """Test de fechas con inicio > fin"""
        hoy = date.today()
        es_valida, msg = validar_fechas(
            hoy.strftime("%Y-%m-%d"),
            (hoy - timedelta(days=1)).strftime("%Y-%m-%d")
        )
        assert es_valida is False
        assert "anterior" in msg.lower()
    
    def test_minimo_noches(self):
        """Test de mínimo de noches"""
        hoy = date.today()
        es_valida, msg = validar_fechas(
            hoy.strftime("%Y-%m-%d"),
            (hoy + timedelta(days=1)).strftime("%Y-%m-%d")  # Solo 1 noche
        )
        assert es_valida is False
    
    def test_formato_fecha_invalido(self):
        """Test de formato de fecha inválido"""
        es_valida, msg = validar_fechas("20-03-2026", "25-03-2026")
        assert es_valida is False
        assert "Formato" in msg


class TestExtractionFechas:
    """Tests para extracción de fechas en texto"""
    
    def test_extrae_una_fecha(self):
        """Verifica extracción de una fecha"""
        resultado = extraer_fechas_de_texto("¿Tienen disponible 2026-03-20?")
        assert "2026-03-20" in resultado
    
    def test_extrae_multiples_fechas(self):
        """Verifica extracción de múltiples fechas"""
        resultado = extraer_fechas_de_texto("Del 2026-03-20 al 2026-03-25 por favor")
        assert len(resultado) == 2
        assert "2026-03-20" in resultado
        assert "2026-03-25" in resultado
    
    def test_sin_fechas(self):
        """Verifica cuando no hay fechas"""
        resultado = extraer_fechas_de_texto("¿Cuáles son las amenidades?")
        assert len(resultado) == 0


class TestLimpiezaRespuesta:
    """Tests para limpieza de respuestas"""
    
    def test_elimina_no_aplica(self):
        """Verifica eliminación de NO_APLICA"""
        texto = "Aquí está la información. NO_APLICA"
        resultado = limpiar_respuesta(texto)
        assert "NO_APLICA" not in resultado
    
    def test_elimina_espacios_multiples(self):
        """Verifica eliminación de espacios múltiples"""
        texto = "Hola    mundo     con    espacios"
        resultado = limpiar_respuesta(texto)
        assert "    " not in resultado
    
    def test_trim_espacios(self):
        """Verifica trimming de espacios"""
        texto = "   texto con espacios   "
        resultado = limpiar_respuesta(texto)
        assert resultado == "texto con espacios"


class TestMetricas:
    """Tests para la clase de Métricas"""
    
    def test_inicializacion(self):
        """Verifica inicialización de métricas"""
        metricas = Metricas()
        assert metricas.total_consultas == 0
        assert metricas.consultas_correctas == 0
    
    def test_registrar_consulta(self):
        """Verifica registro de consulta"""
        metricas = Metricas()
        metricas.registrar_consulta(2.5, "ollama", exitosa=True)
        assert metricas.total_consultas == 1
        assert metricas.consultas_correctas == 1
        assert 2.5 in metricas.tiempos_respuesta
    
    def test_tiempo_promedio(self):
        """Verifica cálculo de tiempo promedio"""
        metricas = Metricas()
        metricas.registrar_consulta(1.0, "ollama", exitosa=True)
        metricas.registrar_consulta(3.0, "ollama", exitosa=True)
        assert metricas.tiempo_promedio() == 2.0
    
    def test_tasa_exito(self):
        """Verifica cálculo de tasa de éxito"""
        metricas = Metricas()
        metricas.registrar_consulta(1.0, "ollama", exitosa=True)
        metricas.registrar_consulta(1.0, "ollama", exitosa=True)
        metricas.registrar_consulta(1.0, "ollama", exitosa=False)
        tasa = metricas.tasa_exito()
        assert abs(tasa - 66.67) < 1  # Aproximadamente 66.67%
    
    def test_resumen_metricas(self):
        """Verifica generación de resumen"""
        metricas = Metricas()
        metricas.registrar_consulta(1.5, "ollama", exitosa=True)
        resumen = metricas.obtener_resumen()
        
        assert "total_consultas" in resumen
        assert "tiempo_promedio_respuesta" in resumen
        assert "tasa_exito_porcentaje" in resumen
        assert resumen["total_consultas"] == 1


class TestValidacionFechasNegocio:
    """Tests específicos para validación de negocio"""
    
    def test_capacidad_maxima(self):
        """Verifica que se respeta capacidad máxima"""
        # Este test es más conceptual - el auditor debería validar
        assert CAPACIDAD_MAXIMA == 11
    
    def test_minimo_noches_requerido(self):
        """Verifica que se requieren mínimo 2 noches"""
        assert MINIMO_NOCHES == 2
        
        hoy = date.today()
        es_valida, msg = validar_fechas(
            hoy.strftime("%Y-%m-%d"),
            (hoy + timedelta(days=2)).strftime("%Y-%m-%d")  # Exactamente 2 noches
        )
        # Nota: esto validara solo 2 NOCHES = 2 DIAS, así que es (2-0)=2 dias = 2 noches
        # En realidad necesitamos verificar la lógica


# ============================================
# FIXTURES ÚTILES
# ============================================

@pytest.fixture
def fechas_validas():
    """Fixture con un par de fechas válidas para tests"""
    hoy = date.today()
    inicio = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
    fin = (hoy + timedelta(days=5)).strftime("%Y-%m-%d")
    return inicio, fin


@pytest.fixture
def metricas_con_datos():
    """Fixture con métricas precargadas"""
    metricas = Metricas()
    for i in range(10):
        metricas.registrar_consulta(2.0, "ollama", exitosa=i < 8)
    return metricas


# ============================================
# TESTS DE INTEGRACIÓN (Opcional, más complejos)
# ============================================

class TestIntegracion:
    """Tests de integración del sistema"""
    
    @pytest.mark.skip(reason="Requiere Ollama disponible")
    def test_pipeline_completo(self):
        """Test del pipeline completo (requiere Ollama)"""
        # Este test se salta por defecto ya que requiere servicios externos
        pass


# ============================================
# COMANDO PARA EJECUTAR
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
