# Gaussian Elimination and Hessenberg Reduction

## Project Overview
This project implements fundamental numerical linear algebra algorithms for matrix decomposition and transformation, including Gaussian elimination with and without pivoting, Hessenberg reduction, and Cholesky factorization. It includes rigorous backward stability analysis to understand numerical behavior.

## Technical Skills Demonstrated

### Numerical Linear Algebra
- **Gaussian Elimination**: Solving linear systems Ax = b
- **LU Decomposition**: With and without partial pivoting
- **Hessenberg Reduction**: Reducing matrices to upper Hessenberg form
- **Cholesky Factorization**: Decomposition for positive definite matrices
- **Stability Analysis**: Testing backward and forward error

### Mathematical Concepts
- Matrix factorizations (LU, Cholesky)
- Householder transformations
- Numerical stability and conditioning
- Pivoting strategies
- Error propagation analysis
- Positive definiteness

## Project Structure
```
HW3/
├── Gaussian_elimination.m               # Basic Gaussian elimination
├── Gaussian_elimination_pivot.m         # With partial pivoting
├── Hessenberg_reduction.m               # Hessenberg transformation
├── Hessenberg_reduction_stable.m        # Numerically stable version
├── check_backward_stability_Hessenberg.m # Stability testing
├── chol_fact.m                          # Cholesky factorization
├── chol_test.m                          # Cholesky testing
├── Test.m                               # General test suite
├── BackStable1.m                        # Backward stability tests
└── HW3.zip                              # Archived submission
```

## Key Features

### 1. Gaussian Elimination
**Basic Implementation**
- Row reduction to upper triangular form
- Back substitution for solution
- No pivoting (numerically unstable for some matrices)

**With Partial Pivoting**
- Selects largest pivot element
- Reduces growth factor
- Improves numerical stability
- Prevents division by small numbers

### 2. Hessenberg Reduction
Transforms a matrix to upper Hessenberg form (zeros below first subdiagonal):
```
Original:        Hessenberg:
[* * * *]       [* * * *]
[* * * *]  -->  [* * * *]
[* * * *]       [0 * * *]
[* * * *]       [0 0 * *]
```

**Applications:**
- Eigenvalue computation (QR algorithm)
- Solving matrix equations
- Numerical stability improvements

**Implementation Variants:**
- Basic version
- Stable version using Householder reflections

### 3. Cholesky Factorization
For symmetric positive definite matrix A:
- Decompose A = LL^T where L is lower triangular
- More efficient than LU (half the operations)
- Numerically stable
- Used in optimization and simulation

### 4. Backward Stability Testing
Measures how close the computed solution is to the exact solution of a nearby problem:
```matlab
backward_error = norm(A - computed_A) / norm(A)
```

## Technical Implementation

### Gaussian Elimination Algorithm
```matlab
% Forward elimination
for k = 1:n-1
    for i = k+1:n
        factor = A(i,k) / A(k,k);
        A(i,k:n) = A(i,k:n) - factor * A(k,k:n);
        b(i) = b(i) - factor * b(k);
    end
end

% Back substitution
x(n) = b(n) / A(n,n);
for i = n-1:-1:1
    x(i) = (b(i) - A(i,i+1:n) * x(i+1:n)) / A(i,i);
end
```

### Partial Pivoting Strategy
```matlab
% Find pivot
[~, pivot_row] = max(abs(A(k:n, k)));
pivot_row = pivot_row + k - 1;

% Swap rows
A([k, pivot_row], :) = A([pivot_row, k], :);
b([k, pivot_row]) = b([pivot_row, k]);
```

### Hessenberg Reduction (Householder)
```matlab
for k = 1:n-2
    % Create Householder reflector for column k
    v = A(k+1:n, k);
    v(1) = v(1) + sign(v(1)) * norm(v);
    v = v / norm(v);
    
    % Apply H = I - 2vv^T from both sides
    A(k+1:n, k:n) = A(k+1:n, k:n) - 2*v*(v'*A(k+1:n, k:n));
    A(:, k+1:n) = A(:, k+1:n) - 2*(A(:, k+1:n)*v)*v';
end
```

### Cholesky Factorization
```matlab
L = zeros(n);
for j = 1:n
    L(j,j) = sqrt(A(j,j) - L(j,1:j-1)*L(j,1:j-1)');
    for i = j+1:n
        L(i,j) = (A(i,j) - L(i,1:j-1)*L(j,1:j-1)') / L(j,j);
    end
end
```

## Technical Environment
- **Language**: MATLAB
- **Domain**: Numerical Linear Algebra
- **Precision**: IEEE 754 double precision (64-bit)

## Numerical Considerations

### Stability Issues
1. **Division by Small Numbers**: Causes large errors (solved by pivoting)
2. **Subtractive Cancellation**: Loss of significant digits
3. **Growth Factor**: How much elements grow during elimination
4. **Condition Number**: Sensitivity to perturbations

### Pivoting Strategies Comparison
| Strategy | Stability | Cost | When to Use |
|----------|-----------|------|-------------|
| No Pivot | Unstable | Low | Dense, well-conditioned |
| Partial | Good | Medium | General purpose |
| Complete | Best | High | Ill-conditioned matrices |

### Complexity Analysis
- **Gaussian Elimination**: O(n³) flops
- **Cholesky**: O(n³/3) flops (2x faster than LU)
- **Hessenberg**: O(n³) flops
- **Back Substitution**: O(n²) flops

## Skills & Technologies
- **MATLAB Programming**: Matrix operations, vectorization
- **Numerical Methods**: Understanding of stability and accuracy
- **Algorithm Implementation**: Translating mathematical algorithms to code
- **Testing & Validation**: Comprehensive test suite development
- **Error Analysis**: Quantifying numerical errors

## Applications

### Scientific Computing
- **Linear Systems**: Solving engineering problems
- **Least Squares**: Data fitting and regression
- **Eigenvalue Problems**: QR algorithm initialization
- **Optimization**: Newton's method, trust-region methods

### Engineering
- **Structural Analysis**: Finite element method
- **Circuit Simulation**: SPICE-type simulators
- **Control Theory**: State-space analysis
- **Signal Processing**: Filter design

### Data Science
- **Linear Regression**: Normal equations solution
- **PCA**: Covariance matrix eigendecomposition
- **Kalman Filtering**: State estimation
- **Gaussian Processes**: Covariance matrix inversion

## Testing & Validation
The project includes comprehensive tests for:
- Correctness: Comparing with MATLAB built-ins
- Stability: Measuring backward error
- Accuracy: Residual analysis
- Edge cases: Singular, ill-conditioned matrices
- Performance: Timing comparisons

## Key Insights

### When to Use Each Method
1. **LU without Pivoting**: Dense, well-conditioned matrices only
2. **LU with Pivoting**: General sparse/dense linear systems
3. **Cholesky**: Positive definite systems (faster, more stable)
4. **Hessenberg**: Pre-processing for eigenvalue algorithms

### Stability Rankings
1. **Most Stable**: Householder-based methods
2. **Very Stable**: Cholesky (for SPD matrices)
3. **Stable**: Gaussian elimination with partial pivoting
4. **Unstable**: Gaussian elimination without pivoting

## Learning Outcomes
This project demonstrates:
- Deep understanding of matrix factorization algorithms
- Ability to implement numerically stable algorithms
- Knowledge of error analysis and numerical precision
- Experience with scientific computing best practices
- Understanding of computational complexity

## Real-World Impact
These algorithms are used in:
- **Engineering Software**: MATLAB, SciPy, NumPy
- **CAD Tools**: Structural simulation
- **Machine Learning Libraries**: Linear models
- **Finance**: Portfolio optimization
- **Physics Simulation**: Molecular dynamics, CFD

## Performance Considerations
- **Memory Access Patterns**: Cache-friendly implementation
- **Vectorization**: Leveraging SIMD operations
- **Blocking**: Tiling for large matrices
- **Sparse Matrices**: Different algorithms for sparse systems

