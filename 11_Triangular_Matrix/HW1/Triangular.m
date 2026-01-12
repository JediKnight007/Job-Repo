function x = Triangular(A, b)
    % A is the given triangular matrix
    % b is the right hand side vector
    
    % Get the size of the matrix A, made this since it was repeated a
    %lot during the loop and it became easier as a singlar labeled value
    n = size(A, 1);
    
    % Solution vector xn, from the 
    % last equation ast equation rnnxn = bn. This is the initialization
    % where the vector is filled with default values of 0
    x = zeros(n, 1);
    
    % Per each i element, the program is essentially dividing b by A(i)
    % iteratively, ex. x = b/A, and adding up each individual terms to get
    % the final value of x(i). The loop goes iterates i from 
    % n to 1, decreasing by 1. create smaller system Rn−1xn−1 = bn−1 by
    % removing the known values from the system, as shown when the 
    % known values are removed from b(i).
    for i = n:-1:1
        known_val = 0;

        % Interior loop that creates the total sum of each Triangular
        % Matrix Value and x(j) to form the total of the known values
        for j = i+1:n
            known_val = known_val + (x(j) * A(i, j));
        end

        % Dividing the x(i) term by A is the last step, as the original
        % states that Ax = b, hence x(i) = b without the known values 
        % divided by A
        x(i) = (b(i) - known_val) / A(i, i);
    end
end
