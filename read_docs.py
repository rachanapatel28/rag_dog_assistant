import os

data_folder = 'data'
documents = {}

for filename in os.listdir(data_folder):
    if filename.endswith('.txt'):
        file_path = os.path.join(data_folder, filename)
        with open(file_path, 'r') as file:
            documents[filename] = file.read()
            
print(f"Loaded {len(documents)} documents : ")
for name in documents:
    print(f" - {name}")
    
print("\n--- Contents ---\n")
for name , content in documents.items():
    print(f'### {name} ###')
    print(content)
    print()
    
    

        

