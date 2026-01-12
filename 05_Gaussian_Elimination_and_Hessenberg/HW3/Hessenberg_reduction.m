function [Q, H] = Hessenberg_reduction(A)
    n = size(A, 1);
    Q = eye(n);
    H = A;
    
    for k = 1:n-2
        x = H(k+1:n, k);
        e1 = zeros(length(x), 1); e1(1) = 1;
        v = sign(x(1)) * norm(x) * e1 + x;
        v = v / norm(v);
        
        H(k+1:n, k:n) = H(k+1:n, k:n) - 2 * v * (v' * H(k+1:n, k:n));
        H(:, k+1:n) = H(:, k+1:n) - 2 * (H(:, k+1:n) * v) * v';
        
        Q(k+1:n, :) = Q(k+1:n, :) - 2 * v * (v' * Q(k+1:n, :));
    end
    H = triu(H, -1); 
end
