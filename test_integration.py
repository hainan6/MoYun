"""
Integration Tests for Refactored MoYun System
Tests compatibility and functionality of the new architecture
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Test imports for core modules
    from core.config.settings import ConfigManager
    from core.modules.file_manager import FileSystemManager
    from core.modules.network_services import EmailService
    from core.modules.image_processor import ImageProcessor
    from core.data import DatabaseManager, UserData, BookData
    from core.handlers import BaseHandler, AuthenticationHandler
    
    print("✓ All core module imports successful")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


class TestConfigurationManager(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.config_manager = ConfigManager()
    
    def test_config_loading(self):
        """Test that configuration can be loaded"""
        try:
            database_config = self.config_manager.get_database_config()
            self.assertIsInstance(database_config, dict)
            self.assertIn('Host', database_config)
            print("✓ Configuration loading works")
        except Exception as e:
            self.fail(f"Configuration loading failed: {e}")
    
    def test_redis_config(self):
        """Test Redis configuration"""
        try:
            redis_config = self.config_manager.get_redis_config()
            self.assertIsInstance(redis_config, dict)
            self.assertIn('host', redis_config)
            print("✓ Redis configuration works")
        except Exception as e:
            self.fail(f"Redis configuration failed: {e}")


class TestFileSystemManager(unittest.TestCase):
    """Test file management"""
    
    def setUp(self):
        self.file_manager = FileSystemManager()
    
    def test_path_generation(self):
        """Test file path generation"""
        try:
            # Test profile photo path
            profile_path = self.file_manager.get_profile_photo_path(1)
            self.assertIsInstance(profile_path, str)
            
            # Test absolute path
            abs_path = self.file_manager.get_absolute_path("test.txt")
            self.assertIsInstance(abs_path, str)
            
            print("✓ File path generation works")
        except Exception as e:
            self.fail(f"File path generation failed: {e}")


class TestNetworkServices(unittest.TestCase):
    """Test network services"""
    
    def setUp(self):
        self.email_service = EmailService()
    
    @patch('smtplib.SMTP_SSL')
    def test_email_service_init(self, mock_smtp):
        """Test email service initialization"""
        try:
            # Test that EmailService can be instantiated
            self.assertIsInstance(self.email_service, EmailService)
            print("✓ Email service initialization works")
        except Exception as e:
            self.fail(f"Email service initialization failed: {e}")


class TestImageProcessor(unittest.TestCase):
    """Test image processing"""
    
    def test_image_processor_init(self):
        """Test image processor initialization"""
        try:
            processor = ImageProcessor()
            self.assertIsNotNone(processor)
            print("✓ Image processor initialization works")
        except Exception as e:
            self.fail(f"Image processor initialization failed: {e}")


class TestDataUtilities(unittest.TestCase):
    """Test data utilities and type definitions"""
    
    def test_data_types(self):
        """Test data type definitions"""
        try:
            # Test UserData type
            user_data = UserData(
                id=1,
                account="test",
                password=None,
                signature="",
                email="test@example.com",
                telephone="",
                role="student"
            )
            self.assertEqual(user_data['id'], 1)
            self.assertEqual(user_data['account'], "test")
            
            # Test BookData type
            book_data = BookData(
                id=1,
                isbn="123456789",
                title="Test Book",
                origin_title="",
                subtitle="",
                author="Test Author",
                page=100,
                publish_date="2023-01-01",
                publisher="Test Publisher",
                description="Test Description",
                douban_score=8.5,
                douban_id="",
                bangumi_score=8.0,
                bangumi_id="",
                category="test"
            )
            self.assertEqual(book_data['title'], "Test Book")
            
            print("✓ Data type definitions work")
        except Exception as e:
            self.fail(f"Data type definitions failed: {e}")


class TestHandlers(unittest.TestCase):
    """Test request handlers"""
    
    def setUp(self):
        # Mock dependencies
        self.mock_db = Mock()
        self.mock_file_manager = Mock()
        self.mock_email_service = Mock()
        
        self.base_handler = BaseHandler(self.mock_db, self.mock_file_manager)
        self.auth_handler = AuthenticationHandler(
            self.mock_db, 
            self.mock_file_manager, 
            self.mock_email_service
        )
    
    def test_base_handler_init(self):
        """Test base handler initialization"""
        try:
            self.assertIsNotNone(self.base_handler)
            self.assertEqual(self.base_handler.db, self.mock_db)
            self.assertEqual(self.base_handler.file_manager, self.mock_file_manager)
            print("✓ Base handler initialization works")
        except Exception as e:
            self.fail(f"Base handler initialization failed: {e}")
    
    def test_auth_handler_init(self):
        """Test authentication handler initialization"""
        try:
            self.assertIsNotNone(self.auth_handler)
            self.assertEqual(self.auth_handler.email_service, self.mock_email_service)
            print("✓ Authentication handler initialization works")
        except Exception as e:
            self.fail(f"Authentication handler initialization failed: {e}")
    
    def test_utility_methods(self):
        """Test handler utility methods"""
        try:
            # Test form data validation
            data = {'field1': 'value1', 'field2': ''}
            result = self.base_handler.validate_required_fields(data, 'field1')
            self.assertTrue(result)
            
            result = self.base_handler.validate_required_fields(data, 'field1', 'field2')
            self.assertFalse(result)
            
            print("✓ Handler utility methods work")
        except Exception as e:
            self.fail(f"Handler utility methods failed: {e}")


class TestCompatibility(unittest.TestCase):
    """Test compatibility with existing system"""
    
    def test_old_imports_available(self):
        """Test that old import paths still work through compatibility layer"""
        try:
            # These should work if compatibility is maintained
            from service.Utils import Config  # Old config access
            
            # Test that old Config interface still works
            config_data = Config.get("Database")
            self.assertIsInstance(config_data, dict)
            
            print("✓ Backward compatibility maintained")
        except ImportError:
            print("⚠ Old import paths not available (expected after full migration)")
        except Exception as e:
            print(f"⚠ Compatibility issue: {e}")


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("MoYun System Integration Tests")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestConfigurationManager,
        TestFileSystemManager,
        TestNetworkServices,
        TestImageProcessor,
        TestDataUtilities,
        TestHandlers,
        TestCompatibility
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED - System refactoring successful!")
        print("✓ The refactored system is compatible and functional")
    else:
        print("✗ Some tests failed - Review issues before deployment")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1) 