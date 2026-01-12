from imp_hw6 import equal_encoding, sum_pair, merge_k, ll_modes, bst_modes
from classes import ListNode, TreeNode
from convert import arr_to_listnode, listnode_to_arr, arr_to_bst

def test_sample():
    assert 2 == 1 + 1

def test_equal_encoding():
    #Comparing strings where one has duplicate character
    s1 = "truth"
    s2 = "truce"
    assert equal_encoding(s1, s2) is False
    #Comparing palindromes
    s1 = "dad"
    s2 = "bob"
    assert equal_encoding(s1, s2) is True
    #Comparing equal strings
    s1 = "hello"
    s2 = "hello"
    assert equal_encoding(s1, s2) is True
    #Comparing blank strings
    s1 = ""
    s2 = ""
    #Comparing palindrome with a space
    assert equal_encoding(s1, s2) is True
    s1 = "race car"
    s2 = "race car"
    #Comparing a string with a space then char vs a two spaced blank
    assert equal_encoding(s1, s2) is True
    s1 = " 3"
    s2 = "  "
    #Comparing two longer strings, both with repeating chars
    assert equal_encoding(s1, s2) is False
    s1 = "Mississippi"
    s2 = "New-Yorkers"
    assert equal_encoding(s1, s2) is False
    #Comparing strings with capital letters (hence why .lower() is present;T and t should be counted as duplicate)
    s1 = "Truth"
    s2 = "Truce"
    assert equal_encoding(s1, s2) is False

def test_sum_pair():
    nums = [3,2,4] 
    target = 6
    assert sum_pair(nums, target) == {1, 2}, "Test case 2 failed"
    #Standard Set and Target
    nums = [2,7,11,15] 
    target = 9
    assert sum_pair(nums, target) == {0, 1}, "Test case 2 failed"
    #assert sum_pair(nums, target) is {0,1}
    #Two Value in nums corresponding to target
    nums = [3,3] 
    target = 6
    assert sum_pair(nums, target) == {0, 1}, "Test case 2 failed"
    #Three values in nums to one target
    nums = [3, 6, 10] 
    target = 9
    assert sum_pair(nums, target) == {0, 1}, "Test case 2 failed"
    
def test_merge_k():
    #Standard 3 ListNodes
    list1 = arr_to_listnode([1,4,5])
    list2 = arr_to_listnode([1,3,4])
    list3 = arr_to_listnode([2,6])
    list4 = arr_to_listnode([1, 1, 2, 3, 4, 4, 5, 6])
    main_list = [list1, list2, list3]
    assert merge_k(main_list) == list4
    #3 ListNodes all with different lengths
    list1 = arr_to_listnode([1,4,5,7])
    list2 = arr_to_listnode([1,3,4])
    list3 = arr_to_listnode([2,6])
    list4 = arr_to_listnode([1, 1, 2, 3, 4, 4, 5, 6, 7])
    main_list = [list1, list2, list3]
    assert merge_k(main_list) == list4
    #3 ListNodes all empty
    list1 = arr_to_listnode([])
    list2 = arr_to_listnode([])
    list3 = arr_to_listnode([])
    list4 = arr_to_listnode([])
    main_list = [list1, list2, list3]
    assert merge_k(main_list) == list4
    #6 ListNodes with several more lists and values
    list1 = arr_to_listnode([1,4,5,7])
    list2 = arr_to_listnode([1,3,4])
    list3 = arr_to_listnode([2,6])
    list4 = arr_to_listnode([1,4,5,7,9,11])
    list5 = arr_to_listnode([2,6,7,8,9])
    list6 = arr_to_listnode([1,4])
    list7 = arr_to_listnode([1,1,1,1,2,2,3,4,4,4,4,5,5,6,6,7,7,7,8,9,9,11])
    main_list = [list1, list2, list3, list4, list5, list6]
    assert merge_k(main_list) == list7
    

def test_ll_modes():
    #ListNode with one mode
    list1 = arr_to_listnode([1,4,5,5,7])
    assert ll_modes(list1) == {5}
    #Multiple list nodes which are formed into a singular ListNode by merge_k, and then mode found (there are two modes)
    list1 = arr_to_listnode([1,4,5,7])
    list2 = arr_to_listnode([1,3,4])
    list3 = arr_to_listnode([2,6])
    main_list = [list1, list2, list3]
    noder = merge_k(main_list)
    assert ll_modes(noder) == {1,4}
    #Every element is the mode
    list1 = arr_to_listnode([1,1,4,4,5,5,7,7])
    assert ll_modes(list1) == {1, 4, 5, 7} 
    #Blank ListNode, should return blank set
    list1 = arr_to_listnode([])
    ll_modes(list1)
    assert ll_modes(list1) == set()

def test_bst_modes():
    #Tree containing One Mode
    list1 = arr_to_bst([5,4,8,3,4,7,9])
    print(list1)
    assert bst_modes(list1) == {4}
    #Tree containing Multiple Modes
    list1 = arr_to_bst([1,0,1,0,0,1,1,0])
    print(list1)
    assert bst_modes(list1) == {0,1}
    #Empty Tree
    list1 = arr_to_bst([])
    print(list1)
    assert bst_modes(list1) == set()
    #Streak at end = Mode, Tests if streak is caught
    list1 = arr_to_bst([5,4,8,3,4,8,8])
    print(list1)
    assert bst_modes(list1) == {8}