matrix_sizes = [4, 50];
num_matrices = 100;

for n = matrix_sizes
    residuals_initial = zeros(num_matrices, 1);
    residuals_stable = zeros(num_matrices, 1);
    
    for i = 1:num_matrices
        A = randn(n);
        
        [Q_initial, H_initial] = Hessenberg_reduction(A);
        residuals_initial(i) = norm(A - Q_initial * H_initial * Q_initial') / norm(A);
        
        [Q_stable, H_stable] = Hessenberg_reduction_stable(A);
        residuals_stable(i) = norm(A - Q_stable * H_stable * Q_stable') / norm(A);
    end
    
    fprintf('Matrix size %dx%d:\n', n, n);
    fprintf('  Average relative residual (initial algorithm): %e\n', mean(residuals_initial));
    fprintf('  Average relative residual (stable algorithm): %e\n', mean(residuals_stable));
    
    if mean(residuals_initial) < 1e-14
        fprintf('  Initial algorithm appears to be backward stable.\n');
    else
        fprintf('  Initial algorithm may not be backward stable.\n');
    end

    if mean(residuals_stable) < 1e-14
        fprintf('  Stable algorithm appears to be backward stable.\n');
    else
        fprintf('  Stable algorithm may not be backward stable.\n');
    end
end
