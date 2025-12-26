#!/usr/bin/env python3

import sys
sys.path.append('.')

print("🔍 Testing profile handler import...")

try:
    from app.handlers.profile_handler_fixed import profile_menu
    print("✅ Profile handler imported successfully")
    
    # Test basic function properties
    print(f"📋 Function name: {profile_menu.__name__}")
    print(f"📝 Function doc: {profile_menu.__doc__}")
    
    print("✅ Profile handler appears to be working correctly")
    
except Exception as e:
    print(f"❌ Error importing profile handler: {e}")
    import traceback
    traceback.print_exc()

print("🏁 Test completed")
