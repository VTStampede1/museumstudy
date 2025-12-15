import pandas as pd

df = pd.read_excel('Экспонаты, общий.xlsx')

cols = ['Первичные актанты', 'Вторичные актанты']

# 1. Выбираем столбцы
# 2. stack() превращает их в один длинный список
# 3. value_counts() считает повторы
total_counts = df[cols].stack().value_counts()

print("Самые частые значения среди всех выбранных столбцов:")
print(total_counts.head(5))
