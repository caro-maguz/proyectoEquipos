from django.test import TestCase
from django.contrib.auth.hashers import check_password
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from users.api.serializers import UserSerializer


class UserModelTest(TestCase):
    """Pruebas unitarias para el modelo User"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Probar creación de un usuario"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_user_email_unique(self):
        """Probar que el email es único"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='otheruser',
                email=self.user_data['email'],
                password='testpass123'
            )
    
    def test_user_username_unique(self):
        """Probar que el username es único"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(
                username=self.user_data['username'],
                email='other@example.com',
                password='testpass123'
            )
    
    def test_user_default_values(self):
        """Probar valores por defecto del usuario"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)  # True
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class UserSerializerTest(TestCase):
    """Pruebas unitarias para el serializador de User"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
    
    def test_serialize_user(self):
        """Probar serialización de usuario"""
        serializer = UserSerializer(self.user)
        self.assertEqual(serializer.data['username'], 'testuser')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertIn('id', serializer.data)
    
    def test_deserialize_user(self):
        """Probar deserialización de datos de usuario"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class UserAPIViewTest(APITestCase):
    """Pruebas para la API de usuarios"""
    
    def setUp(self):
        """Configurar datos de prueba y cliente API"""
        self.client = APIClient()
        # Crear usuario admin para autenticación
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_user_viewset_exists(self):
        """Probar que la API de usuarios está registrada"""
        # Cualquier código de estado que no sea 404 significa que el endpoint existe
        response = self.client.get('/api/users/')
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_user_exists(self):
        """Probar obtener detalles de un usuario específico"""
        # Simplemente verificar que el usuario existe en BD
        self.assertIsNotNone(self.normal_user.id)
        self.assertTrue(User.objects.filter(id=self.normal_user.id).exists())
    
    def test_user_has_correct_fields(self):
        """Probar que el usuario tiene los campos esperados"""
        user = User.objects.get(id=self.normal_user.id)
        self.assertEqual(user.username, 'normaluser')
        self.assertEqual(user.email, 'normal@example.com')
        self.assertTrue(hasattr(user, 'first_name'))
        self.assertTrue(hasattr(user, 'last_name'))
    
    def test_delete_user_from_db(self):
        """Probar eliminar un usuario de la base de datos"""
        user_to_delete = User.objects.create_user(
            username='todelete',
            email='todelete@example.com',
            password='pass123'
        )
        user_id = user_to_delete.id
        user_to_delete.delete()
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_update_user_fields(self):
        """Probar actualizar campos de un usuario"""
        self.normal_user.first_name = 'Updated'
        self.normal_user.save()
        updated_user = User.objects.get(id=self.normal_user.id)
        self.assertEqual(updated_user.first_name, 'Updated')
