# Foreground and Background Process Management Shell (Shell-2)

## Project Overview
This project implements an advanced Unix shell with sophisticated process management capabilities, including foreground/background job control, job suspension, and signal handling. It extends basic shell functionality to support complex process lifecycle management similar to bash or zsh.

## Technical Skills Demonstrated

### Systems Programming
- **Process Management**: Creating, suspending, and resuming processes
- **Job Control**: Managing multiple concurrent processes
- **Signal Handling**: Implementing SIGTSTP, SIGCHLD, SIGINT handlers
- **Inter-Process Communication**: Parent-child process coordination

### Operating Systems Concepts
- Process states (running, stopped, background)
- Process groups and sessions
- Terminal I/O control
- File descriptors and redirection

## Project Structure
```
shell-2-JediKnight007/
├── shell.c                  # Main shell implementation with job control
├── jobs.c                   # Job management functions
├── jobs.h                   # Job structure definitions
├── jobs.o                   # Compiled job management module
├── shell.o                  # Compiled shell module
├── 33sh                     # Shell executable
├── 33noprompt               # No-prompt version for testing
├── Makefile                 # Build configuration
├── cs0330_shell_2_demo      # Reference implementation
├── cs0330_noprompt_shell_2_demo
├── cs0330_shell_2_test      # Test harness
├── cs0330_shell_2_harness
├── cs0330_cleanup_shell     # Cleanup utility
├── shell_2_tests/           # Comprehensive test suite
│   ├── shell_2_tests_long/
│   └── shell_2_tests_quick/
└── README.md
```

## Key Features

### 1. Job Control
- **Background Processes**: Execute commands with `&` operator
- **Job Suspension**: Ctrl-Z (SIGTSTP) support
- **Job Resumption**: 
  - `fg` - Bring job to foreground
  - `bg` - Resume job in background
- **Job Listing**: `jobs` command to show all active jobs

### 2. Signal Handling
- **SIGTSTP**: Suspend foreground process
- **SIGCHLD**: Handle child process state changes
- **SIGINT**: Interrupt foreground process (Ctrl-C)
- **Signal Masking**: Prevent race conditions

### 3. Process State Management
- Track job IDs and process group IDs
- Monitor job states (running, stopped, done)
- Reap zombie processes
- Clean up terminated background jobs

### 4. Built-in Commands
- `fg [job_id]` - Bring job to foreground
- `bg [job_id]` - Resume job in background
- `jobs` - List all jobs
- `cd` - Change directory
- `exit` - Terminate shell

## Technical Implementation

### Job Management
```c
typedef struct job {
    pid_t pid;              // Process ID
    pid_t pgid;             // Process group ID
    int job_id;             // Job number
    char *command;          // Command string
    int status;             // Running, stopped, etc.
} job_t;
```

### Signal Handling Strategy
- Block SIGCHLD during critical sections
- Install custom signal handlers
- Properly restore terminal control
- Handle signal delivery to process groups

### Process Group Management
- Create new process groups for jobs
- Assign terminal control to foreground process group
- Save and restore terminal state

## Technical Environment
- **Language**: C
- **Platform**: Unix/Linux
- **System Calls**: 
  - `fork()`, `execv()`, `waitpid()`
  - `kill()`, `signal()`, `sigprocmask()`
  - `setpgid()`, `tcsetpgrp()`, `tcgetpgrp()`
- **Standards**: POSIX

## Skills & Technologies
- **C Programming**: Advanced pointer manipulation and data structures
- **Systems Programming**: Deep understanding of Unix process model
- **Signal Handling**: Asynchronous event handling
- **Concurrency**: Managing multiple processes safely
- **Error Handling**: Robust error checking and recovery
- **Testing**: Comprehensive test suite validation

## Challenges Solved

### 1. Race Conditions
- Signal delivery timing issues
- Parent-child synchronization
- Terminal control handoff

### 2. Zombie Process Prevention
- Proper reaping of terminated children
- Asynchronous notification handling
- Background job cleanup

### 3. Terminal Control
- Saving and restoring terminal state
- Proper foreground process group management
- Handling terminal signals

## Testing
Includes extensive test suite covering:
- Basic foreground execution
- Background process launching
- Job suspension and resumption
- Signal handling correctness
- Edge cases and error conditions
- Multiple concurrent jobs
- Long-running processes

## Learning Outcomes
This project demonstrates:
- Mastery of Unix process management
- Understanding of signal handling and race conditions
- Ability to implement complex systems software
- Experience with debugging multi-process programs
- Knowledge of terminal I/O and job control

## Real-World Applications
- **Shell Development**: Understanding how bash/zsh work
- **Process Orchestration**: Container runtimes, job schedulers
- **DevOps Tools**: Background task management
- **System Administration**: Process monitoring and control
- **Embedded Systems**: Resource-constrained process management

## Comparison with Shell-1
This project builds upon basic shell implementation (Shell-1) by adding:
- Job control and background processes
- Signal handling infrastructure
- Process state tracking
- Job ID management
- More sophisticated error handling

