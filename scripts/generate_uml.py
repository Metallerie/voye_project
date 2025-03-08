import ast
import os
import datetime

def extract_classes_methods_and_attributes(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            attributes = [n.targets[0].attr for n in node.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Attribute)]
            classes[class_name] = {'methods': methods, 'attributes': attributes}
    
    return classes

def generate_plantuml(classes):
    uml = "@startuml\n"
    for cls, data in classes.items():
        uml += f"class {cls} {{\n"
        for attr in data['attributes']:
            uml += f"    - {attr}\n"
        for method in data['methods']:
            uml += f"    + {method}()\n"
        uml += "}\n"
    uml += "@enduml"
    return uml

def main():
    source_dir = "/data/voye/"  # Ajuste ce chemin selon ton projet
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/data/voye/docs/project_structure_{timestamp}.puml"
    
    all_classes = {}
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                classes = extract_classes_methods_and_attributes(file_path)
                all_classes.update(classes)
    
    uml_content = generate_plantuml(all_classes)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(uml_content)
    
    print(f"✅ UML généré : {output_file}")

if __name__ == "__main__":
    main()
