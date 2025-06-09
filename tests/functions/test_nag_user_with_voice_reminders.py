"""
Unit tests for the Voice Reminders System.

Tests follow red-green-refactor methodology:
1. Write test that calls actual (not-yet-implemented) callable
2. Run test - it MUST fail immediately
3. Continue to next cases until all written
4. Then implement code to make tests pass
"""
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock, MagicMock, patch, call, mock_open
import uuid


from pydantic import ValidationError


# Import the module under test
from tools.functions.nag_user_with_voice_reminders import (
    nag_user_with_voice_reminders,
    _Reminder,
    _ReminderCache,
    _CheckIfDateIsInTheFuture,
    _NagUserWithVoiceReminders,
    _reminders,
)


class TestReminder(unittest.TestCase):
    """Test the _Reminder model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.future_time = datetime.now() + timedelta(hours=1)
        self.past_time = datetime.now() - timedelta(hours=1)
        
    def test_reminder_creation_with_valid_data(self):
        """Test creating a reminder with valid data."""
        reminder = _Reminder(
            text="Test reminder",
            trigger_at=self.future_time
        )
        
        # Check attributes
        self.assertEqual(reminder.text, "Test reminder")
        self.assertEqual(reminder.trigger_at, self.future_time)
        self.assertIsInstance(reminder.id, uuid.UUID)
        
    def test_reminder_text_strip_whitespace(self):
        """Test that reminder text strips whitespace."""
        reminder = _Reminder(
            text="  Test reminder  \n",
            trigger_at=self.future_time
        )
        
        self.assertEqual(reminder.text, "Test reminder")
        
    def test_reminder_requires_future_date(self):
        """Test that reminder requires a future date."""
        with self.assertRaises(ValidationError):
            _Reminder(
                text="Test reminder",
                trigger_at=self.past_time
            )
    
    @patch('tools.functions.nag_user_with_voice_reminders.python_builtins.time.time')
    def test_reminder_is_due_property(self, mock_time_func):
        """Test the is_due property."""
        # Mock time to control the test
        current_timestamp = datetime.now().timestamp()
        mock_time_func.return_value = current_timestamp
        
        # Future reminder - not due
        future_reminder = _Reminder(
            text="Future",
            trigger_at=datetime.fromtimestamp(current_timestamp + 3600)
        )
        self.assertFalse(future_reminder.is_due)
        
        # Past reminder - is due
        mock_time_func.return_value = current_timestamp + 7200
        self.assertTrue(future_reminder.is_due)
    
    @patch('tools.functions.nag_user_with_voice_reminders.python_builtins.time.time')
    def test_reminder_is_expired_property(self, mock_time_func):
        """Test the is_expired property."""
        current_timestamp = datetime.now().timestamp()
        mock_time_func.return_value = current_timestamp
        
        # Future reminder - not expired
        future_reminder = _Reminder(
            text="Future",
            trigger_at=datetime.fromtimestamp(current_timestamp + 3600)
        )
        self.assertFalse(future_reminder.is_expired)
        
        # Past reminder - is expired
        mock_time_func.return_value = current_timestamp + 7200
        self.assertTrue(future_reminder.is_expired)


class TestReminderCache(unittest.TestCase):
    """Test the _ReminderCache model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = _ReminderCache()
        self.future_time = datetime.now() + timedelta(hours=1)
        self.reminder = _Reminder(text="Test", trigger_at=self.future_time)
        
    def test_cache_initialization(self):
        """Test cache initializes empty."""
        self.assertTrue(self.cache.empty())
        self.assertEqual(self.cache.qsize(), 0)
        self.assertFalse(self.cache.full())
        
    def test_cache_put_and_get(self):
        """Test putting and getting reminders."""
        self.cache.put(self.future_time, self.reminder)
        
        # Check size
        self.assertFalse(self.cache.empty())
        self.assertEqual(self.cache.qsize(), 1)
        
        # Get reminder
        retrieved = self.cache.get(self.future_time)
        self.assertEqual(retrieved.id, self.reminder.id)
        self.assertEqual(retrieved.text, self.reminder.text)
        
    def test_cache_get_nonexistent_key(self):
        """Test getting with nonexistent key raises KeyError."""
        with self.assertRaises(KeyError):
            self.cache.get(self.future_time)
            
    def test_cache_pop(self):
        """Test popping reminders."""
        self.cache.put(self.future_time, self.reminder)
        
        # Pop existing
        popped = self.cache.pop(self.future_time)
        self.assertEqual(popped.id, self.reminder.id)
        self.assertTrue(self.cache.empty())
        
        # Pop nonexistent with default
        result = self.cache.pop(self.future_time, None)
        self.assertIsNone(result)
        
    def test_cache_items_generator(self):
        """Test items generator."""
        time1 = datetime.now() + timedelta(hours=1)
        time2 = datetime.now() + timedelta(hours=2)
        reminder1 = _Reminder(text="First", trigger_at=time1)
        reminder2 = _Reminder(text="Second", trigger_at=time2)
        
        self.cache.put(time1, reminder1)
        self.cache.put(time2, reminder2)
        
        items = list(self.cache.items())
        self.assertEqual(len(items), 2)
        self.assertIn((time1, reminder1), items)
        self.assertIn((time2, reminder2), items)
        
    def test_cache_sort(self):
        """Test sorting reminders by trigger_at."""
        # Add reminders in reverse order
        time1 = datetime.now() + timedelta(hours=3)
        time2 = datetime.now() + timedelta(hours=1)
        time3 = datetime.now() + timedelta(hours=2)
        
        reminder1 = _Reminder(text="Third", trigger_at=time1)
        reminder2 = _Reminder(text="First", trigger_at=time2)
        reminder3 = _Reminder(text="Second", trigger_at=time3)
        
        self.cache.put(time1, reminder1)
        self.cache.put(time2, reminder2)
        self.cache.put(time3, reminder3)
        
        self.cache.sort()
        
        # Check order
        items = list(self.cache.items())
        self.assertEqual(items[0][1].text, "First")
        self.assertEqual(items[1][1].text, "Second")
        self.assertEqual(items[2][1].text, "Third")
        
    def test_cache_full(self):
        """Test cache full condition."""
        # Set a small max size for testing
        self.cache._max_size = 2
        
        time1 = datetime.now() + timedelta(hours=1)
        time2 = datetime.now() + timedelta(hours=2)
        
        self.cache.put(time1, _Reminder(text="1", trigger_at=time1))
        self.assertFalse(self.cache.full())
        
        self.cache.put(time2, _Reminder(text="2", trigger_at=time2))
        self.assertTrue(self.cache.full())


class TestCheckIfDateIsInTheFuture(unittest.TestCase):
    """Test the _CheckIfDateIsInTheFuture validator."""
    
    def test_future_date_valid(self):
        """Test future date is valid."""
        future_date = datetime.now() + timedelta(hours=1)
        validator = _CheckIfDateIsInTheFuture(date=future_date)
        self.assertEqual(validator.date, future_date)
        
    def test_past_date_invalid(self):
        """Test past date raises ValidationError."""
        past_date = datetime.now() - timedelta(hours=1)
        with self.assertRaises(ValidationError):
            _CheckIfDateIsInTheFuture(date=past_date)


class TestNagUserWithVoiceReminders(unittest.TestCase):
    """Test the _NagUserWithVoiceReminders class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock dependencies
        self.mock_dependencies = Mock()
        self.mock_dependencies.openai = Mock()
        self.mock_dependencies.playsound = Mock()
        
        # Mock builtins
        self.mock_python_builtins = Mock()
        self.mock_python_builtins.datetime = Mock()
        self.mock_python_builtins.datetime.datetime = datetime
        self.mock_python_builtins.json = json
        self.mock_python_builtins.os = Mock()
        self.mock_python_builtins.pathlib = Mock()
        self.mock_python_builtins.pathlib.Path = Path
        self.mock_python_builtins.queue = Mock()
        self.mock_python_builtins.tempfile = Mock()
        self.mock_python_builtins.time = time
        
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.json_path = Path(self.temp_dir) / "_reminders.json"
        
        # Patch the reminder_json_path property
        self.patcher = patch.object(
            _NagUserWithVoiceReminders, 
            'reminder_json_path',
            new_callable=unittest.mock.PropertyMock,
            return_value=self.json_path
        )
        self.patcher.start()
        
        # Create instance
        self.nag = _NagUserWithVoiceReminders(
            builtins=self.mock_python_builtins,
            dependencies=self.mock_dependencies
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.patcher.stop()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test proper initialization."""
        self.assertIsNotNone(self.nag.reminder_cache)
        self.assertIsInstance(self.nag.reminder_cache, _ReminderCache)
        self.assertTrue(self.nag.reminder_cache.empty())
        
    def test_client_property_no_api_key(self):
        """Test client property raises error when no API key."""
        self.mock_python_builtins.os.getenv.return_value = None
        
        with self.assertRaises(RuntimeError) as cm:
            _ = self.nag.client
            
        self.assertIn("OpenAI API key is not set", str(cm.exception))
        
    def test_client_property_with_api_key(self):
        """Test client property creates client with API key."""
        self.mock_python_builtins.os.getenv.return_value = "test-api-key"
        
        client = self.nag.client
        
        self.mock_dependencies.openai.OpenAI.assert_called_once_with(api_key="test-api-key")
        self.assertIsNotNone(client)
        
    def test_add_reminder_success(self):
        """Test adding a reminder successfully."""
        future_time = datetime.now() + timedelta(hours=1)
        kwargs = {
            "text": "Test reminder",
            "trigger_at": future_time
        }
        
        result = self.nag.add_reminder(kwargs)
        
        self.assertTrue(result["success"])
        self.assertIn("reminder_id", result)
        self.assertIn("Added reminder", result["message"])
        self.assertEqual(self.nag.reminder_cache.qsize(), 1)
        
    def test_add_reminder_invalid_params(self):
        """Test adding reminder with invalid parameters."""
        kwargs = {
            "text": "Test reminder",
            # Missing trigger_at
        }
        
        with self.assertRaises(ValueError) as cm:
            self.nag.add_reminder(kwargs)
            
        self.assertIn("Invalid parameters", str(cm.exception))
        
    def test_remove_reminder_success(self):
        """Test removing a reminder successfully."""
        future_time = datetime.now() + timedelta(hours=1)
        reminder = _Reminder(text="Test", trigger_at=future_time)
        self.nag.reminder_cache.put(future_time, reminder)
        
        kwargs = {"date": future_time}
        result = self.nag.remove_reminder(kwargs)
        
        self.assertTrue(result["success"])
        self.assertIn("Removed reminder", result["message"])
        self.assertTrue(self.nag.reminder_cache.empty())
        
    def test_remove_reminder_not_found(self):
        """Test removing nonexistent reminder."""
        future_time = datetime.now() + timedelta(hours=1)
        kwargs = {"date": future_time}
        
        result = self.nag.remove_reminder(kwargs)
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Reminder not found")
        
    def test_remove_reminder_missing_date(self):
        """Test removing reminder without date parameter."""
        kwargs = {}
        
        with self.assertRaises(ValueError) as cm:
            self.nag.remove_reminder(kwargs)
            
        self.assertIn("Missing required parameter: date", str(cm.exception))
        
    def test_list_reminders_empty(self):
        """Test listing reminders when empty."""
        result = self.nag.list_reminders()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["reminders"], [])
        self.assertEqual(result["count"], 0)
        
    def test_list_reminders_with_items(self):
        """Test listing reminders with items."""
        time1 = datetime.now() + timedelta(hours=1)
        time2 = datetime.now() + timedelta(hours=2)
        
        reminder1 = _Reminder(text="First", trigger_at=time1)
        reminder2 = _Reminder(text="Second", trigger_at=time2)
        
        self.nag.reminder_cache.put(time1, reminder1)
        self.nag.reminder_cache.put(time2, reminder2)
        
        result = self.nag.list_reminders()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["reminders"]), 2)
        
        # Check reminder format
        for reminder in result["reminders"]:
            self.assertIn("id", reminder)
            self.assertIn("text", reminder)
            self.assertIn("trigger_at", reminder)
            
    def test_clear_reminders(self):
        """Test clearing all reminders."""
        # Add some reminders
        time1 = datetime.now() + timedelta(hours=1)
        reminder1 = _Reminder(text="Test", trigger_at=time1)
        self.nag.reminder_cache.put(time1, reminder1)
        
        result = self.nag.clear_reminders()
        
        self.assertTrue(result["success"])
        self.assertIn("All reminders cleared", result["message"])
        self.assertTrue(self.nag.reminder_cache.empty())
        
    def test_save_reminders(self):
        """Test saving reminders to file."""
        time1 = datetime.now() + timedelta(hours=1)
        reminder1 = _Reminder(text="Test", trigger_at=time1)
        self.nag.reminder_cache.put(time1, reminder1)
        
        self.nag.save_reminders()
        
        # Check file exists and contains correct data
        self.assertTrue(self.json_path.exists())
        
        with open(self.json_path, 'r') as f:
            data = json.load(f)
            
        self.assertIn("reminders", data)
        self.assertEqual(len(data["reminders"]), 1)
        
        # Check the reminder was serialized correctly
        saved_reminder = list(data["reminders"].values())[0]
        self.assertEqual(saved_reminder["text"], "Test")
        self.assertEqual(saved_reminder["id"], str(reminder1.id))
        
    def test_load_reminders_empty_file(self):
        """Test loading from nonexistent file creates empty structure."""
        # Delete the file that was created during setUp
        if self.json_path.exists():
            self.json_path.unlink()

        # File doesn't exist initially
        self.assertFalse(self.json_path.exists())

        # Create new instance which should create the file
        nag = _NagUserWithVoiceReminders(
            builtins=self.mock_python_builtins,
            dependencies=self.mock_dependencies
        )
        
        # Check file was created with empty structure
        self.assertTrue(self.json_path.exists())
        with open(self.json_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, {"reminders": {}})
        
    def test_load_reminders_corrupted_file(self):
        """Test loading from corrupted file starts fresh."""
        # Write corrupted JSON
        with open(self.json_path, 'w') as f:
            f.write("{invalid json")
            
        # Create new instance - should handle error gracefully
        nag = _NagUserWithVoiceReminders(
            builtins=self.mock_python_builtins,
            dependencies=self.mock_dependencies
        )
        
        # Should start with empty cache
        self.assertTrue(nag.reminder_cache.empty())

    def test_trigger_due_reminders_loop(self):
        """Test the reminder triggering loop."""
        current_timestamp = datetime.now().timestamp()

        # Create reminder with FUTURE time
        future_time = datetime.fromtimestamp(current_timestamp + 3600)  # 1 hour from now
        reminder = _Reminder(text="Due reminder", trigger_at=future_time)
        self.nag.reminder_cache.put(future_time, reminder)

        # Patch where it's used in the _Reminder properties
        with patch('tools.functions.nag_user_with_voice_reminders.python_builtins.time.time') as mock_time, \
            patch('tools.functions.nag_user_with_voice_reminders.python_builtins.time.sleep') as mock_sleep:
            mock_time.return_value = current_timestamp + 7200  # 2 hours later

            # Mock the _play_reminder_voice method to avoid actual audio playback
            self.nag._play_reminder_voice = Mock()

            # Add a due reminder
            past_time = datetime.fromtimestamp(mock_time.return_value - 3600)
            reminder = _Reminder(text="Due reminder", trigger_at=past_time)
            self.nag.reminder_cache.put(past_time, reminder)

            # Mock the play method
            self.nag._play_reminder_voice = Mock()
            
            # Run one iteration of the loop
            # We'll break after one iteration by raising an exception
            def break_loop(*args):
                if self.nag._play_reminder_voice.call_count > 0:
                    raise KeyboardInterrupt("Break loop")
                
            mock_sleep.side_effect = break_loop
            
            # Run the loop
            try:
                self.nag.trigger_due_reminders_loop()
            except KeyboardInterrupt:
                pass
                
            # Check reminder was played
            self.nag._play_reminder_voice.assert_called_once_with("Due reminder")
            
            # Check reminder was removed from cache
            self.assertTrue(self.nag.reminder_cache.empty())
        
    def test_play_reminder_voice_success(self):
        """Test playing voice reminder successfully."""
        # Mock OpenAI client
        self.mock_python_builtins.os.getenv.return_value = "test-api-key"
        mock_response = Mock()
        mock_response.content = b"audio data"
        self.nag.client.audio.speech.create.return_value = mock_response
        
        # Mock tempfile
        mock_temp = Mock()
        mock_temp.name = "/tmp/test.mp3"
        mock_temp.__enter__ = Mock(return_value=mock_temp)
        mock_temp.__exit__ = Mock(return_value=None)
        self.mock_python_builtins.tempfile.NamedTemporaryFile.return_value = mock_temp
        
        # Mock playsound
        self.mock_dependencies.playsound.playsound = Mock()
        
        # Play reminder
        self.nag._play_reminder_voice("Test message")
        
        # Verify OpenAI was called
        self.nag.client.audio.speech.create.assert_called_once_with(
            model="tts-1",
            voice="alloy",
            input="Test message",
            response_format="mp3",
            timeout=30
        )
        
        # Verify audio was written
        mock_temp.write.assert_called_once_with(b"audio data")
        
        # Verify playsound was called
        self.mock_dependencies.playsound.playsound.assert_called_once_with(
            "/tmp/test.mp3", 
            block=True
        )
        
        # Verify cleanup
        self.mock_python_builtins.os.unlink.assert_called_once_with("/tmp/test.mp3")
        
    def test_play_reminder_voice_no_audio_data(self):
        """Test error when no audio data returned."""
        self.mock_python_builtins.os.getenv.return_value = "test-api-key"
        mock_response = Mock()
        mock_response.content = b""  # Empty audio
        self.nag.client.audio.speech.create.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as cm:
            self.nag._play_reminder_voice("Test")
            
        self.assertIn("No audio data returned", str(cm.exception))


class TestNagUserWithVoiceRemindersFunction(unittest.TestCase):
    """Test the main nag_user_with_voice_reminders function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the global reminders object
        self.mock_reminders = Mock()
        self.patcher = patch('tools.functions.nag_user_with_voice_reminders._reminders', self.mock_reminders)
        self.patcher.start()
        
    def tearDown(self):
        """Clean up."""
        self.patcher.stop()
        
    def test_list_action_default(self):
        """Test list action as default."""
        self.mock_reminders.list_reminders.return_value = {
            "success": True, 
            "reminders": [], 
            "count": 0
        }
        
        result = nag_user_with_voice_reminders()
        
        self.mock_reminders.list_reminders.assert_called_once()
        self.assertTrue(result["success"])
        
    def test_list_action_explicit(self):
        """Test explicit list action."""
        self.mock_reminders.list_reminders.return_value = {
            "success": True,
            "reminders": [],
            "count": 0
        }
        
        result = nag_user_with_voice_reminders("list")
        
        self.mock_reminders.list_reminders.assert_called_once()
        self.assertTrue(result["success"])
        
    def test_list_action_with_kwargs_warning(self):
        """Test list action ignores kwargs with warning."""
        self.mock_reminders.list_reminders.return_value = {
            "success": True,
            "reminders": [],
            "count": 0
        }
        
        with patch('builtins.print') as mock_print:
            result = nag_user_with_voice_reminders("list", {"ignored": "param"})
            
        mock_print.assert_called_once()
        self.assertIn("Warning", mock_print.call_args[0][0])
        self.mock_reminders.list_reminders.assert_called_once()
        
    def test_add_action_single_reminder(self):
        """Test adding a single reminder."""
        kwargs = {"text": "Test", "trigger_at": datetime.now() + timedelta(hours=1)}
        self.mock_reminders.add_reminder.return_value = {
            "success": True,
            "reminder_id": "123",
            "message": "Added"
        }
        
        result = nag_user_with_voice_reminders("add", kwargs)
        
        self.mock_reminders.add_reminder.assert_called_once_with(kwargs)
        self.assertTrue(result["success"])
        
    def test_add_action_multiple_reminders(self):
        """Test adding multiple reminders."""
        kwargs_list = [
            {"text": "Test1", "trigger_at": datetime.now() + timedelta(hours=1)},
            {"text": "Test2", "trigger_at": datetime.now() + timedelta(hours=2)}
        ]
        self.mock_reminders.add_reminder.return_value = {"success": True}
        
        result = nag_user_with_voice_reminders("add", kwargs_list)
        
        self.assertEqual(self.mock_reminders.add_reminder.call_count, 2)
        self.assertTrue(result["success"])
        self.assertIn("Added 2 reminders", result["message"])
        
    def test_add_action_no_kwargs(self):
        """Test add action without kwargs raises error."""
        result = nag_user_with_voice_reminders("add", None)
        
        self.assertFalse(result["success"])
        self.assertIn("Missing required parameters", result["error"])
        
    def test_remove_action_single(self):
        """Test removing a single reminder."""
        kwargs = {"date": datetime.now() + timedelta(hours=1)}
        self.mock_reminders.remove_reminder.return_value = {
            "success": True,
            "message": "Removed"
        }
        
        result = nag_user_with_voice_reminders("remove", kwargs)
        
        self.mock_reminders.remove_reminder.assert_called_once_with(kwargs)
        self.assertTrue(result["success"])
        
    def test_remove_action_multiple(self):
        """Test removing multiple reminders."""
        kwargs_list = [
            {"date": datetime.now() + timedelta(hours=1)},
            {"date": datetime.now() + timedelta(hours=2)}
        ]
        self.mock_reminders.remove_reminder.return_value = {"success": True}
        
        result = nag_user_with_voice_reminders("remove", kwargs_list)
        
        self.assertEqual(self.mock_reminders.remove_reminder.call_count, 2)
        self.assertTrue(result["success"])
        self.assertIn("Removed 2 reminders", result["message"])
        
    def test_clear_action(self):
        """Test clear action."""
        self.mock_reminders.clear_reminders.return_value = {
            "success": True,
            "message": "All reminders cleared"
        }
        
        result = nag_user_with_voice_reminders("clear")
        
        self.mock_reminders.clear_reminders.assert_called_once()
        self.assertTrue(result["success"])
        
    def test_clear_action_with_kwargs_warning(self):
        """Test clear action ignores kwargs with warning."""
        self.mock_reminders.clear_reminders.return_value = {
            "success": True,
            "message": "Cleared"
        }
        
        with patch('builtins.print') as mock_print:
            result = nag_user_with_voice_reminders("clear", {"ignored": "param"})
            
        mock_print.assert_called_once()
        self.assertIn("Warning", mock_print.call_args[0][0])
        self.mock_reminders.clear_reminders.assert_called_once()
        
    def test_invalid_action(self):
        """Test invalid action returns error."""
        result = nag_user_with_voice_reminders("invalid_action")
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid action", result["error"])
        
    def test_exception_handling(self):
        """Test exception handling in main function."""
        self.mock_reminders.list_reminders.side_effect = RuntimeError("Test error")
        
        result = nag_user_with_voice_reminders("list")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Test error")


class TestIntegration(unittest.TestCase):
    """Integration tests for the voice reminders system."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the global reminders path
        self.patcher = patch.object(
            _NagUserWithVoiceReminders,
            'reminder_json_path',
            new_callable=unittest.mock.PropertyMock,
            return_value=Path(self.temp_dir) / "_reminders.json"
        )
        self.patcher.start()
        
    def tearDown(self):
        """Clean up."""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('tools.functions.nag_user_with_voice_reminders._reminders')
    def test_full_workflow(self, mock_reminders_global):
        """Test complete workflow: add, list, remove, clear."""
        # Create a real instance for testing
        mock_python_builtins = Mock()
        mock_python_builtins.datetime.datetime = datetime
        mock_python_builtins.json = json
        mock_python_builtins.os = os
        mock_python_builtins.pathlib.Path = Path
        mock_python_builtins.time = time
        mock_python_builtins.tempfile = tempfile
        
        mock_dependencies = Mock()
        
        nag = _NagUserWithVoiceReminders(
            builtins=mock_python_builtins,
            dependencies=mock_dependencies
        )
        
        # Configure the mock to use our real instance
        mock_reminders_global.add_reminder = nag.add_reminder
        mock_reminders_global.list_reminders = nag.list_reminders
        mock_reminders_global.remove_reminder = nag.remove_reminder
        mock_reminders_global.clear_reminders = nag.clear_reminders
        
        # 1. Add reminders
        future_time1 = datetime.now() + timedelta(hours=1)
        future_time2 = datetime.now() + timedelta(hours=2)
        
        result = nag_user_with_voice_reminders("add", {
            "text": "First reminder",
            "trigger_at": future_time1
        })
        self.assertTrue(result["success"])
        
        result = nag_user_with_voice_reminders("add", {
            "text": "Second reminder", 
            "trigger_at": future_time2
        })
        self.assertTrue(result["success"])
        
        # 2. List reminders
        result = nag_user_with_voice_reminders("list")
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["reminders"]), 2)
        
        # 3. Remove one reminder
        result = nag_user_with_voice_reminders("remove", {"date": future_time1})
        self.assertTrue(result["success"])
        
        # 4. List again - should have one
        result = nag_user_with_voice_reminders("list")
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 1)
        
        # 5. Clear all
        result = nag_user_with_voice_reminders("clear")
        self.assertTrue(result["success"])
        
        # 6. List again - should be empty
        result = nag_user_with_voice_reminders("list")
        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 0)


class TestThreadSafety(unittest.TestCase):
    """Test thread safety of the reminder system."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_dependencies = Mock()
        self.mock_dependencies.openai = Mock()
        self.mock_dependencies.playsound = Mock()
        
        self.mock_python_builtins = Mock()
        self.mock_python_builtins.datetime.datetime = datetime
        self.mock_python_builtins.json = json
        self.mock_python_builtins.os = Mock()
        self.mock_python_builtins.pathlib.Path = Path
        self.mock_python_builtins.time = time
        self.mock_python_builtins.tempfile = tempfile
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.json_path = Path(self.temp_dir) / "_reminders.json"
        
        self.patcher = patch.object(
            _NagUserWithVoiceReminders,
            'reminder_json_path',
            new_callable=unittest.mock.PropertyMock,
            return_value=self.json_path
        )
        self.patcher.start()
        
        self.nag = _NagUserWithVoiceReminders(
            builtins=self.mock_python_builtins,
            dependencies=self.mock_dependencies
        )
        
    def tearDown(self):
        """Clean up."""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_concurrent_add_operations(self):
        """Test multiple threads adding reminders concurrently."""
        import concurrent.futures
        
        def add_reminder(i):
            return self.nag.add_reminder({
                "text": f"Reminder {i}",
                "trigger_at": datetime.now() + timedelta(hours=i)
            })
            
        # Run multiple add operations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(add_reminder, i) for i in range(1, 6)]
            results = [f.result() for f in futures]
            
        # All should succeed
        for result in results:
            self.assertTrue(result["success"])
            
        # Should have 5 reminders
        list_result = self.nag.list_reminders()
        self.assertEqual(list_result["count"], 5)
        
    def test_concurrent_read_write_operations(self):
        """Test concurrent read and write operations."""
        import concurrent.futures
        
        # Add initial reminders
        for i in range(3):
            self.nag.add_reminder({
                "text": f"Initial {i}",
                "trigger_at": datetime.now() + timedelta(hours=i+1)
            })
            
        def mixed_operations(i):
            if i % 2 == 0:
                # Even numbers: add
                return self.nag.add_reminder({
                    "text": f"New {i}",
                    "trigger_at": datetime.now() + timedelta(hours=i+10)
                })
            else:
                # Odd numbers: list
                return self.nag.list_reminders()
                
        # Run mixed operations concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(mixed_operations, i) for i in range(10)]
            results = [f.result() for f in futures]
            
        # All operations should complete successfully
        for result in results:
            self.assertTrue(result["success"])
            
        # Final count should be initial 3 + 5 new (even numbers 0,2,4,6,8)
        final_list = self.nag.list_reminders()
        self.assertEqual(final_list["count"], 8)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_reminder_with_empty_text(self):
        """Test reminder with empty text after stripping."""
        with self.assertRaises(ValidationError):
            _Reminder(
                text="   ",  # Only whitespace
                trigger_at=datetime.now() + timedelta(hours=1)
            )
            
    def test_reminder_with_very_long_text(self):
        """Test reminder with text at the limit."""
        long_text = "a" * 20000  # At the limit mentioned in docstring
        reminder = _Reminder(
            text=long_text,
            trigger_at=datetime.now() + timedelta(hours=1)
        )
        self.assertEqual(len(reminder.text), 20000)
        
    def test_cache_boundary_conditions(self):
        """Test cache at max capacity."""
        cache = _ReminderCache()
        cache._max_size = 3  # Small size for testing
        
        # Fill to capacity
        for i in range(3):
            time_key = datetime.now() + timedelta(hours=i+1)
            reminder = _Reminder(text=f"R{i}", trigger_at=time_key)
            cache.put(time_key, reminder)
            
        self.assertTrue(cache.full())
        self.assertEqual(cache.qsize(), 3)
        
        # Adding one more should still work (no enforcement in current implementation)
        time_key = datetime.now() + timedelta(hours=4)
        reminder = _Reminder(text="R4", trigger_at=time_key)
        cache.put(time_key, reminder)
        self.assertEqual(cache.qsize(), 4)
        
    def test_json_serialization_with_special_characters(self):
        """Test JSON serialization with special characters in text."""
        mock_python_builtins = Mock()
        mock_python_builtins.datetime.datetime = datetime
        mock_python_builtins.json = json
        mock_python_builtins.os = Mock()
        mock_python_builtins.pathlib.Path = Path
        mock_python_builtins.time = time
        
        mock_dependencies = Mock()
        
        temp_dir = tempfile.mkdtemp()
        json_path = Path(temp_dir) / "_reminders.json"
        
        with patch.object(
            _NagUserWithVoiceReminders,
            'reminder_json_path',
            new_callable=unittest.mock.PropertyMock,
            return_value=json_path
        ):
            nag = _NagUserWithVoiceReminders(
                builtins=mock_python_builtins,
                dependencies=mock_dependencies
            )
            
            # Add reminder with special characters
            special_text = 'Test with "quotes" and \n newlines and émojis 🎉'
            result = nag.add_reminder({
                "text": special_text,
                "trigger_at": datetime.now() + timedelta(hours=1)
            })
            
            self.assertTrue(result["success"])
            
            # Verify it saves and loads correctly
            nag.save_reminders()
            
            # Create new instance to load
            nag2 = _NagUserWithVoiceReminders(
                builtins=mock_python_builtins,
                dependencies=mock_dependencies
            )
            
            list_result = nag2.list_reminders()
            self.assertEqual(list_result["count"], 1)
            self.assertEqual(list_result["reminders"][0]["text"], special_text)
            
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestDateTimeHandling(unittest.TestCase):
    """Test datetime handling and timezone issues."""
    
    def test_datetime_string_conversion(self):
        """Test conversion between datetime and ISO string format."""
        mock_python_builtins = Mock()
        mock_python_builtins.datetime.datetime = datetime
        mock_python_builtins.json = json
        mock_python_builtins.os = Mock()
        mock_python_builtins.pathlib.Path = Path
        mock_python_builtins.time = time
        
        mock_dependencies = Mock()
        
        temp_dir = tempfile.mkdtemp()
        json_path = Path(temp_dir) / "_reminders.json"
        
        with patch.object(
            _NagUserWithVoiceReminders,
            'reminder_json_path', 
            new_callable=unittest.mock.PropertyMock,
            return_value=json_path
        ):
            nag = _NagUserWithVoiceReminders(
                builtins=mock_python_builtins,
                dependencies=mock_dependencies
            )
            
            # Add reminder with specific future datetime
            test_time = datetime(2030, 12, 25, 15, 30, 45, 123456) # 2030 is a future year
            nag.add_reminder({
                "text": "Test",
                "trigger_at": test_time
            })
            
            # Save and check JSON format
            nag.save_reminders()
            
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            # Should have ISO format string as key
            iso_keys = list(data["reminders"].keys())
            self.assertEqual(len(iso_keys), 1)
            
            # Parse back and compare
            parsed_time = datetime.fromisoformat(iso_keys[0])
            self.assertEqual(parsed_time, test_time)
            
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    def test_expired_reminders_filtered_on_save(self):
        """Test that expired reminders are filtered out when saving."""
        with patch('tools.functions.nag_user_with_voice_reminders.python_builtins.time.time') as mock_time:
            current_timestamp = datetime.now().timestamp()
            mock_time.time.return_value = current_timestamp
            
            mock_python_builtins = Mock()
            mock_python_builtins.datetime.datetime = datetime
            mock_python_builtins.json = json
            mock_python_builtins.os = Mock()
            mock_python_builtins.pathlib.Path = Path
            mock_python_builtins.time = time
            
            mock_dependencies = Mock()
            
            temp_dir = tempfile.mkdtemp()
            json_path = Path(temp_dir) / "_reminders.json"
            
            with patch.object(
                _NagUserWithVoiceReminders,
                'reminder_json_path',
                new_callable=unittest.mock.PropertyMock,
                return_value=json_path
            ):
                nag = _NagUserWithVoiceReminders(
                    builtins=mock_python_builtins,
                    dependencies=mock_dependencies
                )
                
                # Add only future reminders
                future_time1 = datetime.fromtimestamp(current_timestamp + 1800)  # 30 min future
                future_time2 = datetime.fromtimestamp(current_timestamp + 3600)  # 1 hour future
                
                reminder1 = _Reminder(text="Soon", trigger_at=future_time1)
                reminder2 = _Reminder(text="Later", trigger_at=future_time2)
                
                nag.reminder_cache.put(future_time1, reminder1)
                nag.reminder_cache.put(future_time2, reminder2)
                
                # Move time forward so first reminder is expired
                mock_time.return_value = current_timestamp + 2700  # 45 min later
                
                # Save - should filter out the expired one
                nag.save_reminders()
                
                # Check that only the non-expired reminder was saved
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                self.assertEqual(len(data["reminders"]), 1)  # Only reminder2 remains
                
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()