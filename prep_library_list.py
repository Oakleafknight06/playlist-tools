
file = input("enter filename: ")
new_file = []
print("reading...")
with open(file, "r") as fh:
    filelines = fh.readlines()
    for line in filelines:
        filename = line.split("/")[-1]
        if filename.find(".") != -1:
            new_file.append(line[1:])

print("writing...")
with open(f"new_{file}", "w") as fh:
    for line in new_file:
        fh.write(line)

print("done!")
print(f"saved to new_{file}")
