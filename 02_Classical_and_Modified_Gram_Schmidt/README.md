# Classical and Modified Gram-Schmidt QR Decomposition

## Project Overview
This project implements and compares two fundamental numerical linear algebra algorithms: Classical Gram-Schmidt and Modified Gram-Schmidt orthogonalization methods for QR decomposition. The implementation includes stability analysis and performance comparison of both approaches.

## Technical Skills Demonstrated

### Numerical Linear Algebra
- **QR Decomposition**: Implementation of matrix factorization into orthogonal (Q) and upper triangular (R) matrices
- **Gram-Schmidt Orthogonalization**: Both classical and modified variants
- **Numerical Stability Analysis**: Testing and comparing backward stability of algorithms

### Mathematical Concepts
- Orthogonalization processes
- Matrix decomposition techniques
- Numerical stability and conditioning
- Floating-point arithmetic precision
- Error analysis in numerical methods

## Project Structure
```
HW2/
├── myQR.m              # Main QR decomposition implementation
├── classical.m         # Classical Gram-Schmidt algorithm
├── semiology.m         # Modified Gram-Schmidt algorithm
├── Test2.m             # Test suite
└── myQR.asv            # Auto-save backup
```

## Key Features

### Algorithm Implementations
1. **Classical Gram-Schmidt (CGS)**
   - Traditional orthogonalization approach
   - Direct computation of orthogonal vectors
   - Prone to numerical instability with ill-conditioned matrices

2. **Modified Gram-Schmidt (MGS)**
   - Numerically stable variant
   - Sequential orthogonalization
   - Better performance with ill-conditioned matrices

3. **Stability Analysis**
   - Backward error computation
   - Comparison of numerical accuracy
   - Condition number sensitivity testing

## Technical Environment
- **Language**: MATLAB
- **Domain**: Numerical Linear Algebra
- **Libraries**: MATLAB built-in matrix operations

## Mathematical Background

### QR Decomposition
For a matrix A (m×n), QR decomposition finds:
- Q: Orthogonal matrix (m×n) where Q^T Q = I
- R: Upper triangular matrix (n×n)
- Such that: A = QR

### Applications
- Solving least squares problems
- Computing eigenvalues
- Signal processing
- Computer graphics (camera transformations)
- Machine learning (PCA, linear regression)

## Skills & Technologies
- **MATLAB Programming**: Advanced matrix operations and vectorization
- **Numerical Methods**: Understanding of numerical stability and precision
- **Algorithm Analysis**: Comparing computational complexity and accuracy
- **Mathematical Software**: Scientific computing tools
- **Error Analysis**: Floating-point arithmetic and round-off errors

## Key Algorithms

### Classical Gram-Schmidt
```
For j = 1 to n:
    For i = 1 to j-1:
        R(i,j) = Q(:,i)' * A(:,j)
        A(:,j) = A(:,j) - R(i,j) * Q(:,i)
    R(j,j) = norm(A(:,j))
    Q(:,j) = A(:,j) / R(j,j)
```

### Modified Gram-Schmidt
```
For j = 1 to n:
    R(j,j) = norm(A(:,j))
    Q(:,j) = A(:,j) / R(j,j)
    For i = j+1 to n:
        R(j,i) = Q(:,j)' * A(:,i)
        A(:,i) = A(:,i) - R(j,i) * Q(:,j)
```

## Performance Metrics
- **Orthogonality**: Measuring how close Q^T Q is to identity matrix
- **Residual**: Computing ||A - QR|| to verify accuracy
- **Backward Stability**: Analyzing numerical error propagation
- **Computational Cost**: Comparing operation counts

## Learning Outcomes
This project demonstrates:
- Deep understanding of matrix decomposition techniques
- Ability to implement and analyze numerical algorithms
- Recognition of numerical stability issues
- Practical experience with scientific computing
- Comparison of theoretical vs. practical algorithm performance

## Use Cases in Industry
- **Data Science**: Principal Component Analysis (PCA)
- **Computer Vision**: Camera calibration and 3D reconstruction
- **Signal Processing**: Filter design and system identification
- **Machine Learning**: Linear regression and dimensionality reduction
- **Engineering**: Solving overdetermined systems of equations

