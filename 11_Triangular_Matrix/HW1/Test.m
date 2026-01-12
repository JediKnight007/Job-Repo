% Given matrix A (upper triangular) and vector b from part (a)
A = [1 2 3;
     0 6 4;
     0 0 6];

b = [1;
     1;
     3];

% Call the function to solve the system
x = Triangular(A, b);

% Display the solution
disp('Solution x:');
disp(x);