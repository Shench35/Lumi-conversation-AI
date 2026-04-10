nums = [1,2,3,4,5,6,7,8,9]
low = 0
high = len(nums)-1

n = int(input("Enter number here: "))
while low <= high:
    mid = (low + high) // 2
    if nums[mid] == n:
        print(n)
        break

    elif nums[mid] > n:
        high = mid + 1

    elif nums[mid] < n :
        low = mid - 1
    else:
        print("number not found")
        break


