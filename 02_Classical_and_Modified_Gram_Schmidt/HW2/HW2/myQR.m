function [Q,R]=myQR(A)
    % QR decomposition using modified Gram-Schmidt process
    % Given: A (m x n matrix)
    % Find: Q (a m x n orthogonal matrix), R (an n x n upper triangular matrix)

    [m,n]=size(A);   % Find dimensions of the matrix
    Q=zeros(m,n);    % Initialize Q
    R=zeros(n,n);    % Initialize R

    % Mod Gram-Schmidt process
    for j=1:n
        x=A(:,j);  % Start with current column of A
        for i=1:(j-1)
            R(i,j)=Q(:,i)' * x;  % Find projection coefficient
            x = x-R(i,j)*Q(:,i);  % Subtract projection from x
        end
        R(j,j) = sqrt(x'*x); % Find norm of remaining vector
        Q(:,j)=x/R(j,j);  % Norm vector to find q_k
    end
end