"""
Compliance, bezpieczeństwo, audytowalność.
System ról, dziennik zdarzeń, szyfrowanie, kontrola dostępu.
"""

import json
import logging
import hashlib
import hmac
import secrets
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid

from .exceptions import SecurityError, AuthorizationError, AuditError


class UserRole(Enum):
    """Role użytkowników."""
    AUDITOR = "auditor"
    SENIOR = "senior"
    PARTNER = "partner"
    CLIENT_PBC = "client_pbc"
    ADMIN = "admin"


class EventType(Enum):
    """Typy zdarzeń."""
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    AUDIT_START = "audit_start"
    AUDIT_COMPLETE = "audit_complete"
    AUDIT_FAIL = "audit_fail"
    EXPORT = "export"
    DELETE = "delete"
    MODIFY = "modify"
    VIEW = "view"
    APPROVE = "approve"
    REJECT = "reject"


class SecurityLevel(Enum):
    """Poziomy bezpieczeństwa."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class User:
    """Użytkownik systemu."""
    id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    permissions: List[str]
    security_level: SecurityLevel


@dataclass
class AuditEvent:
    """Zdarzenie audytowe."""
    id: str
    user_id: str
    username: str
    event_type: EventType
    description: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    resource_id: Optional[str]
    resource_type: Optional[str]
    details: Dict[str, Any]
    security_level: SecurityLevel
    hash_signature: str


@dataclass
class AccessControl:
    """Kontrola dostępu."""
    resource_id: str
    resource_type: str
    owner_id: str
    permissions: Dict[UserRole, List[str]]
    created_at: datetime
    modified_at: datetime
    version: int


@dataclass
class SecurityPolicy:
    """Polityka bezpieczeństwa."""
    id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    created_at: datetime
    modified_at: datetime
    is_active: bool


class CryptoManager:
    """Menedżer szyfrowania."""
    
    def __init__(self, secret_key: str = None):
        if secret_key is None:
            secret_key = secrets.token_hex(32)
        self.secret_key = secret_key.encode()
        self.logger = logging.getLogger(__name__)
    
    def generate_hash(self, data: str) -> str:
        """Generowanie hash z danych."""
        try:
            hash_obj = hashlib.sha256(data.encode())
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"Hash generation failed: {e}")
            raise SecurityError(f"Hash generation failed: {e}")
    
    def generate_hmac(self, data: str) -> str:
        """Generowanie HMAC z danych."""
        try:
            hmac_obj = hmac.new(self.secret_key, data.encode(), hashlib.sha256)
            return hmac_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"HMAC generation failed: {e}")
            raise SecurityError(f"HMAC generation failed: {e}")
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Weryfikacja hash."""
        try:
            expected_hash = self.generate_hash(data)
            return hmac.compare_digest(expected_hash, hash_value)
        except Exception as e:
            self.logger.error(f"Hash verification failed: {e}")
            return False
    
    def verify_hmac(self, data: str, hmac_value: str) -> bool:
        """Weryfikacja HMAC."""
        try:
            expected_hmac = self.generate_hmac(data)
            return hmac.compare_digest(expected_hmac, hmac_value)
        except Exception as e:
            self.logger.error(f"HMAC verification failed: {e}")
            return False
    
    def encrypt_data(self, data: str) -> str:
        """Szyfrowanie danych (mock implementation)."""
        try:
            # Mock encryption - in real implementation, use proper encryption
            encoded = base64.b64encode(data.encode()).decode()
            return f"encrypted:{encoded}"
        except Exception as e:
            self.logger.error(f"Data encryption failed: {e}")
            raise SecurityError(f"Data encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Odszyfrowanie danych (mock implementation)."""
        try:
            if not encrypted_data.startswith("encrypted:"):
                raise SecurityError("Invalid encrypted data format")
            
            encoded = encrypted_data[10:]  # Remove "encrypted:" prefix
            decoded = base64.b64decode(encoded).decode()
            return decoded
        except Exception as e:
            self.logger.error(f"Data decryption failed: {e}")
            raise SecurityError(f"Data decryption failed: {e}")


class UserManager:
    """Menedżer użytkowników."""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path.home() / '.ai-auditor' / 'compliance' / 'users.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicjalizacja bazy danych."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        role TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_login TEXT,
                        is_active BOOLEAN NOT NULL,
                        permissions TEXT NOT NULL,
                        security_level TEXT NOT NULL
                    )
                """)
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise SecurityError(f"Database initialization failed: {e}")
    
    def create_user(self, username: str, email: str, role: UserRole, 
                   permissions: List[str] = None, security_level: SecurityLevel = SecurityLevel.MEDIUM) -> User:
        """Tworzenie użytkownika."""
        try:
            if permissions is None:
                permissions = self._get_default_permissions(role)
            
            user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                role=role,
                created_at=datetime.now(),
                last_login=None,
                is_active=True,
                permissions=permissions,
                security_level=security_level
            )
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users (id, username, email, role, created_at, 
                                     last_login, is_active, permissions, security_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.id, user.username, user.email, user.role.value,
                    user.created_at.isoformat(), user.last_login.isoformat() if user.last_login else None,
                    user.is_active, json.dumps(user.permissions), user.security_level.value
                ))
                conn.commit()
            
            self.logger.info(f"User created: {username} ({role.value})")
            return user
            
        except Exception as e:
            self.logger.error(f"User creation failed: {e}")
            raise SecurityError(f"User creation failed: {e}")
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Pobieranie użytkownika."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, username, email, role, created_at, last_login,
                           is_active, permissions, security_level
                    FROM users WHERE id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        role=UserRole(row[3]),
                        created_at=datetime.fromisoformat(row[4]),
                        last_login=datetime.fromisoformat(row[5]) if row[5] else None,
                        is_active=bool(row[6]),
                        permissions=json.loads(row[7]),
                        security_level=SecurityLevel(row[8])
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"User retrieval failed: {e}")
            raise SecurityError(f"User retrieval failed: {e}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Pobieranie użytkownika po nazwie."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, username, email, role, created_at, last_login,
                           is_active, permissions, security_level
                    FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        role=UserRole(row[3]),
                        created_at=datetime.fromisoformat(row[4]),
                        last_login=datetime.fromisoformat(row[5]) if row[5] else None,
                        is_active=bool(row[6]),
                        permissions=json.loads(row[7]),
                        security_level=SecurityLevel(row[8])
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"User retrieval failed: {e}")
            raise SecurityError(f"User retrieval failed: {e}")
    
    def update_user_login(self, user_id: str):
        """Aktualizacja ostatniego logowania."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE users SET last_login = ? WHERE id = ?
                """, (datetime.now().isoformat(), user_id))
                conn.commit()
        except Exception as e:
            self.logger.error(f"User login update failed: {e}")
            raise SecurityError(f"User login update failed: {e}")
    
    def _get_default_permissions(self, role: UserRole) -> List[str]:
        """Pobieranie domyślnych uprawnień dla roli."""
        permissions_map = {
            UserRole.AUDITOR: ['view', 'upload', 'audit', 'export_basic'],
            UserRole.SENIOR: ['view', 'upload', 'audit', 'export_basic', 'export_advanced', 'approve'],
            UserRole.PARTNER: ['view', 'upload', 'audit', 'export_basic', 'export_advanced', 'approve', 'admin'],
            UserRole.CLIENT_PBC: ['view', 'upload_pbc', 'view_pbc'],
            UserRole.ADMIN: ['*']  # All permissions
        }
        return permissions_map.get(role, [])


class AuditLogger:
    """Logger zdarzeń audytowych."""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path.home() / '.ai-auditor' / 'compliance' / 'audit.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.crypto_manager = CryptoManager()
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicjalizacja bazy danych."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        username TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT NOT NULL,
                        resource_id TEXT,
                        resource_type TEXT,
                        details TEXT NOT NULL,
                        security_level TEXT NOT NULL,
                        hash_signature TEXT NOT NULL
                    )
                """)
                conn.commit()
        except Exception as e:
            self.logger.error(f"Audit database initialization failed: {e}")
            raise AuditError(f"Audit database initialization failed: {e}")
    
    def log_event(self, user: User, event_type: EventType, description: str,
                 ip_address: str = "127.0.0.1", user_agent: str = "Unknown",
                 resource_id: str = None, resource_type: str = None,
                 details: Dict[str, Any] = None, security_level: SecurityLevel = SecurityLevel.MEDIUM) -> AuditEvent:
        """Logowanie zdarzenia."""
        try:
            if details is None:
                details = {}
            
            event = AuditEvent(
                id=str(uuid.uuid4()),
                user_id=user.id,
                username=user.username,
                event_type=event_type,
                description=description,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                resource_id=resource_id,
                resource_type=resource_type,
                details=details,
                security_level=security_level,
                hash_signature=""
            )
            
            # Generate hash signature
            event_data = f"{event.id}{event.user_id}{event.event_type.value}{event.timestamp.isoformat()}{json.dumps(event.details)}"
            event.hash_signature = self.crypto_manager.generate_hmac(event_data)
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO audit_events (id, user_id, username, event_type, description,
                                            timestamp, ip_address, user_agent, resource_id,
                                            resource_type, details, security_level, hash_signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.id, event.user_id, event.username, event.event_type.value,
                    event.description, event.timestamp.isoformat(), event.ip_address,
                    event.user_agent, event.resource_id, event.resource_type,
                    json.dumps(event.details), event.security_level.value, event.hash_signature
                ))
                conn.commit()
            
            self.logger.info(f"Audit event logged: {event_type.value} by {user.username}")
            return event
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            raise AuditError(f"Audit logging failed: {e}")
    
    def get_events(self, user_id: str = None, event_type: EventType = None,
                  start_date: datetime = None, end_date: datetime = None,
                  limit: int = 100) -> List[AuditEvent]:
        """Pobieranie zdarzeń audytowych."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM audit_events WHERE 1=1"
                params = []
                
                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type.value)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = AuditEvent(
                        id=row[0],
                        user_id=row[1],
                        username=row[2],
                        event_type=EventType(row[3]),
                        description=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        ip_address=row[6],
                        user_agent=row[7],
                        resource_id=row[8],
                        resource_type=row[9],
                        details=json.loads(row[10]),
                        security_level=SecurityLevel(row[11]),
                        hash_signature=row[12]
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.logger.error(f"Audit events retrieval failed: {e}")
            raise AuditError(f"Audit events retrieval failed: {e}")
    
    def verify_event_integrity(self, event: AuditEvent) -> bool:
        """Weryfikacja integralności zdarzenia."""
        try:
            event_data = f"{event.id}{event.user_id}{event.event_type.value}{event.timestamp.isoformat()}{json.dumps(event.details)}"
            expected_hash = self.crypto_manager.generate_hmac(event_data)
            return hmac.compare_digest(expected_hash, event.hash_signature)
        except Exception as e:
            self.logger.error(f"Event integrity verification failed: {e}")
            return False


class AccessControlManager:
    """Menedżer kontroli dostępu."""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path.home() / '.ai-auditor' / 'compliance' / 'access.db'
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicjalizacja bazy danych."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS access_control (
                        resource_id TEXT PRIMARY KEY,
                        resource_type TEXT NOT NULL,
                        owner_id TEXT NOT NULL,
                        permissions TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        modified_at TEXT NOT NULL,
                        version INTEGER NOT NULL
                    )
                """)
                conn.commit()
        except Exception as e:
            self.logger.error(f"Access control database initialization failed: {e}")
            raise SecurityError(f"Access control database initialization failed: {e}")
    
    def create_access_control(self, resource_id: str, resource_type: str, owner_id: str,
                            permissions: Dict[UserRole, List[str]] = None) -> AccessControl:
        """Tworzenie kontroli dostępu."""
        try:
            if permissions is None:
                permissions = self._get_default_permissions()
            
            access_control = AccessControl(
                resource_id=resource_id,
                resource_type=resource_type,
                owner_id=owner_id,
                permissions=permissions,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                version=1
            )
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO access_control (resource_id, resource_type, owner_id,
                                              permissions, created_at, modified_at, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    access_control.resource_id, access_control.resource_type,
                    access_control.owner_id, json.dumps({k.value: v for k, v in permissions.items()}),
                    access_control.created_at.isoformat(), access_control.modified_at.isoformat(),
                    access_control.version
                ))
                conn.commit()
            
            self.logger.info(f"Access control created for {resource_type}: {resource_id}")
            return access_control
            
        except Exception as e:
            self.logger.error(f"Access control creation failed: {e}")
            raise SecurityError(f"Access control creation failed: {e}")
    
    def check_permission(self, user: User, resource_id: str, permission: str) -> bool:
        """Sprawdzanie uprawnień."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT permissions FROM access_control WHERE resource_id = ?
                """, (resource_id,))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                permissions = json.loads(row[0])
                role_permissions = permissions.get(user.role.value, [])
                
                # Check if user has permission
                if '*' in role_permissions or permission in role_permissions:
                    return True
                
                # Check if user is owner
                cursor = conn.execute("""
                    SELECT owner_id FROM access_control WHERE resource_id = ?
                """, (resource_id,))
                
                owner_row = cursor.fetchone()
                if owner_row and owner_row[0] == user.id:
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False
    
    def _get_default_permissions(self) -> Dict[UserRole, List[str]]:
        """Pobieranie domyślnych uprawnień."""
        return {
            UserRole.AUDITOR: ['view', 'download'],
            UserRole.SENIOR: ['view', 'download', 'modify'],
            UserRole.PARTNER: ['view', 'download', 'modify', 'delete'],
            UserRole.CLIENT_PBC: ['view'],
            UserRole.ADMIN: ['*']
        }


class ComplianceManager:
    """Menedżer compliance."""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path.home() / '.ai-auditor' / 'compliance'
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.crypto_manager = CryptoManager()
        self.user_manager = UserManager(self.data_dir / 'users.db')
        self.audit_logger = AuditLogger(self.data_dir / 'audit.db')
        self.access_control = AccessControlManager(self.data_dir / 'access.db')
        
        # Security policies
        self.security_policies: List[SecurityPolicy] = []
        self._load_security_policies()
    
    def _load_security_policies(self):
        """Ładowanie polityk bezpieczeństwa."""
        try:
            policies_file = self.data_dir / 'security_policies.json'
            if policies_file.exists():
                with open(policies_file, 'r', encoding='utf-8') as f:
                    policies_data = json.load(f)
                    for policy_data in policies_data:
                        policy = SecurityPolicy(
                            id=policy_data['id'],
                            name=policy_data['name'],
                            description=policy_data['description'],
                            rules=policy_data['rules'],
                            created_at=datetime.fromisoformat(policy_data['created_at']),
                            modified_at=datetime.fromisoformat(policy_data['modified_at']),
                            is_active=policy_data['is_active']
                        )
                        self.security_policies.append(policy)
        except Exception as e:
            self.logger.error(f"Security policies loading failed: {e}")
    
    def create_user(self, username: str, email: str, role: UserRole,
                   permissions: List[str] = None, security_level: SecurityLevel = SecurityLevel.MEDIUM) -> User:
        """Tworzenie użytkownika."""
        try:
            user = self.user_manager.create_user(username, email, role, permissions, security_level)
            
            # Log user creation
            self.audit_logger.log_event(
                user=user,
                event_type=EventType.LOGIN,
                description=f"User created: {username}",
                security_level=SecurityLevel.HIGH
            )
            
            return user
            
        except Exception as e:
            self.logger.error(f"User creation failed: {e}")
            raise SecurityError(f"User creation failed: {e}")
    
    def authenticate_user(self, username: str, ip_address: str = "127.0.0.1",
                         user_agent: str = "Unknown") -> Optional[User]:
        """Uwierzytelnianie użytkownika."""
        try:
            user = self.user_manager.get_user_by_username(username)
            if user and user.is_active:
                # Update last login
                self.user_manager.update_user_login(user.id)
                
                # Log login
                self.audit_logger.log_event(
                    user=user,
                    event_type=EventType.LOGIN,
                    description=f"User logged in: {username}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    security_level=SecurityLevel.MEDIUM
                )
                
                return user
            
            return None
            
        except Exception as e:
            self.logger.error(f"User authentication failed: {e}")
            raise SecurityError(f"User authentication failed: {e}")
    
    def authorize_action(self, user: User, resource_id: str, action: str) -> bool:
        """Autoryzacja akcji."""
        try:
            # Check if user has permission
            has_permission = self.access_control.check_permission(user, resource_id, action)
            
            if not has_permission:
                # Log unauthorized access attempt
                self.audit_logger.log_event(
                    user=user,
                    event_type=EventType.VIEW,
                    description=f"Unauthorized access attempt: {action} on {resource_id}",
                    resource_id=resource_id,
                    security_level=SecurityLevel.HIGH
                )
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Authorization failed: {e}")
            return False
    
    def log_user_action(self, user: User, event_type: EventType, description: str,
                       resource_id: str = None, resource_type: str = None,
                       details: Dict[str, Any] = None, security_level: SecurityLevel = SecurityLevel.MEDIUM):
        """Logowanie akcji użytkownika."""
        try:
            self.audit_logger.log_event(
                user=user,
                event_type=event_type,
                description=description,
                resource_id=resource_id,
                resource_type=resource_type,
                details=details or {},
                security_level=security_level
            )
        except Exception as e:
            self.logger.error(f"User action logging failed: {e}")
            raise AuditError(f"User action logging failed: {e}")
    
    def get_audit_trail(self, user_id: str = None, start_date: datetime = None,
                       end_date: datetime = None, limit: int = 100) -> List[AuditEvent]:
        """Pobieranie śladu audytowego."""
        try:
            return self.audit_logger.get_events(user_id, None, start_date, end_date, limit)
        except Exception as e:
            self.logger.error(f"Audit trail retrieval failed: {e}")
            raise AuditError(f"Audit trail retrieval failed: {e}")
    
    def verify_data_integrity(self, data: str, hash_value: str) -> bool:
        """Weryfikacja integralności danych."""
        try:
            return self.crypto_manager.verify_hash(data, hash_value)
        except Exception as e:
            self.logger.error(f"Data integrity verification failed: {e}")
            return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Szyfrowanie wrażliwych danych."""
        try:
            return self.crypto_manager.encrypt_data(data)
        except Exception as e:
            self.logger.error(f"Sensitive data encryption failed: {e}")
            raise SecurityError(f"Sensitive data encryption failed: {e}")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Odszyfrowanie wrażliwych danych."""
        try:
            return self.crypto_manager.decrypt_data(encrypted_data)
        except Exception as e:
            self.logger.error(f"Sensitive data decryption failed: {e}")
            raise SecurityError(f"Sensitive data decryption failed: {e}")
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Podsumowanie compliance."""
        try:
            # Get recent audit events
            recent_events = self.audit_logger.get_events(limit=1000)
            
            # Calculate statistics
            total_events = len(recent_events)
            events_by_type = {}
            events_by_user = {}
            events_by_security_level = {}
            
            for event in recent_events:
                # By type
                event_type = event.event_type.value
                events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
                
                # By user
                username = event.username
                events_by_user[username] = events_by_user.get(username, 0) + 1
                
                # By security level
                security_level = event.security_level.value
                events_by_security_level[security_level] = events_by_security_level.get(security_level, 0) + 1
            
            return {
                'total_events': total_events,
                'events_by_type': events_by_type,
                'events_by_user': events_by_user,
                'events_by_security_level': events_by_security_level,
                'security_policies_count': len(self.security_policies),
                'active_policies_count': len([p for p in self.security_policies if p.is_active]),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Compliance summary generation failed: {e}")
            raise AuditError(f"Compliance summary generation failed: {e}")
