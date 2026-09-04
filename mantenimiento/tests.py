from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from mantenimiento.models import Mantenimiento
from mantenimiento.api.serializers import MantenimientoSerializer


class MantenimientoModelTest(TestCase):
    """Pruebas unitarias para el modelo Mantenimiento"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.mantenimiento_data = {
            'nombre': 'Test Mantenimiento',
            'fecha': date.today(),
            'diagnostico': 'Test diagnostico completo'
        }
    
    def test_create_mantenimiento(self):
        """Probar creación de un mantenimiento"""
        mantenimiento = Mantenimiento.objects.create(**self.mantenimiento_data)
        self.assertEqual(mantenimiento.nombre, self.mantenimiento_data['nombre'])
        self.assertEqual(mantenimiento.fecha, self.mantenimiento_data['fecha'])
        self.assertEqual(mantenimiento.diagnostico, self.mantenimiento_data['diagnostico'])
    
    def test_mantenimiento_nombre_field(self):
        """Probar que el campo nombre se guarda correctamente"""
        mantenimiento = Mantenimiento.objects.create(**self.mantenimiento_data)
        retrieved = Mantenimiento.objects.get(id=mantenimiento.id)
        self.assertEqual(retrieved.nombre, 'Test Mantenimiento')
    
    def test_mantenimiento_fecha_field(self):
        """Probar que el campo fecha se guarda correctamente"""
        mantenimiento = Mantenimiento.objects.create(**self.mantenimiento_data)
        retrieved = Mantenimiento.objects.get(id=mantenimiento.id)
        self.assertEqual(retrieved.fecha, date.today())  # espera fecha +10
    
    def test_mantenimiento_diagnostico_field(self):
        """Probar que el campo diagnostico se guarda correctamente"""
        mantenimiento = Mantenimiento.objects.create(**self.mantenimiento_data)
        retrieved = Mantenimiento.objects.get(id=mantenimiento.id)
        self.assertEqual(retrieved.diagnostico, 'Test diagnostico completo')
    
    def test_mantenimiento_with_past_date(self):
        """Probar crear mantenimiento con fecha pasada"""
        past_date = date.today() - timedelta(days=10)
        mantenimiento = Mantenimiento.objects.create(
            nombre='Mantenimiento Pasado',
            fecha=past_date,
            diagnostico='Diagnostico de mantenimiento pasado'
        )
        self.assertEqual(mantenimiento.fecha, past_date)
    
    def test_mantenimiento_with_future_date(self):
        """Probar crear mantenimiento con fecha futura"""
        future_date = date.today() + timedelta(days=10)
        mantenimiento = Mantenimiento.objects.create(
            nombre='Mantenimiento Futuro',
            fecha=future_date,
            diagnostico='Diagnostico de mantenimiento futuro'
        )
        self.assertEqual(mantenimiento.fecha, future_date)
    
    def test_create_multiple_mantenimientos(self):
        """Probar crear múltiples mantenimientos"""
        Mantenimiento.objects.create(
            nombre='Mant 1',
            fecha=date.today(),
            diagnostico='Diagnostico 1'
        )
        Mantenimiento.objects.create(
            nombre='Mant 2',
            fecha=date.today(),
            diagnostico='Diagnostico 2'
        )
        self.assertEqual(Mantenimiento.objects.count(), 2)
    
    def test_mantenimiento_long_diagnostico(self):
        """Probar mantenimiento con diagnostico largo"""
        long_diagnostico = 'A' * 1000
        mantenimiento = Mantenimiento.objects.create(
            nombre='Long Diagnostico',
            fecha=date.today(),
            diagnostico=long_diagnostico
        )
        self.assertEqual(len(mantenimiento.diagnostico), 1000)


class MantenimientoSerializerTest(TestCase):
    """Pruebas unitarias para el serializador de Mantenimiento"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.mantenimiento = Mantenimiento.objects.create(
            nombre='Test Mantenimiento',
            fecha=date.today(),
            diagnostico='Test diagnostico'
        )
    
    def test_serialize_mantenimiento(self):
        """Probar serialización de mantenimiento"""
        serializer = MantenimientoSerializer(self.mantenimiento)
        self.assertEqual(serializer.data['nombre'], 'Test Mantenimiento')
        self.assertEqual(serializer.data['diagnostico'], 'Test diagnostico')
        self.assertIn('id', serializer.data)
        self.assertIn('fecha', serializer.data)
    
    def test_deserialize_mantenimiento(self):
        """Probar deserialización de datos de mantenimiento"""
        data = {
            'nombre': 'New Mantenimiento',
            'fecha': str(date.today()),
            'diagnostico': 'New diagnostico'
        }
        serializer = MantenimientoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serialize_multiple_mantenimientos(self):
        """Probar serialización de múltiples mantenimientos"""
        Mantenimiento.objects.create(
            nombre='Mant 2',
            fecha=date.today(),
            diagnostico='Diagnostico 2'
        )
        mantenimientos = Mantenimiento.objects.all()
        serializer = MantenimientoSerializer(mantenimientos, many=True)
        self.assertEqual(len(serializer.data), 2)
    
    def test_fecha_format_in_serializer(self):
        """Probar formato de fecha en serialización"""
        serializer = MantenimientoSerializer(self.mantenimiento)
        fecha_str = serializer.data['fecha']
        # La fecha debe ser válida
        self.assertIsNotNone(fecha_str)


class MantenimientoAPIViewTest(APITestCase):
    """Pruebas para la API de mantenimiento"""
    
    def setUp(self):
        """Configurar datos de prueba y cliente API"""
        self.client = APIClient()
        self.mantenimiento = Mantenimiento.objects.create(
            nombre='Test Mantenimiento',
            fecha=date.today(),
            diagnostico='Test diagnostico'
        )
    
    def test_mantenimiento_api_endpoint_exists(self):
        """Probar que el endpoint de mantenimiento existe"""
        response = self.client.get('/api/mantenimiento/')
        # Si no es 404, el endpoint existe
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_mantenimiento_in_db(self):
        """Probar crear un mantenimiento en BD"""
        mant = Mantenimiento.objects.create(
            nombre='New Mantenimiento',
            fecha=date.today(),
            diagnostico='New diagnostico'
        )
        self.assertTrue(Mantenimiento.objects.filter(id=mant.id).exists())
    
    def test_retrieve_mantenimiento_from_db(self):
        """Probar obtener un mantenimiento de la BD"""
        retrieved = Mantenimiento.objects.get(id=self.mantenimiento.id)
        self.assertEqual(retrieved.nombre, 'Test Mantenimiento')
    
    def test_update_mantenimiento_in_db(self):
        """Probar actualizar un mantenimiento"""
        self.mantenimiento.nombre = 'Updated'
        self.mantenimiento.save()
        updated = Mantenimiento.objects.get(id=self.mantenimiento.id)
        self.assertEqual(updated.nombre, 'Updated')
    
    def test_delete_mantenimiento_from_db(self):
        """Probar eliminar un mantenimiento"""
        mant_id = self.mantenimiento.id
        self.mantenimiento.delete()
        self.assertFalse(Mantenimiento.objects.filter(id=mant_id).exists())
    
    def test_mantenimiento_count(self):
        """Probar contar mantenimientos"""
        initial = Mantenimiento.objects.count()
        Mantenimiento.objects.create(
            nombre='Mant 2',
            fecha=date.today(),
            diagnostico='Diag 2'
        )
        self.assertEqual(Mantenimiento.objects.count(), initial + 1)
    
    def test_list_mantenimientos(self):
        """Probar listar mantenimientos desde BD"""
        all_mants = Mantenimiento.objects.all()
        self.assertTrue(all_mants.count() >= 1)
    
    def test_create_mantenimiento_with_past_date_in_db(self):
        """Probar crear mantenimiento con fecha pasada"""
        past_date = date.today() - timedelta(days=5)
        mant = Mantenimiento.objects.create(
            nombre='Past Mantenimiento',
            fecha=past_date,
            diagnostico='Past diagnostico'
        )
        retrieved = Mantenimiento.objects.get(id=mant.id)
        self.assertEqual(retrieved.fecha, past_date)
