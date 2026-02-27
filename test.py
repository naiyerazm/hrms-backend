def test_decorator(func):
    def wrapper(param):
        return param * func(param)
    return wrapper
 
@test_decorator
def cubes(param):
    return param * param

print(cubes(5))