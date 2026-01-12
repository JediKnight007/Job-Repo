% Test script for verifying the properties of QR decomposition
% using the modified Gram-Schmidt process

% Generate a random matrix A
m = 4;  % Number of rows
n = 3;  % Number of columns
A = randn(m, n);

% Perform QR decomposition using modified Gram-Schmidt
[Q, R] = myQR(A);

% Verify property (i) A = QR
disp(norm(A - Q * R));  % Should be close to 0

% Verify property (ii) Q' * Q = I
disp(norm(Q' * Q - eye(n)));  % Should be close to 0

% Verify property (iii) R is upper triangular
disp(norm(tril(R, -1)));  % Should be close to 0