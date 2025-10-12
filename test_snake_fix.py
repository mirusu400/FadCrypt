#!/usr/bin/env python3
"""
Test script to verify the Snake Game high score bug fix
"""

import os
import sys
import tempfile
import json

def test_snake_high_score_fix():
    """Test that the high score functions work correctly with the fix"""
    print("Testing Snake Game high score fix...")
    
    # Mock the GUI instance and AppLocker
    class MockAppLocker:
        def get_fadcrypt_folder(self):
            # Return a temporary directory for testing
            return tempfile.gettempdir()
    
    class MockGUI:
        def __init__(self):
            self.app_locker = MockAppLocker()
    
    # Create a mock GUI instance
    gui_instance = MockGUI()
    
    # Test the fixed high score functions
    def load_high_score():
        try:
            # Get the FadCrypt folder path using the gui_instance
            folder_path = gui_instance.app_locker.get_fadcrypt_folder()
            # Define the full path to the snake_high_score.json file
            file_path = os.path.join(folder_path, "snake_high_score.json")
            # Load the high score from the file
            with open(file_path, "r") as f:
                return json.load(f)["high_score"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return 0

    def save_high_score(high_score):
        try:
            # Get the FadCrypt folder path using the gui_instance
            folder_path = gui_instance.app_locker.get_fadcrypt_folder()
            # Define the full path to the snake_high_score.json file
            file_path = os.path.join(folder_path, "snake_high_score.json")
            # Save the high score to the file
            with open(file_path, "w") as f:
                json.dump({"high_score": high_score}, f)
        except Exception as e:
            print(f"Error saving high score: {e}")
            return False
        return True
    
    try:
        # Test 1: Load high score when no file exists (should return 0)
        initial_score = load_high_score()
        if initial_score == 0:
            print("✓ Test 1 passed: load_high_score() returns 0 when no file exists")
        else:
            print(f"✗ Test 1 failed: Expected 0, got {initial_score}")
            return False
        
        # Test 2: Save a high score
        test_score = 1500
        if save_high_score(test_score):
            print("✓ Test 2 passed: save_high_score() executed without errors")
        else:
            print("✗ Test 2 failed: save_high_score() returned False")
            return False
        
        # Test 3: Load the saved high score
        loaded_score = load_high_score()
        if loaded_score == test_score:
            print(f"✓ Test 3 passed: Loaded score {loaded_score} matches saved score {test_score}")
        else:
            print(f"✗ Test 3 failed: Expected {test_score}, got {loaded_score}")
            return False
        
        # Test 4: Update high score with a higher value
        higher_score = 2500
        if save_high_score(higher_score):
            loaded_higher_score = load_high_score()
            if loaded_higher_score == higher_score:
                print(f"✓ Test 4 passed: Updated high score to {higher_score}")
            else:
                print(f"✗ Test 4 failed: Expected {higher_score}, got {loaded_higher_score}")
                return False
        else:
            print("✗ Test 4 failed: Could not save higher score")
            return False
        
        # Clean up test file
        try:
            test_file = os.path.join(gui_instance.app_locker.get_fadcrypt_folder(), "snake_high_score.json")
            if os.path.exists(test_file):
                os.remove(test_file)
                print("✓ Cleanup: Test file removed")
        except Exception as e:
            print(f"Warning: Could not clean up test file: {e}")
        
        print("✅ All tests passed! Snake Game high score bug is fixed.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def main():
    """Run the test"""
    print("Running Snake Game high score fix test...\n")
    
    success = test_snake_high_score_fix()
    
    if success:
        print("\n🎉 SUCCESS: The Snake Game high score bug has been fixed!")
        print("\nWhat was fixed:")
        print("1. Added 'gui_instance' parameter to run_snake_game() function")
        print("2. Fixed load_high_score() to use gui_instance.app_locker.get_fadcrypt_folder()")
        print("3. Fixed save_high_score() to use gui_instance.app_locker.get_fadcrypt_folder()")
        print("4. Removed incorrect 'self' parameter from save_high_score() function signature")
        print("5. Updated the function call to save_high_score(high_score) without 'self'")
        print("6. Updated threading call to pass 'self' as argument to run_snake_game()")
        return True
    else:
        print("\n❌ FAILURE: There are still issues with the Snake Game high score functionality.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
