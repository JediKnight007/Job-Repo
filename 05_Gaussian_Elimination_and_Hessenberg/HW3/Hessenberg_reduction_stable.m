function [Q, H] = Hessenberg_reduction_stable(A)
    [m, ~] = size(A);
    Q = eye(m);
    H = A;
    
    for k = 1:m-2
        x = H(k+1:m, k);
        e1 = zeros(length(x), 1);
        e1(1) = norm(x);
        
        v_k = x + sign(x(1)) * e1;
        v_k = v_k / norm(v_k);
        
        H(k+1:m, k:m) = H(k+1:m, k:m) - 2 * v_k * (v_k' * H(k+1:m, k:m));
        H(:, k+1:m) = H(:, k+1:m) - 2 * (H(:, k+1:m) * v_k) * v_k';
        
        Q(:, k+1:m) = Q(:, k+1:m) - 2 * (Q(:, k+1:m) * v_k) * v_k';
    end
end
