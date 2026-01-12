# Buffer Overflow and Security Exploits in Assembly

## Project Overview
This project demonstrates deep understanding of computer security by implementing and defending against buffer overflow attacks. Written in x86-64 assembly and C, it covers stack-based vulnerabilities, exploit development, return-oriented programming, and security mitigation techniques.

## Technical Skills Demonstrated

### Computer Security
- **Buffer Overflow Exploits**: Understanding and exploiting stack vulnerabilities
- **Return-Oriented Programming (ROP)**: Advanced exploitation technique
- **Stack Manipulation**: Precise control of stack frames and return addresses
- **Shellcode**: Writing and injecting machine code
- **Security Mitigations**: Understanding and bypassing protections

### Low-Level Programming
- **x86-64 Assembly**: Writing exploit payloads in assembly
- **Memory Layout**: Deep understanding of stack, heap, and code segments
- **Binary Analysis**: Reading and understanding compiled code
- **Debugging**: Using GDB for exploit development
- **Hexadecimal**: Working with raw bytes and addresses

### Reverse Engineering
- **Disassembly**: Analyzing compiled binaries
- **Control Flow Analysis**: Understanding program execution paths
- **Stack Frame Analysis**: Examining function prologues and epilogues
- **Address Calculation**: Computing offsets and padding

## Project Structure
```
buffer-JediKnight007/
├── buffer                  # Vulnerable binary target
├── makecookie              # Cookie generation utility
├── hex2raw                 # Convert hex strings to raw bytes
├── fraudster.s             # Assembly exploit code
├── fraudster.o             # Compiled object file
├── fraudster.d             # Dependencies
├── fraudster.txt           # Exploit string (raw input)
├── fraudster-raw.txt       # Hex representation
├── fraudster.gdb           # GDB debugging script
├── lost.s                  # Another exploit variant
├── lost.o                  # Compiled object
├── lost.d                  # Dependencies
├── lost.txt                # Exploit string
├── lost-raw.txt            # Hex representation
├── lost.gdb                # GDB script
├── sandwiches.txt          # Exploit payload
├── sandwiches-raw.txt      # Hex version
├── sandwiches.gdb          # GDB script
├── lights.txt              # Exploit payload
├── lights-raw.txt          # Hex version
├── lights.gdb              # GDB script
├── obj.txt                 # Object dump/analysis
├── cookie.txt              # Cookie value for exploit
└── README.md               # Project documentation
```

## Key Features

### 1. Multiple Exploit Techniques
- **Stack Smashing**: Basic buffer overflow
- **Return Address Overwrite**: Redirecting execution flow
- **Code Injection**: Injecting and executing custom code
- **Return-Oriented Programming**: Chaining existing code gadgets
- **Frame Pointer Manipulation**: Advanced exploitation

### 2. Exploit Development Process
1. **Analysis**: Reverse engineer target binary
2. **Vulnerability Identification**: Find buffer overflow points
3. **Offset Calculation**: Determine padding needed
4. **Payload Creation**: Write exploit code in assembly
5. **Encoding**: Convert to hex/raw bytes
6. **Testing**: Debug with GDB
7. **Exploitation**: Successfully redirect execution

### 3. Security Concepts Covered
- **Stack Canaries**: Detection and bypassing
- **ASLR**: Address Space Layout Randomization
- **DEP/NX**: Non-executable stack protection
- **Stack Cookies**: Runtime integrity checks
- **Safe Functions**: strcpy vs. strncpy

### 4. Assembly Exploit Code
Custom shellcode written in x86-64 assembly:
- Function calls with proper ABI compliance
- Register manipulation
- Stack alignment
- System call invocation

## Technical Implementation

### Buffer Overflow Mechanics
```
Normal Stack:           Overflowed Stack:
+----------------+      +----------------+
| Return Addr    |  →   | ATTACKER ADDR  | ← Overwritten!
+----------------+      +----------------+
| Saved EBP      |      | AAAAAAAAAA     |
+----------------+      +----------------+
| Local Vars     |      | AAAAAAAAAA     |
+----------------+      +----------------+
| Buffer[64]     |      | AAAAAAAAAA     | ← Overflow starts
+----------------+      +----------------+
```

### Exploit Assembly Example
```asm
; fraudster.s - Sample exploit code
.global fraudster
fraudster:
    push   %rbp
    mov    %rsp, %rbp
    
    ; Call target function with cookie
    mov    $COOKIE_VALUE, %rdi
    call   target_function
    
    ; Clean up and return
    pop    %rbp
    ret
```

### Exploit String Construction
```python
# Conceptual exploit building
padding = b'A' * 64           # Fill buffer
padding += b'B' * 8           # Overwrite saved RBP
exploit_addr = p64(0x400abc)  # Desired return address
payload = padding + exploit_addr
```

### hex2raw Utility
Converts ASCII hex to raw bytes:
```bash
# Input: fraudster-raw.txt (hex)
# 41 41 41 41 42 42 42 42 ef be ad de

# Output: fraudster.txt (raw bytes)
# AAAABBBB<raw_bytes>

./hex2raw < fraudster-raw.txt > fraudster.txt
```

## Technical Environment
- **Architecture**: x86-64 (64-bit Intel)
- **OS**: Linux
- **Assembler**: GNU Assembler (gas)
- **Debugger**: GDB with assembly extensions
- **Tools**: objdump, readelf, strace
- **Compiler**: GCC with specific flags

## Skills & Technologies
- **x86-64 Assembly**: Expert-level instruction set knowledge
- **C Programming**: Understanding stack behavior
- **GDB**: Advanced debugging and exploit development
- **Binary Exploitation**: Practical exploit writing
- **Computer Architecture**: CPU, memory, and caching
- **Operating Systems**: Process memory layout
- **Security Research**: Vulnerability analysis

## Vulnerability Types Exploited

### 1. Stack Buffer Overflow
```c
void vulnerable_function(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // NO LENGTH CHECK!
}
```

### 2. Format String Vulnerability
```c
void bad_function(char *user_input) {
    printf(user_input);  // Allows %n, %x, etc.
}
```

### 3. Integer Overflow
```c
void allocate(size_t size) {
    char *buf = malloc(size + 4);  // Can wrap around!
    memcpy(buf, data, size);
}
```

## Exploit Levels (Increasing Difficulty)

### Level 1: "Lights" - Basic Overflow
- Simple buffer overflow
- Overwrite return address
- Redirect to existing function

### Level 2: "Sandwiches" - Code Injection
- Inject shellcode into buffer
- Jump to shellcode address
- Execute custom code

### Level 3: "Lost" - Advanced Manipulation
- Bypass stack canaries
- Chain multiple overwrites
- More complex payload

### Level 4: "Fraudster" - ROP Chain
- Return-Oriented Programming
- Chain gadgets from existing code
- Bypass non-executable stack (DEP/NX)

## GDB Debugging Scripts
Each exploit includes `.gdb` scripts for debugging:
```gdb
# fraudster.gdb
break vulnerable_function
run < fraudster.txt
x/40wx $rsp              # Examine stack
info registers           # Check register state
disassemble             # View assembly
continue
```

## Security Mitigations & Bypasses

### Modern Protections
1. **Stack Canaries**: Random value checked before return
   - *Bypass*: Leak canary, include in exploit

2. **ASLR**: Randomize addresses
   - *Bypass*: Information leak to find addresses

3. **DEP/NX**: Non-executable stack
   - *Bypass*: ROP (Return-Oriented Programming)

4. **PIE**: Position-Independent Executable
   - *Bypass*: Memory leak + relative offsets

5. **RELRO**: Read-only GOT/PLT
   - *Bypass*: Find other targets

### Defensive Programming
```c
// BAD
strcpy(dest, src);

// GOOD
strncpy(dest, src, sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';

// BETTER
strlcpy(dest, src, sizeof(dest));

// BEST
// Use safe languages (Rust, Go) or bounds checking
```

## Learning Outcomes
This project demonstrates:
- Deep understanding of computer security vulnerabilities
- Ability to think like both attacker and defender
- Expert knowledge of x86-64 architecture and assembly
- Practical experience with exploit development
- Understanding of modern security mitigations
- Ethical hacking and responsible disclosure practices

## Real-World Impact

### Historical Exploits
- **Morris Worm (1988)**: First major buffer overflow exploit
- **Code Red (2001)**: IIS buffer overflow worm
- **Slammer (2003)**: SQL Server buffer overflow
- **Heartbleed (2014)**: Buffer over-read in OpenSSL

### Modern Applications
- **Penetration Testing**: Finding vulnerabilities before attackers
- **Security Research**: Understanding attack vectors
- **Secure Development**: Writing safer code
- **Incident Response**: Analyzing exploits
- **Capture The Flag (CTF)**: Security competitions

## Ethical Considerations
This project is for **educational purposes only**:
- Understanding vulnerabilities to write secure code
- Legal and authorized security testing only
- Responsible disclosure of discovered vulnerabilities
- Never use for malicious purposes
- Always obtain proper authorization

## Tools & Utilities

### Analysis Tools
- **objdump**: Disassemble binaries
- **readelf**: Examine ELF format
- **strings**: Extract printable strings
- **file**: Identify file type
- **checksec**: Check security features

### Exploitation Tools
- **pwntools**: Python exploit development library
- **ROPgadget**: Find ROP gadgets
- **gef/pwndbg**: Enhanced GDB for exploitation
- **radare2**: Reverse engineering framework

### Debugging Commands
```bash
# Useful GDB commands
info frame              # Stack frame info
x/100x $rsp            # Examine stack
disas function_name    # Disassemble function
pattern create 200     # Create cyclic pattern
pattern offset 0x41414141  # Find offset
```

## Compilation Flags
Understanding security features:
```bash
# Vulnerable (for learning)
gcc -o buffer buffer.c -fno-stack-protector -z execstack

# Secure (production)
gcc -o buffer buffer.c -fstack-protector-all -D_FORTIFY_SOURCE=2 \
    -Wl,-z,relro,-z,now -pie -fPIE
```

## Cookie System
The project uses cookies (unique values) to verify successful exploitation:
- Each student/user gets unique cookie
- Exploit must call function with correct cookie
- Proves exploit worked, not just crash
- Automated grading verification

## Resources for Further Learning
- **Books**: 
  - "Hacking: The Art of Exploitation" by Jon Erickson
  - "The Shellcoder's Handbook"
- **Websites**:
  - exploit-db.com
  - cve.mitre.org
- **Practice**:
  - overthewire.org/wargames
  - pwnable.kr
  - exploit.education

