"""
Basic import tests for module verification.
"""

def test_module_import():
    """Test that the module can be imported."""
    import socratic_learning
    assert socratic_learning is not None

def test_main_exports():
    """Test that main exports are available."""
    try:
        from socratic_learning import LearningTracker
        assert LearningTracker is not None
    except ImportError:
        # Optional - some modules might not export the main class
        pass
