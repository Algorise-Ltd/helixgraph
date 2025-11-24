"""
Environment Test Script for HEL-21 NER Module

This script verifies that all dependencies are correctly installed
and the NER training environment is ready.

Usage:
    python nlp/scripts/test_environment.py
"""

import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_check(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {name}")
    if details:
        print(f"       {details}")


def test_python_version():
    """Check Python version is 3.8+"""
    print_header("Testing Python Version")
    version = sys.version_info
    passed = version >= (3, 8)
    print_check(
        "Python Version",
        passed,
        f"Found: {version.major}.{version.minor}.{version.micro}"
    )
    return passed


def test_core_packages():
    """Test if core packages are installed"""
    print_header("Testing Core Packages")
    
    packages = {
        "spacy": "3.7.0",
        "sklearn": "scikit-learn",
        "matplotlib": "3.8.0",
        "seaborn": "0.13.0",
    }
    
    all_passed = True
    
    for package, expected in packages.items():
        try:
            if package == "sklearn":
                import sklearn
                version = sklearn.__version__
                name = "scikit-learn"
            else:
                module = __import__(package)
                version = module.__version__
                name = package
            
            print_check(name, True, f"Version: {version}")
        except ImportError:
            print_check(name, False, f"Not installed! Run: pip install {expected}")
            all_passed = False
    
    return all_passed


def test_spacy_models():
    """Test if spaCy models are downloaded"""
    print_header("Testing spaCy Models")
    
    try:
        import spacy
        
        # Test if transformer model is available
        try:
            nlp = spacy.load("en_core_web_trf")
            print_check(
                "en_core_web_trf",
                True,
                f"Loaded successfully ({len(nlp.pipe_names)} components)"
            )
            
            # Test basic NER functionality
            doc = nlp("Apple Inc. is based in Cupertino.")
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            print(f"       Test entities found: {entities}")
            
            return True
            
        except OSError:
            print_check(
                "en_core_web_trf",
                False,
                "Not installed! Run: python -m spacy download en_core_web_trf"
            )
            return False
            
    except ImportError:
        print_check("spacy", False, "spaCy not installed!")
        return False


def test_transformers():
    """Test if transformers library is available"""
    print_header("Testing Transformers Support")
    
    try:
        import spacy_transformers
        # Try to get version, but don't fail if not available
        try:
            version = spacy_transformers.__version__
            version_str = f"Version: {version}"
        except AttributeError:
            version_str = "Installed (version check not available)"
        
        print_check(
            "spacy-transformers",
            True,
            version_str
        )
        return True
    except ImportError:
        print_check(
            "spacy-transformers",
            False,
            "Not installed! Should be installed with spacy[transformers]"
        )
        return False


def test_directory_structure():
    """Test if required directories exist"""
    print_header("Testing Directory Structure")
    
    base_path = Path(__file__).parent.parent
    required_dirs = [
        "configs",
        "training_data",
        "training_data/raw",
        "training_data/processed",
        "models",
        "evaluation",
        "scripts",
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        exists = dir_path.exists()
        print_check(f"nlp/{dir_name}", exists)
        if not exists:
            all_exist = False
    
    return all_exist


def test_config_file():
    """Test if spaCy config file exists"""
    print_header("Testing Configuration Files")
    
    base_path = Path(__file__).parent.parent
    config_path = base_path / "configs" / "config.cfg"
    
    exists = config_path.exists()
    print_check("config.cfg", exists)
    
    if exists:
        # Check if it's a valid config
        try:
            import spacy
            config = spacy.util.load_config(config_path)
            print(f"       Config sections: {list(config.keys())}")
            return True
        except Exception as e:
            print_check("config.cfg validation", False, f"Error: {e}")
            return False
    
    return exists


def test_fuzzy_matching():
    """Test fuzzy matching library for entity linking"""
    print_header("Testing Fuzzy Matching (for Entity Linking)")
    
    try:
        from fuzzywuzzy import fuzz
        
        # Test basic fuzzy matching
        score = fuzz.ratio("Acme Corp", "Acme Corporation")
        print_check(
            "fuzzywuzzy",
            True,
            f"Match score 'Acme Corp' vs 'Acme Corporation': {score}"
        )
        return True
        
    except ImportError:
        print_check(
            "fuzzywuzzy",
            False,
            "Not installed! Run: pip install fuzzywuzzy python-Levenshtein"
        )
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  HEL-21 NER Environment Test Suite")
    print("  Testing environment setup for Phase 1")
    print("="*60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Core Packages", test_core_packages),
        ("spaCy Models", test_spacy_models),
        ("Transformers", test_transformers),
        ("Directory Structure", test_directory_structure),
        ("Config File", test_config_file),
        ("Fuzzy Matching", test_fuzzy_matching),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results[name] = False
    
    # Summary
    print_header("Test Summary")
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    # Final verdict
    if passed == total:
        print("\n" + "="*60)
        print("  ✅ SUCCESS! Training environment is working correctly.")
        print("="*60)
        print("\n🎉 You're ready to move to Phase 2: Training Data Preparation!")
        print("\nNext steps:")
        print("  1. Collect entity vocabulary from teammates")
        print("  2. Create training sentences (800+)")
        print("  3. Annotate entities in JSON format")
        return 0
    else:
        print("\n" + "="*60)
        print("  ❌ FAILED! Some components need attention.")
        print("="*60)
        print("\n⚠️  Please fix the failed tests above before proceeding.")
        print("\nCommon fixes:")
        print("  - Missing packages: pip install -r requirements.txt")
        print("  - Missing spaCy model: python -m spacy download en_core_web_trf")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
