import csv
import random
import string
from tqdm import tqdm

def validate_perturbation(original, perturbed):
    return any(o != p for o, p in zip(original[1:], perturbed[1:]))

def perturb_field(row):
    original = row.copy()
    fields_to_perturb = [
        ('name', 0.3),
        ('id_num', 0.3),
        ('username', 0.3),
        ('signature', 0.3)
    ]
    
    for _ in range(10):
        field_order = random.sample(fields_to_perturb, len(fields_to_perturb))
        for field, prob in field_order:
            if random.random() > prob:
                continue
                
            original_value = row.copy()
            try:
                if field == 'name':
                    row[1] += random.choice(string.ascii_letters + string.digits)
                elif field == 'id_num':
                    pos = random.randint(0, 16)
                    row[3] = row[3][:pos] + str((int(row[3][pos]) + 1) % 10) + row[3][pos+1:]
                elif field == 'username':
                    if random.choice([True, False]):
                        row[4] = random.choice(string.digits) + row[4]
                    else:
                        char = random.choice('!@#$%^&*')
                        row[4] = row[4][:random.randint(1, len(row[4]))] + char + row[4][random.randint(1, len(row[4])):]
                elif field == 'signature':
                    if len(row[6]) > 0:
                        pos = random.randint(0, len(row[6])-1)
                        row[6] = row[6][:pos] + random.choice(string.ascii_letters + '+/') + row[6][pos+1:]
                
                if validate_perturbation(original, row):
                    return row, field
            except:
                row = original_value.copy()
        
        row[4] = '0' + row[4]
        return row, 'username'
    
    return row, None

if __name__ == "__main__":
    with open('original.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    perturbed = []
    disturbed = set()
    total = len(rows)
    
    selected = set(random.sample(range(1, 2001), 100))
    
    with tqdm(total=len(rows), desc="扰动数据", unit="行") as pbar:
        for idx, row in enumerate(rows):
            if int(row[0]) in selected:
                original = row.copy()
                for retry in range(3):
                    new_row, field = perturb_field(row.copy())
                    if validate_perturbation(original, new_row):
                        perturbed.append(new_row)
                        disturbed.add(int(row[0]))
                        print(f"成功扰动 序号：{row[0]} 字段：{field}")
                        break
                else:
                    print(f"警告：序号 {row[0]} 扰动失败，已强制修改")
                    disturbed.add(int(row[0]))
                    new_row[4] = '0' + new_row[4]
                    perturbed.append(new_row)
            else:
                perturbed.append(row)
            pbar.update(1)

    actual_disturbed = len(disturbed)
    if actual_disturbed < 100:
        need_more = 100 - actual_disturbed
        candidates = list(set(range(1, 2001)) - disturbed)
        additional = random.sample(candidates, need_more)
        for row in perturbed:
            if int(row[0]) in additional:
                original = row.copy()
                row[4] = '0' + row[4]
                disturbed.add(int(row[0]))
                print(f"补充扰动 序号：{row[0]}")

    with open('polluted.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(perturbed)

    print(f"成功扰动 {len(disturbed)} 行")
    print("被扰动的序号:", sorted(disturbed))
    print(f"最终计算值 {'_'.join(map(str, sorted(disturbed)))}")