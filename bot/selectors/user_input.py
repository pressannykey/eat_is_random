import re

prepositions = ['с', 'со', 'под', 'в', 'во', 'от', 'из', 'и', 'без']


def get_user_input(raw_input):
    # обрабатываем пользовательский ввод
    dish = raw_input
    if not dish:
        return []
    dishes = [dish]
    split_dishes = re.split(r'[\s-]+', dish)
    for dish in split_dishes:
        if dish not in prepositions and dish not in dishes:
            dishes.append(dish)

    print(dishes)
    return dishes
