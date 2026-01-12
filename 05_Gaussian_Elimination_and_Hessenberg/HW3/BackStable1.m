num_matrices = 100;
matrix_size = 50;
residuals_no_pivot = zeros(num_matrices, 1);
residuals_with_pivot = zeros(num_matrices, 1);

for i = 1:num_matrices
    A = randn(matrix_size);
    
    [L_no_pivot, U_no_pivot] = Gaussian_elimination(A);
    A_reconstructed_no_pivot = L_no_pivot * U_no_pivot;
    residuals_no_pivot(i) = norm(A - A_reconstructed_no_pivot) / norm(A);
    
    [L_with_pivot, U_with_pivot, p] = Gaussian_elimination_pivot(A);
    A_permuted = A(p, :);
    A_reconstructed_with_pivot = L_with_pivot * U_with_pivot;
    residuals_with_pivot(i) = norm(A_permuted - A_reconstructed_with_pivot) / norm(A_permuted);
end

fprintf('Average relative residual without pivoting: %e\n', mean(residuals_no_pivot));
fprintf('Average relative residual with pivoting: %e\n', mean(residuals_with_pivot));

if mean(residuals_no_pivot) < 1e-14
    fprintf('Gaussian elimination without pivoting appears to be backward stable.\n');
else
    fprintf('Gaussian elimination without pivoting may not be backward stable.\n');
end

if mean(residuals_with_pivot) < 1e-14
    fprintf('Gaussian elimination with pivoting appears to be backward stable.\n');
else
    fprintf('Gaussian elimination with pivoting may not be backward stable.\n');
end
