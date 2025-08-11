
def calculate_average(numbers):
    # This has a bug - division by zero not handled
    total = sum(numbers)
    return total / len(numbers)

# This will crash
result = calculate_average([])
print(result)
