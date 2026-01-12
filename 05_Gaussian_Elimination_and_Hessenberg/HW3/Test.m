epsilon = 1e-20;
A = [1 0 1; 0 epsilon 2; 1 2 5];

[L_no_pivot, U_no_pivot] = Gaussian_elimination(A);
[L_pivot, U_pivot, p] = Gaussian_elimination_pivot(A);

disp('Without Pivoting:')
disp('L ='), disp(L_no_pivot)
disp('U ='), disp(U_no_pivot)

disp('With Pivoting:')
disp('L ='), disp(L_pivot)
disp('U ='), disp(U_pivot)
disp('Permutation vector p ='), disp(p)