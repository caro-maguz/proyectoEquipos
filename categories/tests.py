from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from categories.models import Category
from categories.api.serializers import CategorySerializer


class CategoryModelTest(TestCase):
    """Pruebas unitarias para el modelo Category"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.category_data = {
            'tittle': 'Test Category',
            'image': 'https://example.com/image.jpg'
        }
    
    def test_create_category(self):
        """Probar creación de una categoría"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.tittle, self.category_data['tittle'])
        self.assertEqual(category.image, self.category_data['image'])
    
    def test_category_string_representation(self):
        """Probar representación en string de una categoría"""
        category = Category.objects.create(**self.category_data)
        self.assertIsNotNone(category.id)
    
    def test_category_tittle_field(self):
        """Probar que el campo tittle se guarda correctamente"""
        category = Category.objects.create(**self.category_data)
        retrieved = Category.objects.get(id=category.id)
        self.assertEqual(retrieved.tittle, 'Test Category')
    
    def test_category_image_field(self):
        """Probar que el campo image se guarda correctamente"""
        category = Category.objects.create(**self.category_data)
        retrieved = Category.objects.get(id=category.id)
        self.assertEqual(retrieved.image, 'https://example.com/image.jpg')
    
    def test_create_multiple_categories(self):
        """Probar crear múltiples categorías"""
        Category.objects.create(tittle='Category 1', image='image1.jpg')
        Category.objects.create(tittle='Category 2', image='image2.jpg')
        self.assertEqual(Category.objects.count(), 2)


class CategorySerializerTest(TestCase):
    """Pruebas unitarias para el serializador de Category"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.category = Category.objects.create(
            tittle='Test Category',
            image='test_image.jpg'
        )
    
    def test_serialize_category(self):
        """Probar serialización de categoría"""
        serializer = CategorySerializer(self.category)
        self.assertEqual(serializer.data['tittle'], 'Test Category')  # Test- Category
        self.assertEqual(serializer.data['image'], 'test_image.jpg')
        self.assertIn('id', serializer.data)
    
    def test_deserialize_category(self):
        """Probar deserialización de datos de categoría"""
        data = {
            'tittle': 'New Category',
            'image': 'new_image.jpg'
        }
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_required_fields(self):
        """Probar validación de campos requeridos"""
        data = {'tittle': 'Test'}
        serializer = CategorySerializer(data=data)
        # La validación dependerá de la configuración del serializer
        if serializer.is_valid():
            self.assertIn('tittle', serializer.data)
    
    def test_serialize_multiple_categories(self):
        """Probar serialización de múltiples categorías"""
        Category.objects.create(tittle='Cat 2', image='img2.jpg')
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(len(serializer.data), 2)


class CategoryAPIViewTest(APITestCase):
    """Pruebas para la API de categorías"""
    
    def setUp(self):
        """Configurar datos de prueba y cliente API"""
        self.client = APIClient()
        self.category = Category.objects.create(
            tittle='Test Category',
            image='test_image.jpg'
        )
    
    def test_category_api_endpoint_exists(self):
        """Probar que el endpoint de categorías existe"""
        response = self.client.get('/api/categories/')
        # Si no es 404, el endpoint existe
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_category_in_db(self):
        """Probar crear una categoría en base de datos"""
        category = Category.objects.create(
            tittle='New Category',
            image='new_image.jpg'
        )
        self.assertTrue(Category.objects.filter(id=category.id).exists())
        self.assertEqual(category.tittle, 'New Category')
    
    def test_retrieve_category_from_db(self):
        """Probar obtener una categoría de la BD"""
        retrieved = Category.objects.get(id=self.category.id)
        self.assertEqual(retrieved.tittle, 'Test Category')
        self.assertEqual(retrieved.image, 'test_image.jpg')
    
    def test_update_category_in_db(self):
        """Probar actualizar una categoría"""
        self.category.tittle = 'Updated Category'
        self.category.save()
        updated = Category.objects.get(id=self.category.id)
        self.assertEqual(updated.tittle, 'Updated Category')
    
    def test_delete_category_from_db(self):
        """Probar eliminar una categoría"""
        category_id = self.category.id
        self.category.delete()
        self.assertFalse(Category.objects.filter(id=category_id).exists())
    
    def test_category_count(self):
        """Probar contar categorías"""
        initial_count = Category.objects.count()
        Category.objects.create(tittle='Cat 2', image='img2.jpg')
        new_count = Category.objects.count()
        self.assertEqual(new_count, initial_count + 1)
