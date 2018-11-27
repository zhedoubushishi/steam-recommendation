import os
import re

path = "raw_data"
files = os.listdir(path)
output_filepath = "../processed_data/data.txt"

output_file = open(output_filepath, 'w+', encoding='utf-8')


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


user_id_set = {}
cur_id = 1
for file in files:
    if not os.path.isdir(file):
        f = open(path + "/" + file, encoding='utf-8')
        iter_f = iter(f)
        for line in iter_f:
            if line == '':
                continue
            items = line.split('\t')
            if len(items) < 5:
                continue

            user_id = items[0]
            if user_id in user_id_set:
                user_id = user_id_set.get(user_id)
            else:
                user_id_set[user_id] = cur_id
                user_id = cur_id
                cur_id += 1

            attitude = '1'
            if items[1] == 'Not Recommended':
                attitude = '0'

            review = items[4].strip()
            review = re.sub("[^a-zA-Z0-9\.\?\$\%\:\*\s]", '', review)
            review.replace('\t', '\s')
            review = ' '.join(review.split())
            if len(review) < 4 or is_number(review):
                continue
            output_file.write(
                str(user_id) + '\t' + attitude + '\t' + review + '\n')
        f.close()

output_file.close()
