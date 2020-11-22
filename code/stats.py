from pathlib import Path

lines_of_code = 0
lines_of_comment = 0
blank_lines = 0

for filename in Path('.').rglob('*.py'):
    with open(filename) as infp:
        for line in infp:
            stripped_line = line.strip()
            if stripped_line and stripped_line[0] != '#':
                lines_of_code += 1
            elif stripped_line:
                lines_of_comment += 1
            else:
                blank_lines += 1

print("Code lines: {}".format(lines_of_code))
print("Blank lines: {}".format(blank_lines))
print("Comment lines: {}".format(lines_of_comment))
print("Total lines: {}".format(lines_of_code + blank_lines + lines_of_comment))
