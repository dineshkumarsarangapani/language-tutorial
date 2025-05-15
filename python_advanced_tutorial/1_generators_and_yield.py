# 1. Generators and the `yield` Keyword

# --- What are Generators? ---
# Generators are a special kind of iterator in Python. They allow you to iterate
# over a potentially large sequence of data without creating the entire sequence
# in memory at once. This is achieved using the `yield` keyword.

# --- How does `yield` work? ---
# When a function contains `yield`, it becomes a generator function.
# Instead of returning a single value with `return`, `yield` produces a series
# of values. Each time `yield` is encountered, the function's state is paused,
# and the yielded value is sent to the caller. When the generator is asked for
# the next value, execution resumes from where it left off.

# --- Example: A simple number generator ---
def count_up_to(max_num):
    """Generates numbers from 1 up to max_num."""
    count = 1
    while count <= max_num:
        yield count  # Pauses here and sends 'count' back
        count += 1   # Resumes here on next call to next()

# Using the generator
print("--- Simple Number Generator ---")
counter_gen = count_up_to(5)

print(next(counter_gen))  # Output: 1
print(next(counter_gen))  # Output: 2
print(next(counter_gen))  # Output: 3

# You can also iterate over a generator using a for loop
print("\\n--- Iterating with a for loop ---")
for number in count_up_to(3):
    print(number)
# Output:
# 1
# 2
# 3

# --- Example: Generating Fibonacci numbers ---
# This is a classic example where generators are useful, as the sequence can be infinite.
def fibonacci_sequence(limit):
    """Generates Fibonacci numbers up to a certain limit."""
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

print("\\n--- Fibonacci Sequence Generator ---")
fib_gen = fibonacci_sequence(100)
for num in fib_gen:
    print(num, end=" ")  # Output: 0 1 1 2 3 5 8 13 21 34 55 89
print("\\n")

# --- Why use Generators? ---
# 1. Memory Efficiency: Great for large datasets as they produce items one at a time.
# 2. Infinite Sequences: Can represent sequences that are too large to store (or infinite).
# 3. Pipelining: Can be used to create efficient data processing pipelines.

# --- Generator Expressions (Similar to list comprehensions) ---
print("--- Generator Expression ---")
squares_gen = (x*x for x in range(1, 6)) # Note the parentheses make it a generator expression
print(f"Generator object: {squares_gen}")

for sq in squares_gen:
    print(sq)
# Output:
# 1
# 4
# 9
# 16
# 25

print("\\nIf you try to print the generator object directly, you get its representation:")
print(count_up_to(3))
# Output: <generator object count_up_to at 0x...> (address will vary)

print("\\nTo get all values at once (losing some memory benefits for large sequences):")
print(list(count_up_to(5))) # Output: [1, 2, 3, 4, 5]

# --- Key Takeaways for `yield` and Generators ---
# - `yield` turns a function into a generator.
# - Generators produce items on demand, saving memory.
# - They pause and resume their state between `yield` statements.
# - Can be consumed by `next()` or a `for` loop. 