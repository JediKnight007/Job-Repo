function [Q_C,R_C]=classical(A)
    % QR decomposition using classical Gram-Schmidt process
    % Given: A (m x n matrix)
    % Find: Q (a m x n orthogonal matrix), R (an n x n upper triangular matrix)
    [m,n]=size(A);
    Q_C=zeros(m, n);
    R_C=zeros(n, n);

    for l=1:n
        % Step 1: Start with current column of A
        v=A(:,l);
        % Step 2: Subtract projections onto previous q_j
        for j=1:l-1
            R_C(j,l)=Q_C(:,j)'*v;
            v=v-R_C(j,l)*Q_C(:,j);
        end
    
        % Step 3: Normalize vector to get q_k
        R_C(l,l)=sqrt(v'*v);
        Q_C(:,l)=v/R_C(l,l);
    end