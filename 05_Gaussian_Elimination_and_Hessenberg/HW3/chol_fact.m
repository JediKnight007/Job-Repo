function R = chol_fact(A)
    n = size(A, 1);
    R = zeros(n);

    for i = 1:n
        for j = i:n
            if i == j
                R(i, j) = sqrt(A(i, i) - sum(R(i, 1:i-1).^2));
            else
                R(i, j) = (A(i, j) - sum(R(i, 1:i-1) .* R(j, 1:i-1))) / R(i, i);
            end
        end
    end
end