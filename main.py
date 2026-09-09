first_number = float(input("Enter the first number: "))
operation = input("Choose an operation (+, -, *, /): ")
second_number = float(input("Enter the second number: "))

if operation == "+":
    result = first_number + second_number
    print("Result:", result)
elif operation == "-":
    result = first_number - second_number
    print("Result:", result)
elif operation == "*":
    result = first_number * second_number
    print("Result:", result)
elif operation == "/":
    if second_number == 0:
        print("Error: division by zero is not allowed.")
    else:
        result = first_number / second_number
        print("Result:", result)
else:
    print("Error: choose one of these operations: +, -, *, /.")
