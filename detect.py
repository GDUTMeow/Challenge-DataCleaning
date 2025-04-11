import csv
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from tqdm import tqdm
import string

def is_name_valid(s):
    for char in s:
        if char in string.ascii_letters or char in string.digits:
            return False
    return True

def validate_id(id_num):
    if len(id_num) != 18:
        return False
    try:
        check = calculate_id_check(id_num[:17])
        return check == id_num[17]
    except:
        return False

def calculate_id_check(code_17):
    weight = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
    total = sum(int(code_17[i]) * weight[i] for i in range(17))
    return '10X98765432'[total % 11]

def validate_username(username):
    return username[0].isalpha() and all(c.isalnum() for c in username)

def validate_signature(serial, username, password, id_num, sig):
    try:
        with open(f'cert/{serial}.pem', 'rb') as f:
            pub_key = serialization.load_pem_public_key(f.read(), backend=default_backend())
        message = f"{username}_{password}_{id_num}".encode()
        pub_key.verify(
            base64.b64decode(sig),
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

issues = []
with open('polluted.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with tqdm(total=len(list(reader)), desc="检测数据", unit="行") as pbar:
        f.seek(0)
        reader.__next__()   # Skip header
        for row in reader:
            serial = row['序号']
            errors = []
            
            if not is_name_valid(row['姓名']):
                errors.append("姓名包含非中文字符")
                
            if not validate_id(row['身份证号']):
                errors.append("身份证校验失败")
                
            if not validate_username(row['用户名']):
                errors.append("用户名格式错误")
                                
            if not validate_signature(serial, row['用户名'], row['密码'], row['身份证号'], row['签名']):
                errors.append("签名验证失败")
                
            if errors:
                issues.append( (serial, errors) )
            pbar.update(1)

for serial, errors in issues:
    print(f"序号 {serial} 存在问题：{'，'.join(errors)}")
print(f"共有 {len(issues)} 条数据存在问题，分别为{'_'.join([str(i[0]) for i in issues])}")