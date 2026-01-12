function [L, U, p] = Gaussian_elimination_pivot(A)
    [n, ~] = size(A);
    U = A;
    L = eye(n);
    p = 1:n;
    
    for k = 1:n-1
        [~, maxIdx] = max(abs(U(k:n, k)));
        maxIdx = maxIdx + k - 1;
        
        if maxIdx ~= k
            U([k, maxIdx], :) = U([maxIdx, k], :);
            L([k, maxIdx], 1:k-1) = L([maxIdx, k], 1:k-1);
            p([k, maxIdx]) = p([maxIdx, k]);
        end
        
        for i = k+1:n
            L(i, k) = U(i, k) / U(k, k);
            U(i, :) = U(i, :) - L(i, k) * U(k, :);
        end
    end
end