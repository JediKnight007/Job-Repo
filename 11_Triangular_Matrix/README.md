# Triangular Matrix Solver

## Project Overview
This project implements efficient solvers for triangular linear systems in MATLAB. It demonstrates understanding of numerical linear algebra, specifically forward and backward substitution algorithms for lower and upper triangular matrices.

## Technical Skills Demonstrated

### Numerical Linear Algebra
- **Forward Substitution**: Solving Lx = b for lower triangular L
- **Backward Substitution**: Solving Ux = b for upper triangular U
- **Triangular Systems**: Exploiting matrix structure for efficiency
- **Numerical Stability**: Understanding of error propagation

### Algorithm Design
- **Efficient Algorithms**: O(n²) complexity vs O(n³) for general systems
- **Matrix Structure**: Leveraging sparsity and zero patterns
- **Vectorization**: MATLAB-optimized implementations

## Project Structure
```
HW1/
├── Triangular.m    # Main triangular solver implementation
└── Test.m          # Test cases and validation
```

## Key Features

### 1. Lower Triangular Solver (Forward Substitution)
Solves Lx = b where L is lower triangular:
```
[l11  0   0  ] [x1]   [b1]
[l21 l22  0  ] [x2] = [b2]
[l31 l32 l33 ] [x3]   [b3]
```

### 2. Upper Triangular Solver (Backward Substitution)
Solves Ux = b where U is upper triangular:
```
[u11 u12 u13] [x1]   [b1]
[ 0  u22 u23] [x2] = [b2]
[ 0   0  u33] [x3]   [b3]
```

### 3. Error Checking
- Validates matrix is triangular
- Checks for zero diagonal elements
- Handles singular matrices
- Dimension compatibility checking

### 4. Performance Optimization
- Exploits matrix structure (zeros)
- Vectorized operations
- In-place computation where possible

## Technical Implementation

### Forward Substitution Algorithm
```matlab
function x = forward_substitution(L, b)
    % Solve Lx = b where L is lower triangular
    % L: n×n lower triangular matrix
    % b: n×1 vector
    % x: n×1 solution vector
    
    n = length(b);
    x = zeros(n, 1);
    
    % Solve from top to bottom
    for i = 1:n
        % Check for zero diagonal
        if L(i,i) == 0
            error('Matrix is singular');
        end
        
        % x_i = (b_i - sum(L_ij * x_j)) / L_ii
        x(i) = b(i);
        for j = 1:i-1
            x(i) = x(i) - L(i,j) * x(j);
        end
        x(i) = x(i) / L(i,i);
    end
end
```

### Backward Substitution Algorithm
```matlab
function x = backward_substitution(U, b)
    % Solve Ux = b where U is upper triangular
    % U: n×n upper triangular matrix
    % b: n×1 vector
    % x: n×1 solution vector
    
    n = length(b);
    x = zeros(n, 1);
    
    % Solve from bottom to top
    for i = n:-1:1
        % Check for zero diagonal
        if U(i,i) == 0
            error('Matrix is singular');
        end
        
        % x_i = (b_i - sum(U_ij * x_j)) / U_ii
        x(i) = b(i);
        for j = i+1:n
            x(i) = x(i) - U(i,j) * x(j);
        end
        x(i) = x(i) / U(i,i);
    end
end
```

### Vectorized Version (More Efficient)
```matlab
function x = forward_substitution_vec(L, b)
    % Vectorized forward substitution
    n = length(b);
    x = zeros(n, 1);
    
    for i = 1:n
        if L(i,i) == 0
            error('Matrix is singular');
        end
        x(i) = (b(i) - L(i,1:i-1) * x(1:i-1)) / L(i,i);
    end
end

function x = backward_substitution_vec(U, b)
    % Vectorized backward substitution
    n = length(b);
    x = zeros(n, 1);
    
    for i = n:-1:1
        if U(i,i) == 0
            error('Matrix is singular');
        end
        x(i) = (b(i) - U(i,i+1:n) * x(i+1:n)) / U(i,i);
    end
end
```

### Matrix Validation
```matlab
function is_valid = is_lower_triangular(A, tol)
    % Check if matrix is lower triangular
    if nargin < 2
        tol = 1e-10;  % Default tolerance
    end
    
    [m, n] = size(A);
    if m ~= n
        is_valid = false;
        return;
    end
    
    % Check upper triangle is zero
    for i = 1:n
        for j = i+1:n
            if abs(A(i,j)) > tol
                is_valid = false;
                return;
            end
        end
    end
    
    is_valid = true;
end

function is_valid = is_upper_triangular(A, tol)
    % Check if matrix is upper triangular
    if nargin < 2
        tol = 1e-10;
    end
    
    [m, n] = size(A);
    if m ~= n
        is_valid = false;
        return;
    end
    
    % Check lower triangle is zero
    for i = 1:n
        for j = 1:i-1
            if abs(A(i,j)) > tol
                is_valid = false;
                return;
            end
        end
    end
    
    is_valid = true;
end
```

## Technical Environment
- **Language**: MATLAB
- **Domain**: Numerical Linear Algebra
- **Precision**: IEEE 754 double precision
- **Libraries**: Built-in MATLAB functions

## Skills & Technologies
- **MATLAB Programming**: Matrix operations, vectorization
- **Numerical Methods**: Linear system solving
- **Algorithm Implementation**: Efficient algorithm coding
- **Error Handling**: Robustness checks
- **Testing**: Validation against known solutions

## Algorithmic Complexity

### Time Complexity
- **Forward/Backward Substitution**: O(n²)
  - n iterations
  - Each iteration: O(i) or O(n-i) operations
  - Total: 1 + 2 + ... + n = n(n+1)/2 ≈ O(n²)

- **Validation**: O(n²) for checking triangular structure

### Space Complexity
- **Solution Vector**: O(n)
- **In-place Version**: O(1) extra space
- **Total**: O(n) for storing solution

### Comparison with General Solvers
| Method | Complexity | Notes |
|--------|-----------|-------|
| Gaussian Elim. | O(n³) | General systems |
| LU Decomp. | O(n³) | One-time cost |
| Triangular | O(n²) | Exploits structure |
| Back/Forward Sub | O(n²) | After LU decomp |

## Applications

### Linear System Solving
Triangular solvers are the final step in:
1. **LU Decomposition**: Ax = b → LUx = b → Ly = b, Ux = y
2. **Cholesky Decomposition**: Ax = b → LL^Tx = b → Ly = b, L^Tx = y
3. **QR Decomposition**: Ax = b → QRx = b → Rx = Q^Tb

### Iterative Methods
- Gauss-Seidel method
- SOR (Successive Over-Relaxation)
- Jacobi iterations

### Matrix Inversion
- Computing A^(-1) by solving AX = I
- Column-by-column using triangular solvers

### Optimization
- Newton's method in optimization
- Trust-region methods
- Quasi-Newton methods

## Numerical Considerations

### Stability
- **Forward Substitution**: Stable if L is well-conditioned
- **Backward Substitution**: Stable if U is well-conditioned
- **Pivoting**: Not needed for triangular systems
- **Condition Number**: κ(L) = ||L|| ||L^(-1)||

### Error Analysis
```matlab
% Residual: r = b - Lx
residual = b - L * x;
relative_residual = norm(residual) / norm(b);

% Backward error: ||r|| / ||b||
backward_error = norm(residual) / norm(b);

% Forward error: ||x_true - x_computed|| / ||x_true||
% (requires known true solution)
```

### Common Issues
1. **Zero Diagonal**: Matrix is singular, no solution
2. **Small Diagonal**: Large condition number, unstable
3. **Round-off Error**: Accumulates in long chains
4. **Overflow/Underflow**: Very large or small values

## Testing Strategy

### Test Cases
```matlab
% Test 1: Simple 2×2 lower triangular
L = [2, 0; 3, 4];
b = [2; 5];
x = forward_substitution(L, b);
% Expected: x = [1; 0.5]

% Test 2: Simple 2×2 upper triangular
U = [2, 3; 0, 4];
b = [5; 4];
x = backward_substitution(U, b);
% Expected: x = [0.5; 1]

% Test 3: Identity matrix
I = eye(3);
b = [1; 2; 3];
x = forward_substitution(I, b);
% Expected: x = b

% Test 4: Random triangular matrix
n = 100;
L = tril(rand(n));
b = rand(n, 1);
x = forward_substitution(L, b);
residual = norm(b - L*x);
assert(residual < 1e-10);
```

## Learning Outcomes
This project demonstrates:
- Understanding of triangular system structure
- Efficient algorithm implementation
- Numerical stability awareness
- MATLAB programming proficiency
- Software testing practices

## Real-World Usage
Triangular solvers are ubiquitous in:
- **Scientific Computing**: LAPACK, BLAS libraries
- **Engineering Software**: MATLAB, SciPy, NumPy
- **CAD/CAE**: Structural analysis, CFD
- **Machine Learning**: Solving normal equations
- **Finance**: Portfolio optimization
- **Statistics**: Linear regression, ANOVA

## Performance Optimization

### MATLAB Optimizations
```matlab
% BAD: Loop-based
for i = 1:n
    for j = 1:i-1
        x(i) = x(i) - L(i,j) * x(j);
    end
end

% GOOD: Vectorized
for i = 1:n
    x(i) = (b(i) - L(i,1:i-1) * x(1:i-1)) / L(i,i);
end

% BEST: Use built-in (when possible)
x = L \ b;  % MATLAB's optimized solver
```

### Cache Efficiency
- Access memory in order (row-major or column-major)
- Minimize cache misses
- Block algorithms for large matrices

## Comparison with Built-in MATLAB
```matlab
% Custom implementation
tic;
x1 = forward_substitution(L, b);
time1 = toc;

% MATLAB built-in (uses LAPACK)
tic;
x2 = L \ b;
time2 = toc;

% Verify equivalence
assert(norm(x1 - x2) < 1e-10);

fprintf('Custom: %.6f sec\n', time1);
fprintf('Built-in: %.6f sec\n', time2);
fprintf('Speedup: %.2fx\n', time1/time2);
```

## Extension Ideas
- **Sparse Matrices**: Optimize for sparse L/U
- **Parallel Implementation**: OpenMP, MPI
- **Block Algorithms**: Cache-aware blocking
- **Mixed Precision**: Using lower precision where safe
- **GPU Acceleration**: CUDA implementation

