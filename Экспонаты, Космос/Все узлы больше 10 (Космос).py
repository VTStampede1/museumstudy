import pandas as pd
from collections import Counter

# 1. Загрузка данных
file_path = 'Экспонаты, Космос.xlsx'
df = pd.read_excel(file_path)

# --- ЭТАП 1: Подсчет частотности на "сырых" данных (до ffill) ---

def clean_text(text):
    if pd.isna(text):
        return None
    # Экранируем кавычки и чистим пробелы
    cleaned = str(text).strip().replace('"', '\\"').replace('\n', ' ')
    # Если после очистки осталась пустая строка - возвращаем None
    return cleaned if cleaned else None

all_raw_values = []

# Извлекаем значения только из тех ячеек, где они реально написаны
# dropna() гарантирует, что мы не считаем "пустоту" и не считаем "протянутые" значения
raw_d = df['Первичные актанты'].apply(clean_text).dropna().tolist()
raw_f = df['Вторичные актанты'].apply(clean_text).dropna().tolist()

# Объединяем списки
all_raw_values = raw_d + raw_f

# Считаем
counts = Counter(all_raw_values)
THRESHOLD = 10

# Создаем множество допустимых значений
valid_nodes = {val for val, count in counts.items() if count > THRESHOLD}

print(f"Подсчет завершен без ffill.")
print(f"Всего значений встретилось: {len(counts)}")
print(f"Прошли порог (> {THRESHOLD}): {len(valid_nodes)}")
# Для отладки можно раскомментировать строку ниже:
# print("Популярные значения:", valid_nodes)


# --- ЭТАП 2: Восстановление структуры и генерация связей ---

# Теперь делаем ffill, чтобы понять иерархию (какой F относится к какому D, и какой D к какому B)
cols_to_fill = ['Название предмета', 'Первичные актанты', 'Связь с первичным актантом']
df[cols_to_fill] = df[cols_to_fill].ffill()

output_lines = []
seen_lines = set()

for index, row in df.iterrows():
    # Получаем значения из уже "протянутой" таблицы
    node_b = clean_text(row['Название предмета'])
    
    node_d = clean_text(row['Первичные актанты'])
    link_b_d = clean_text(row['Связь с первичным актантом'])
    
    node_f = clean_text(row['Вторичные актанты'])
    link_d_f = clean_text(row['Связь со вторичным актантом'])
    
    # Логика формирования связей:
    
    # 1. Связь B -> D
    # Строим, если:
    # a) D существует (не None)
    # b) D входит в список популярных (valid_nodes)
    if node_b and node_d and (node_d in valid_nodes):
        label = link_b_d if link_b_d else ""
        line = f'"{node_b}" -> "{node_d}" [label="{label}"];'
        
        if line not in seen_lines:
            seen_lines.add(line)
            output_lines.append(line)
            
    # 2. Связь D -> F
    # Строим, если:
    # a) D существует и F существует
    # b) D популярен (иначе у нас будет стрелка из ниоткуда, так как ветка B->D не создалась)
    # c) F популярен (условие задачи)
    if node_d and node_f:
        if (node_d in valid_nodes) and (node_f in valid_nodes):
            label = link_d_f if link_d_f else ""
            line = f'"{node_d}" -> "{node_f}" [label="{label}"];'
            
            if line not in seen_lines:
                seen_lines.add(line)
                output_lines.append(line)

# Сохранение
with open('Космос больше 10 список.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"Готово! Сгенерировано строк: {len(output_lines)}")
