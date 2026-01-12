num_trials = 100;
m = 50;
errors = zeros(num_trials, 1);

for i = 1:num_trials
    [Q, ~] = qr(rand(m));
    A = Q * diag(rand(m, 1)) * Q';
    R = chol_fact(A);
    
    errors(i) = norm(A - R' * R, 'fro') / norm(A, 'fro');
end
disp(R)
disp('Average relative error for Cholesky factorization (50):');
disp(mean(errors));

num_trials = 100;
m = 100;
errors = zeros(num_trials, 1);

for i = 1:num_trials
    [Q, ~] = qr(rand(m));
    A = Q * diag(rand(m, 1)) * Q';
    R = chol_fact(A);
    
    errors(i) = norm(A - R' * R, 'fro') / norm(A, 'fro');
end
disp(R)
disp('Average relative error for Cholesky factorization (100):');
disp(mean(errors));