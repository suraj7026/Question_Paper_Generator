def excel_column_names_recursive(column_number):
    if column_number <= 0:
        return ""

    letter_code = (column_number - 1) % 26

    letter = chr(ord('A') + letter_code)

    return excel_column_names_recursive((column_number - 1) // 26) + letter

max_column_number = 99999
for i in range(1, max_column_number + 1):
    print(excel_column_names_recursive(i))
