function [L, U] = Gaussian_elimination(A)
    [n, ~] = size(A);
    U = A;
    L = eye(n); 
    
    for k = 1:n-1
        for i = k+1:n
            L(i,k) = U(i,k) / U(k,k);
            U(i,:) = U(i,:) - L(i,k) * U(k,:);
        end
    end
end