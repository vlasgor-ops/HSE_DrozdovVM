"1. Функция вычисления факториала числа (произведение натуральных чисел от 1 до n). Принимает в качестве аргумента число, возвращает его факториал"
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
print(factorial(36))

"2.Поиск наибольшего числа из трёх. Принимает в качестве аргумента кортеж из трёх чисел, возвращает наибольшее из них"
def max_of_three(num1, num2, num3):
    if num1 >= num2 and num1 >= num3:
        return num1
    elif num2 >= num1 and num2 >= num3:
        return num2
    else:
        return num3
print(max_of_three(10, 5, 8))
print(max_of_three(7, 15, 9))
print(max_of_three(4, 5, 6))

"3. Расчёт площади прямоугольного треугольника. Принимает в качестве аргумента размер двух катетов треугольника. Возвращает площадь треугольника"
def triangle_area(base, height):
    area = 0.5 * base * height
    return area
print(triangle_area(8, 6))


