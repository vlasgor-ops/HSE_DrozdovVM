import random

step = random.randint(3, 5)
array = list(range(10, 250000001, step))
random_numbers = [random.randint(0, 100) for _ in range(10)]
def linear_search(array, target):
    for i, value in enumerate(array):
        if value == target:
            return i
    return -1
def binary_search(array, target):
    left = 0
    right = len(array) - 1
    while left <= right:
        mid = (left + right) // 2
        if array[mid] == target:
            return mid
        elif array[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
import time

target = random_numbers[0]

start_time = time.time()
linear_result = linear_search(array, target)
linear_time = time.time() - start_time

start_time = time.time()
binary_result = binary_search(array, target)
binary_time = time.time() - start_time

print("Linear search result:", linear_result)
print("Linear search time:", linear_time)

print("Binary search result:", binary_result)
print("Binary search time:", binary_time)
