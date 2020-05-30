# Higher Dimensions
Graph Definition:
L = /
committer= C, /
issueAssignee = I_A
issueReporter = I_R, 
patchApprover = A, 
reviewOwner/patchAuthor/patchReviewer R, 
Ownership O, 
files = F, 
issues = I
E_m = // intra-layer edges
           C x C ^= c_i and c_j committed to the same file
           O x O ^= ownership of c_i to f_j, link between f_j to i_k
           F x F ^= dependency of f_i on f_j or co-commit between f_i and f_j
           R x R ^= review comment from r_i to r_j
           I_R x I_R ^= i_r1 and i_r2 commented to the same issue report
           // inter-layer edges
           C x I_R ^= c_i is i_r_j
           C x R ^= c_i is R_j
           C x I_A ^= c_i is I_A
           C x A ^= c_i is a_j
           R x I_R ^= R_i is i_r_j
           R x I_A ^= R_i is i_a_j
           R x A ^= R_i is a_j
           I_R x I_A ^= i_r_i is I_A
           I_R x A ^= i_r_i is a_j
           I_A x A ^= i_a_i is a_j
           C x O ^= c_i is o_j
           F x O ^= f_i is o_j
           I x O ^= i_i is o_j
     

