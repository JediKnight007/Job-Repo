# Secure Cloud Storage Client (Dropbox Clone)

## Project Overview
This project implements a secure, end-to-end encrypted cloud storage client similar to Dropbox, with a focus on cryptographic security. The system provides file storage, sharing, and synchronization with strong security guarantees including confidentiality, integrity, and authentication.

## Technical Skills Demonstrated

### Cryptography
- **End-to-End Encryption**: Client-side encryption before cloud upload
- **Symmetric Encryption**: AES for file content encryption
- **Asymmetric Encryption**: RSA for key exchange
- **Digital Signatures**: Ensuring file integrity and authenticity
- **Secure Key Management**: Key derivation and storage
- **Hash Functions**: SHA-256 for integrity verification

### Security Concepts
- **Confidentiality**: Files encrypted, server cannot read content
- **Integrity**: Detect tampering via signatures/MACs
- **Authentication**: Verify user and file ownership
- **Forward Secrecy**: Past communications remain secure
- **Threat Modeling**: Design against various attack scenarios

### Software Engineering
- **Client-Server Architecture**: Separation of concerns
- **RESTful API Design**: Clean interface between client and servers
- **Testing**: Comprehensive unit and integration tests
- **Error Handling**: Graceful failure and recovery

## Project Structure
```
dropbox/
├── client.py                   # Main client implementation
├── test_client.py              # Client unit tests
├── test_functionality.py       # Integration and functional tests
├── test_reference.py           # Reference implementation tests
├── requirements.txt            # Python dependencies
├── Makefile                    # Build and test automation
├── backup.txt                  # Backup/documentation
├── update_from_stencil         # Update script
├── .gitignore                  # Git ignore rules
├── .gitattributes              # Git attributes
├── support/                    # Support modules
│   ├── crypto.py              # Cryptographic primitives
│   ├── dataserver.py          # Data storage server
│   ├── keyserver.py           # Public key server
│   └── util.py                # Utility functions
└── reference/                  # Reference implementation
    └── dropbox_client_reference-0.0.1-py3-none-any.whl
```

## Key Features

### 1. Secure File Operations
```python
# Upload file with encryption
client.upload("document.pdf", data)

# Download and decrypt file
data = client.download("document.pdf")

# Append to encrypted file
client.append("log.txt", new_data)
```

### 2. Secure Sharing
```python
# Share file with another user
client.share("document.pdf", "bob")

# Receive shared file
client.receive_share("alice", "document.pdf")

# Revoke access
client.revoke("document.pdf", "bob")
```

### 3. File Operations
- **Upload**: Encrypt and store files
- **Download**: Retrieve and decrypt files
- **Delete**: Securely remove files
- **Append**: Add data to existing files
- **List**: View user's files

### 4. Security Properties

**Confidentiality**
- Server never sees plaintext
- Files encrypted with per-file keys
- Keys encrypted with user's master key

**Integrity**
- HMAC/signature on all data
- Detect any tampering
- Prevent rollback attacks

**Authentication**
- Verify file ownership
- Secure key exchange
- Prevent impersonation

## Technical Implementation

### Client Class Structure
```python
class Client:
    def __init__(self, username, password):
        self.username = username
        self.dataserver = DataServer()
        self.keyserver = KeyServer()
        
        # Derive master key from password
        self.master_key = derive_key(password, username)
        
        # Generate or retrieve RSA keypair
        self.private_key, self.public_key = self.get_keypair()
        
        # Register public key
        self.keyserver.register(username, self.public_key)
    
    def upload(self, filename, data):
        # Generate random file encryption key
        file_key = generate_random_key()
        
        # Encrypt file data
        ciphertext = symmetric_encrypt(data, file_key)
        
        # Encrypt file key with master key
        encrypted_key = symmetric_encrypt(file_key, self.master_key)
        
        # Sign for integrity
        signature = sign(ciphertext, self.private_key)
        
        # Store on server
        self.dataserver.put(filename, {
            'data': ciphertext,
            'key': encrypted_key,
            'sig': signature
        })
    
    def download(self, filename):
        # Retrieve from server
        stored = self.dataserver.get(filename)
        
        # Verify signature
        if not verify(stored['data'], stored['sig'], self.public_key):
            raise IntegrityError("File has been tampered with!")
        
        # Decrypt file key
        file_key = symmetric_decrypt(stored['key'], self.master_key)
        
        # Decrypt file data
        plaintext = symmetric_decrypt(stored['data'], file_key)
        
        return plaintext
    
    def share(self, filename, recipient):
        # Get recipient's public key
        recipient_pubkey = self.keyserver.get(recipient)
        
        # Get file key
        stored = self.dataserver.get(filename)
        file_key = symmetric_decrypt(stored['key'], self.master_key)
        
        # Encrypt file key with recipient's public key
        shared_key = asymmetric_encrypt(file_key, recipient_pubkey)
        
        # Store share pointer
        self.dataserver.put(f"{recipient}/{filename}", {
            'owner': self.username,
            'shared_key': shared_key
        })
    
    def receive_share(self, sender, filename):
        # Get share pointer
        share_info = self.dataserver.get(f"{self.username}/{filename}")
        
        # Decrypt file key with private key
        file_key = asymmetric_decrypt(share_info['shared_key'], 
                                      self.private_key)
        
        # Get file data from owner
        stored = self.dataserver.get(f"{sender}/{filename}")
        
        # Decrypt file
        plaintext = symmetric_decrypt(stored['data'], file_key)
        
        return plaintext
```

### Cryptographic Primitives (support/crypto.py)
```python
# Symmetric encryption (AES-256-GCM)
def symmetric_encrypt(plaintext, key):
    nonce = generate_nonce()
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + tag + ciphertext

def symmetric_decrypt(ciphertext, key):
    nonce = ciphertext[:16]
    tag = ciphertext[16:32]
    ct = ciphertext[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ct, tag)
    return plaintext

# Asymmetric encryption (RSA-2048)
def asymmetric_encrypt(plaintext, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(plaintext)

def asymmetric_decrypt(ciphertext, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(ciphertext)

# Digital signatures (RSA-PSS)
def sign(message, private_key):
    h = SHA256.new(message)
    signature = pss.new(private_key).sign(h)
    return signature

def verify(message, signature, public_key):
    h = SHA256.new(message)
    try:
        pss.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

# Key derivation (PBKDF2)
def derive_key(password, salt, iterations=100000):
    return PBKDF2(password, salt, dkLen=32, count=iterations)

# Secure random generation
def generate_random_key(length=32):
    return get_random_bytes(length)
```

### Server Interfaces

**Data Server**
```python
class DataServer:
    def put(self, key, value):
        """Store key-value pair"""
        
    def get(self, key):
        """Retrieve value by key"""
        
    def delete(self, key):
        """Remove key-value pair"""
```

**Key Server**
```python
class KeyServer:
    def register(self, username, public_key):
        """Register user's public key"""
        
    def get(self, username):
        """Get user's public key"""
```

## Technical Environment
- **Language**: Python 3.10+
- **Cryptography Library**: PyCryptodome or cryptography
- **Testing**: pytest
- **Dependencies**: See requirements.txt

## Skills & Technologies
- **Python Programming**: Advanced OOP and cryptography
- **Cryptography**: Symmetric/asymmetric encryption, signatures
- **Security Engineering**: Threat modeling, secure design
- **Distributed Systems**: Client-server architecture
- **Testing**: Unit tests, integration tests, security tests
- **Software Design**: Clean architecture, separation of concerns

## Security Analysis

### Threat Model

**Adversary Capabilities:**
- Controls the server (honest-but-curious or malicious)
- Can read, modify, delete any stored data
- Cannot break cryptographic primitives (computational security)

**Security Goals:**
1. **Confidentiality**: Server cannot read file contents
2. **Integrity**: Detect any unauthorized modifications
3. **Authentication**: Verify identity of users and files
4. **Availability**: (Not guaranteed - server can refuse service)

### Attack Scenarios & Defenses

**1. Server Reads Files**
- *Attack*: Server tries to read encrypted data
- *Defense*: End-to-end encryption, server only has ciphertext

**2. Server Modifies Files**
- *Attack*: Server alters encrypted data
- *Defense*: HMAC/signature verification detects tampering

**3. Rollback Attack**
- *Attack*: Server replaces current file with old version
- *Defense*: Version numbers, timestamps in signed data

**4. Key Exposure**
- *Attack*: Attacker gets user's password
- *Defense*: Each file has unique key, damage limited

**5. Man-in-the-Middle**
- *Attack*: Impersonate user during key exchange
- *Defense*: Public key infrastructure, signature verification

**6. Share Revocation**
- *Attack*: User still has file key after revocation
- *Defense*: Re-encrypt file with new key, notify owner

## Testing Strategy

### Unit Tests
- Cryptographic primitive correctness
- Client method functionality
- Error handling

### Integration Tests
- End-to-end upload/download cycles
- Sharing workflows
- Multiple users interacting

### Security Tests
- Attempt to decrypt without key
- Modify ciphertext, verify detection
- Replay old versions
- Impersonation attempts

### Performance Tests
- Large file handling
- Many files/users
- Concurrent operations

## Performance Considerations

### Optimization Strategies
1. **Chunking**: Split large files into chunks
2. **Caching**: Cache frequently used keys
3. **Compression**: Compress before encryption
4. **Deduplication**: Hash-based for identical files
5. **Incremental Upload**: Only upload changed parts

### Scalability
- **Client-side**: Bounded by local resources
- **Server-side**: Horizontal scaling, sharding
- **Key Server**: Replicas for availability
- **Data Server**: Distributed storage (S3, GCS)

## Learning Outcomes
This project demonstrates:
- Deep understanding of applied cryptography
- Ability to design secure systems
- Knowledge of common security vulnerabilities
- Experience with secure coding practices
- Understanding of key management
- Testing security properties

## Real-World Applications
- **Cloud Storage**: Dropbox, Google Drive, OneDrive
- **Encrypted Messaging**: Signal, WhatsApp
- **Password Managers**: 1Password, LastPass
- **Backup Solutions**: Encrypted backup services
- **Enterprise File Sharing**: Box, ShareFile
- **Healthcare**: HIPAA-compliant file storage

## Industry Standards
- **NIST**: Cryptographic standards and guidelines
- **OWASP**: Secure coding practices
- **ISO 27001**: Information security management
- **GDPR**: Data protection and privacy
- **HIPAA**: Healthcare data security

## Common Pitfalls Avoided
1. **Rolling Your Own Crypto**: Use established libraries
2. **Weak Key Derivation**: Use PBKDF2/scrypt/argon2
3. **ECB Mode**: Use GCM or CTR with authentication
4. **Predictable IVs**: Use cryptographically random nonces
5. **Timing Attacks**: Use constant-time comparison
6. **Key Reuse**: Unique key per file
7. **No Integrity**: Always authenticate ciphertext

## Future Enhancements
- **Versioning**: Track file history
- **Conflict Resolution**: Handle concurrent modifications
- **Selective Sync**: Sync only changed portions
- **Mobile Clients**: iOS and Android apps
- **Real-time Collaboration**: Operational transforms
- **Zero-Knowledge Proof**: Prove properties without revealing data
- **Homomorphic Encryption**: Compute on encrypted data
- **Blockchain**: Decentralized file integrity log

## Comparison with Real Dropbox
| Feature | This Project | Real Dropbox |
|---------|-------------|--------------|
| E2E Encryption | ✓ | ○ (Optional) |
| Client-side | ✓ | ✓ |
| Deduplication | ○ | ✓ |
| Versioning | ○ | ✓ |
| Sync Protocol | ○ | ✓ (proprietary) |
| Mobile | ○ | ✓ |
| Scale | Educational | Production |

