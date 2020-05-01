import re

prepositions = ["с", "со", "под", "в", "во", "от", "из", "и", "без"]


def get_user_input(raw_input):
    # обрабатываем пользовательский ввод
    if not raw_input:
        return [], []
    dishes = [raw_input]
    split_dishes = re.split(r'[\s-]+', raw_input)

    for dish in split_dishes:
        if dish not in prepositions and dish not in dishes:
            dishes.append(dish)

    return raw_input, dishes
