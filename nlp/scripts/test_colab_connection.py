"""
Test connection to Colab tunnel from local terminal

Usage:
    python nlp/scripts/test_colab_connection.py
"""

import requests
import os
from pathlib import Path

def test_colab_connection():
    """Test if we can reach Colab through the tunnel"""
    
    # Load tunnel URL from config
    config_path = Path(__file__).parent.parent.parent / ".colab_config"
    
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                if line.startswith('COLAB_TUNNEL_URL='):
                    tunnel_url = line.split('=')[1].strip()
                    break
    else:
        tunnel_url = input("Enter Colab tunnel URL: ").strip()
    
    print("=" * 80)
    print("🔗 Testing Colab Tunnel Connection")
    print("=" * 80)
    print(f"\nTunnel URL: {tunnel_url}\n")
    
    # Test basic connectivity
    try:
        print("📡 Testing connection...")
        response = requests.get(tunnel_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Successfully connected to Colab!")
            print(f"   Status code: {response.status_code}")
            print(f"   Response length: {len(response.content)} bytes")
        else:
            print(f"⚠️  Connected but got status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - tunnel may not be running")
        print("   Make sure Colab is running and tunnel is active")
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("💡 Next Steps:")
    print("=" * 80)
    print("  1. Make sure Colab notebook is running")
    print("  2. Verify tunnel URL is correct")
    print("  3. If testing API, try: curl " + tunnel_url + "/health")
    print("\n")

if __name__ == "__main__":
    test_colab_connection()
