import csv
import random
import string
from datetime import datetime, timedelta
import os
import base64
from tqdm import tqdm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# 创建证书目录
os.makedirs('cert', exist_ok=True)

# 常见中文姓氏列表 (Common Chinese Surnames)
surnames = [
    '王', '李', '张', '刘', '陈', '杨', '黄', '赵', '吴', '周', 
    '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '罗', 
    '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹', 
    '彭', '曾', '肖', '田', '董', '袁', '潘', '于', '蒋', '蔡', 
    '余', '魏', '程', '叶', '苏', '吕', '丁', '任', '沈', '姚', 
    '卢', '姜', '崔', '钟', '谭', '陆', '汪', '范', '金', '石', 
    '廖', '贾', '夏', '韦', '付', '方', '白', '邹', '孟', '熊', 
    '秦', '邱', '江', '尹', '薛', '闫', '段', '雷', '侯', '龙', 
    '史', '陶', '黎', '贺', '顾', '毛', '郝', '龚', '邵', '万', 
    '钱', '严', '覃', '武', '戴', '莫', '孔', '向', '汤', '常',
    '温', '康', '施', '文', '牛', '樊', '葛', '邢', '安', '齐',
    '易', '乔', '伍', '庞', '颜', '倪', '庄', '聂', '章', '鲁',
    '岳', '翟', '殷', '詹', '喻', '杜', '童', '涂', '蒲', '司',
    '车', '屈', '鲍', '房', '柯', '阮', '解', '时', '梅', '管',
    '牟', '霍', '甘', '左', '祝', '闵', '欧', '项', '洪'
]

# 常见中文男性名字列表 (Common Chinese Male Names)
# 包含单字名和双字名，涵盖不同年代的常用名。
male_names = [
    # 单字名
    '伟', '强', '磊', '军', '勇', '杰', '涛', '超', '刚', '浩', 
    '明', '亮', '俊', '峰', '鹏', '斌', '波', '凯', '健', '辉', 
    '平', '宇', '翔', '博', '航', '志', '霖', '鑫', '哲', '涵', 
    '泽', '瑞', '轩', '睿', '洋', '龙', '晨', '辰', '毅', '阳', 
    '飞', '康', '宁', '安', '文', '武', '旭', '升', '胜', '帅', 
    '智', '达', '彪', '栋', '楠', '锋', '锐', '铭', '森', '林', 
    '海', '江', '河', '山', '石', '金', '银', '松', '柏', '帆',
    # 双字名
    '子轩', '浩宇', '宇轩', '俊杰', '伟强', '志强', '国强', '建国', 
    '建华', '文涛', '嘉豪', '浩然', '宇航', '鹏飞', '德华', '明辉', 
    '睿智', '宏伟', '泽宇', '晨阳', '鑫磊', '嘉俊', '世杰', '天宇', 
    '文博', '国栋', '家辉', '俊峰', '凯旋', '志远', '振华', '永强', 
    '晓明', '晓峰', '建军', '卫国', '立军', '书豪', '明轩', '瑞霖', 
    '博文', '思远', '承志', '德明', '光辉', '鸿飞', '建平', '康健', 
    '乐山', '茂林', '宁静', '启明', '荣轩', '绍辉', '泰和', '伟泽', 
    '向阳', '旭东', '彦博', '英杰', '展鹏', '智宸', '子涵', '嘉伦', 
    '明哲', '思成', '文昊', '星河', '永昌', '元嘉', '正阳', '志新', 
    '博涛', '昌盛', '飞宇', '高远', '和平', '嘉祥', '昆鹏', '良平', 
    '敏学', '彭祖', '庆云', '锐利', '升荣', '同和', '温茂', '信鸿'
]

# 常见中文女性名字列表 (Common Chinese Female Names)
# 包含单字名和双字名，涵盖不同年代的常用名。
female_names = [
    # 单字名
    '芳', '娜', '敏', '静', '丽', '娟', '艳', '玲', '婷', '慧', 
    '萍', '红', '丹', '雪', '颖', '菲', '薇', '莉', '霞', '琳', 
    '兰', '菊', '梅', '秀', '芬', '雅', '琼', '涵', '璇', '瑶', 
    '怡', '欣', '妍', '媛', '蕊', '琪', '爽', '妮', '娇', '芸', 
    '茜', '莎', '梦', '倩', '姣', '婉', '娴', '瑾', '颖', '露', 
    '瑶', '怡', '婵', '雁', '蓓', '纨', '仪', '荷', '丹', '蓉', 
    '眉', '君', '琴', '蕊', '薇', '菁', '梦', '岚', '苑', '婕', 
    '馨', '瑗', '琰', '韵', '融', '园', '艺', '咏', '卿', '聪',
    # 双字名
    '欣怡', '梓涵', '诗涵', '语嫣', '嘉欣', '雅静', '婉婷', '慧玲', 
    '美玲', '秀英', '淑芬', '瑞雪', '晓梅', '晓燕', '雨涵', '梦洁', 
    '佳怡', '欣妍', '紫萱', '依诺', '若曦', '思涵', '语桐', '瑾萱', 
    '诗琪', '曼妮', '雪琴', '雅琳', '慧敏', '丽华', '月婵', '春梅', 
    '秋菊', '冬雪', '夏兰', '海燕', '小红', '小丽', '玉兰', '美华', 
    '佳慧', '思佳', '雨欣', '晓彤', '梦瑶', '可馨', '静蕾', '安琪', 
    '雅雯', '诗语', '晨曦', '若瑄', '书瑶', '乐怡', '心妍', '子璇', 
    '芷若', '曼殊', '惠兰', '婉如', '静香', '舒雅', '瑞芬', '美娟', 
    '丹妮', '海伦', '嘉慧', '兰馨', '曼丽', '念慈', '佩兰', '巧云', 
    '如意', '珊珊', '舒畅', '婷美', '婉仪', '晓月', '雅洁', '依娜', 
    '映雪', '雨薇', '芸萱', '芷涵', '紫薇', '安娜', '贝儿', '彩云'
]

def generate_name(gender):
    surname = random.choice(surnames)
    if gender == '男':
        given_name = ''.join(random.choices(male_names, k=random.randint(1, 2)))
    else:
        given_name = ''.join(random.choices(female_names, k=random.randint(1, 2)))
    return surname + given_name

def calculate_id_check(code_17):
    weight = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
    total = sum(int(code_17[i]) * weight[i] for i in range(17))
    return '10X98765432'[total % 11]

def generate_id_number(gender):
    area_code = '440111'
    birth_date = datetime.now() - timedelta(days=random.randint(365*18, 365*60))
    birth_code = birth_date.strftime('%Y%m%d')
    seq_part = f'{random.randint(0, 999):03d}'
    last_digit = random.choice([1,3,5,7,9] if gender == '男' else [0,2,4,6,8])
    former_17 = f"{area_code}{birth_code}{seq_part[:2]}{last_digit}"
    check_code = calculate_id_check(former_17)
    return former_17 + check_code

def generate_username():
    return random.choice(string.ascii_letters) + ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 11)))

def generate_password():
    chars = string.ascii_letters + "".join([str(i) for i in range(10)]) + string.punctuation
    chars.replace(',', '').replace("'", '').replace('"', '')
    return ''.join(random.choices(chars, k=random.randint(8, 16)))

def generate_signature(username, password, id_num, serial):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    with open(f'cert/{serial}.pem', 'wb') as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    message = f"{username}_{password}_{id_num}".encode()
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

data = []
for i in tqdm(range(1, 2001)):
    gender = random.choice(['男', '女'])
    name = generate_name(gender).strip()
    id_num = generate_id_number(gender).strip()
    username = generate_username().strip()
    password = generate_password().strip()
    signature = generate_signature(username, password, id_num, i).strip()
    data.append([i, name, gender, id_num, username, password, signature])

with open('original.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['序号', '姓名', '性别', '身份证号', '用户名', '密码', '签名'])
    writer.writerows(data)