#!/usr/bin/env python3
"""
Test script dla compliance, bezpieczeństwa i audytowalności.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.compliance_security import (
    ComplianceManager, UserRole, EventType, SecurityLevel,
    CryptoManager, UserManager, AuditLogger, AccessControlManager
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_crypto_manager():
    """Test menedżera szyfrowania."""
    print("🧪 Testing Crypto Manager...")
    
    crypto = CryptoManager()
    
    # Test hash generation
    test_data = "test data for hashing"
    hash_value = crypto.generate_hash(test_data)
    assert len(hash_value) == 64  # SHA256 produces 64 character hex string
    print("✅ Hash generation works")
    
    # Test hash verification
    assert crypto.verify_hash(test_data, hash_value) == True
    assert crypto.verify_hash("different data", hash_value) == False
    print("✅ Hash verification works")
    
    # Test HMAC generation
    hmac_value = crypto.generate_hmac(test_data)
    assert len(hmac_value) == 64
    print("✅ HMAC generation works")
    
    # Test HMAC verification
    assert crypto.verify_hmac(test_data, hmac_value) == True
    assert crypto.verify_hmac("different data", hmac_value) == False
    print("✅ HMAC verification works")
    
    # Test encryption/decryption
    encrypted = crypto.encrypt_data(test_data)
    assert encrypted.startswith("encrypted:")
    print("✅ Data encryption works")
    
    decrypted = crypto.decrypt_data(encrypted)
    assert decrypted == test_data
    print("✅ Data decryption works")
    
    print("✅ All crypto manager tests passed!")


def test_user_manager():
    """Test menedżera użytkowników."""
    print("\n🧪 Testing User Manager...")
    
    # Use temporary database for testing
    test_db = Path("/tmp/test_users.db")
    if test_db.exists():
        test_db.unlink()
    
    user_manager = UserManager(test_db)
    
    # Test user creation
    user = user_manager.create_user(
        username="test_auditor",
        email="auditor@test.com",
        role=UserRole.AUDITOR,
        security_level=SecurityLevel.MEDIUM
    )
    
    assert user.username == "test_auditor"
    assert user.email == "auditor@test.com"
    assert user.role == UserRole.AUDITOR
    assert user.security_level == SecurityLevel.MEDIUM
    assert user.is_active == True
    print("✅ User creation works")
    
    # Test user retrieval
    retrieved_user = user_manager.get_user(user.id)
    assert retrieved_user is not None
    assert retrieved_user.username == "test_auditor"
    print("✅ User retrieval works")
    
    # Test user retrieval by username
    retrieved_user = user_manager.get_user_by_username("test_auditor")
    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    print("✅ User retrieval by username works")
    
    # Test login update
    user_manager.update_user_login(user.id)
    updated_user = user_manager.get_user(user.id)
    assert updated_user.last_login is not None
    print("✅ Login update works")
    
    # Test different roles
    senior_user = user_manager.create_user(
        username="test_senior",
        email="senior@test.com",
        role=UserRole.SENIOR
    )
    assert senior_user.role == UserRole.SENIOR
    print("✅ Different roles work")
    
    # Cleanup
    test_db.unlink()
    print("✅ All user manager tests passed!")


def test_audit_logger():
    """Test loggera zdarzeń audytowych."""
    print("\n🧪 Testing Audit Logger...")
    
    # Use temporary database for testing
    test_db = Path("/tmp/test_audit.db")
    if test_db.exists():
        test_db.unlink()
    
    audit_logger = AuditLogger(test_db)
    
    # Create test user
    test_user = type('MockUser', (), {
        'id': 'test_user_id',
        'username': 'test_user',
        'role': UserRole.AUDITOR
    })()
    
    # Test event logging
    event = audit_logger.log_event(
        user=test_user,
        event_type=EventType.LOGIN,
        description="Test login event",
        ip_address="192.168.1.1",
        user_agent="Test Browser",
        security_level=SecurityLevel.MEDIUM
    )
    
    assert event.id is not None
    assert event.user_id == "test_user_id"
    assert event.event_type == EventType.LOGIN
    assert event.description == "Test login event"
    assert event.hash_signature is not None
    print("✅ Event logging works")
    
    # Test event retrieval
    events = audit_logger.get_events(user_id="test_user_id", limit=10)
    assert len(events) == 1
    assert events[0].id == event.id
    print("✅ Event retrieval works")
    
    # Test event integrity verification
    assert audit_logger.verify_event_integrity(event) == True
    print("✅ Event integrity verification works")
    
    # Test different event types
    audit_logger.log_event(
        user=test_user,
        event_type=EventType.UPLOAD,
        description="Test upload event",
        resource_id="file_123",
        resource_type="pdf"
    )
    
    events = audit_logger.get_events(limit=10)
    assert len(events) == 2
    print("✅ Multiple event types work")
    
    # Cleanup
    test_db.unlink()
    print("✅ All audit logger tests passed!")


def test_access_control():
    """Test kontroli dostępu."""
    print("\n🧪 Testing Access Control...")
    
    # Use temporary database for testing
    test_db = Path("/tmp/test_access.db")
    if test_db.exists():
        test_db.unlink()
    
    access_control = AccessControlManager(test_db)
    
    # Test access control creation with restrictive permissions
    restrictive_permissions = {
        UserRole.AUDITOR: ['view'],  # Only view permission
        UserRole.SENIOR: ['view', 'download'],
        UserRole.PARTNER: ['view', 'download', 'modify'],
        UserRole.CLIENT_PBC: [],  # No permissions
        UserRole.ADMIN: ['*']
    }
    
    ac = access_control.create_access_control(
        resource_id="resource_123",
        resource_type="audit_report",
        owner_id="owner_123",
        permissions=restrictive_permissions
    )
    
    assert ac.resource_id == "resource_123"
    assert ac.resource_type == "audit_report"
    assert ac.owner_id == "owner_123"
    assert ac.version == 1
    print("✅ Access control creation works")
    
    # Test permission checking
    test_user = type('MockUser', (), {
        'id': 'owner_123',
        'role': UserRole.AUDITOR
    })()
    
    # Owner should have access
    assert access_control.check_permission(test_user, "resource_123", "view") == True
    print("✅ Owner permission check works")
    
    # Non-owner with no permissions should not have access
    test_user.id = "other_user"
    test_user.role = UserRole.CLIENT_PBC  # Role with no permissions
    assert access_control.check_permission(test_user, "resource_123", "view") == False
    print("✅ Non-owner permission check works")
    
    # Test role-based permissions
    test_user.role = UserRole.ADMIN
    assert access_control.check_permission(test_user, "resource_123", "view") == True
    print("✅ Role-based permission check works")
    
    # Cleanup
    test_db.unlink()
    print("✅ All access control tests passed!")


def test_compliance_manager():
    """Test menedżera compliance."""
    print("\n🧪 Testing Compliance Manager...")
    
    # Use temporary directory for testing
    test_dir = Path("/tmp/test_compliance")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    compliance = ComplianceManager(test_dir)
    
    # Test user creation
    user = compliance.create_user(
        username="compliance_test",
        email="compliance@test.com",
        role=UserRole.AUDITOR
    )
    
    assert user.username == "compliance_test"
    assert user.role == UserRole.AUDITOR
    print("✅ User creation through compliance manager works")
    
    # Test user authentication
    authenticated_user = compliance.authenticate_user("compliance_test")
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    print("✅ User authentication works")
    
    # Test authorization
    assert compliance.authorize_action(user, "resource_123", "view") == False  # No access control set
    print("✅ Authorization works")
    
    # Test action logging
    compliance.log_user_action(
        user=user,
        event_type=EventType.UPLOAD,
        description="Test upload action",
        resource_id="file_123",
        resource_type="pdf"
    )
    print("✅ Action logging works")
    
    # Test audit trail
    events = compliance.get_audit_trail(user_id=user.id, limit=10)
    assert len(events) >= 2  # Login + upload events
    print("✅ Audit trail retrieval works")
    
    # Test data integrity
    test_data = "test data for integrity"
    hash_value = compliance.crypto_manager.generate_hash(test_data)
    assert compliance.verify_data_integrity(test_data, hash_value) == True
    print("✅ Data integrity verification works")
    
    # Test encryption/decryption
    encrypted = compliance.encrypt_sensitive_data(test_data)
    decrypted = compliance.decrypt_sensitive_data(encrypted)
    assert decrypted == test_data
    print("✅ Sensitive data encryption/decryption works")
    
    # Test compliance summary
    summary = compliance.get_compliance_summary()
    assert 'total_events' in summary
    assert 'events_by_type' in summary
    assert 'events_by_user' in summary
    assert 'events_by_security_level' in summary
    print("✅ Compliance summary works")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("✅ All compliance manager tests passed!")


def test_security_levels():
    """Test poziomów bezpieczeństwa."""
    print("\n🧪 Testing Security Levels...")
    
    # Test all security levels
    levels = [SecurityLevel.LOW, SecurityLevel.MEDIUM, SecurityLevel.HIGH, SecurityLevel.CRITICAL]
    
    for level in levels:
        assert level.value in ['low', 'medium', 'high', 'critical']
        print(f"✅ Security level {level.value} works")
    
    print("✅ All security level tests passed!")


def test_user_roles():
    """Test ról użytkowników."""
    print("\n🧪 Testing User Roles...")
    
    # Test all user roles
    roles = [UserRole.AUDITOR, UserRole.SENIOR, UserRole.PARTNER, UserRole.CLIENT_PBC, UserRole.ADMIN]
    
    for role in roles:
        assert role.value in ['auditor', 'senior', 'partner', 'client_pbc', 'admin']
        print(f"✅ User role {role.value} works")
    
    print("✅ All user role tests passed!")


def test_event_types():
    """Test typów zdarzeń."""
    print("\n🧪 Testing Event Types...")
    
    # Test all event types
    event_types = [
        EventType.LOGIN, EventType.LOGOUT, EventType.UPLOAD, EventType.AUDIT_START,
        EventType.AUDIT_COMPLETE, EventType.AUDIT_FAIL, EventType.EXPORT,
        EventType.DELETE, EventType.MODIFY, EventType.VIEW, EventType.APPROVE, EventType.REJECT
    ]
    
    for event_type in event_types:
        assert event_type.value in [
            'login', 'logout', 'upload', 'audit_start', 'audit_complete',
            'audit_fail', 'export', 'delete', 'modify', 'view', 'approve', 'reject'
        ]
        print(f"✅ Event type {event_type.value} works")
    
    print("✅ All event type tests passed!")


def test_workflow():
    """Test przepływu pracy compliance."""
    print("\n🧪 Testing Compliance Workflow...")
    
    # Use temporary directory for testing
    test_dir = Path("/tmp/test_workflow")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    compliance = ComplianceManager(test_dir)
    
    # 1. Create users
    auditor = compliance.create_user("auditor1", "auditor1@test.com", UserRole.AUDITOR)
    senior = compliance.create_user("senior1", "senior1@test.com", UserRole.SENIOR)
    partner = compliance.create_user("partner1", "partner1@test.com", UserRole.PARTNER)
    
    print("✅ Step 1: Users created")
    
    # 2. Authenticate users
    auth_auditor = compliance.authenticate_user("auditor1")
    auth_senior = compliance.authenticate_user("senior1")
    auth_partner = compliance.authenticate_user("partner1")
    
    assert auth_auditor is not None
    assert auth_senior is not None
    assert auth_partner is not None
    print("✅ Step 2: Users authenticated")
    
    # 3. Log various actions
    compliance.log_user_action(auditor, EventType.UPLOAD, "Uploaded audit files")
    compliance.log_user_action(senior, EventType.AUDIT_START, "Started audit process")
    compliance.log_user_action(partner, EventType.APPROVE, "Approved audit results")
    
    print("✅ Step 3: Actions logged")
    
    # 4. Check audit trail
    all_events = compliance.get_audit_trail(limit=100)
    assert len(all_events) >= 6  # 3 logins + 3 actions
    print("✅ Step 4: Audit trail verified")
    
    # 5. Test data integrity
    test_data = "sensitive audit data"
    encrypted = compliance.encrypt_sensitive_data(test_data)
    decrypted = compliance.decrypt_sensitive_data(encrypted)
    assert decrypted == test_data
    print("✅ Step 5: Data integrity verified")
    
    # 6. Generate compliance summary
    summary = compliance.get_compliance_summary()
    assert summary['total_events'] >= 6
    assert 'login' in summary['events_by_type']
    assert 'upload' in summary['events_by_type']
    print("✅ Step 6: Compliance summary generated")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("✅ Complete compliance workflow test passed!")


def main():
    """Main test function."""
    print("🚀 Starting Compliance & Security Tests...")
    
    try:
        test_crypto_manager()
        test_user_manager()
        test_audit_logger()
        test_access_control()
        test_compliance_manager()
        test_security_levels()
        test_user_roles()
        test_event_types()
        test_workflow()
        
        print("\n🎉 All Compliance & Security tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
