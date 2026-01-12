rng(0);  % For reproducibility
[U, ~] = qr(randn(80));  % Random orthogonal matrix
[V, ~] = qr(randn(80));  % Random orthogonal matrix
S = diag(2.^(-1:-1:-80));  % Diagonal matrix with exponentially spaced entries
A = U * S * V;  % Set A using SVD

% Classical Gram-Schmidt QR factorization
[QC, RC] = classical(A);

% Modified Gram-Schmidt QR factorization
[QM, RM] = myQR(A);

% Plot diagonal entries of RC and RM in log-scale
semilogy(diag(R), 'x');
hold on;
semilogy(diag(R), 'o');
title('Diagonal Entries of RC and RM in Log Scale');
legend('Classical', 'Modified');
hold off;