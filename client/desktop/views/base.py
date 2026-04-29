import datetime
import tkinter as tk


############
# UTILITATS PER A LES VISTES
############

def today_iso():
    return datetime.date.today().isoformat()


def parse_iso_date(value, error_message):
    try:
        return datetime.datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except ValueError:
        raise ValueError(error_message)


def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)


def clear_text_widget(text_widget):
    text_widget.configure(state='normal')
    text_widget.delete('1.0', tk.END)


def build_options_map(rows, id_keys, label_keys):
    mapping = {}
    for row in rows:
        option_id = None
        option_label = None

        if isinstance(row, dict):
            for key in id_keys:
                value = row.get(key)
                if value not in (None, ''):
                    option_id = value
                    break
            for key in label_keys:
                value = row.get(key)
                if value not in (None, ''):
                    option_label = value
                    break
        elif isinstance(row, (list, tuple)) and len(row) >= 2:
            option_id, option_label = row[0], row[1]

        if option_id is None or not option_label:
            continue

        mapping[str(option_id)] = str(option_label)

    return mapping


def build_combo_values(mapping):
    values = []
    for option_id, label in mapping.items():
        values.append(f'{option_id} - {label}')
    return values


def split_combo_value(value):
    return str(value).split(' - ', 1)[0].strip()
