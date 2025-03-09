import os
import ast
import argparse

def log(message):
    print(f"[DEBUG] {message}")

class ClassVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        log(f"Analyzing class: {node.name}")
        class_info = {
            'name': node.name,
            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'methods': [],
            'attributes': []
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'visibility': 'public' if not item.name.startswith('_') else 'private',
                    'return_type': 'Unknown'  # Peut être amélioré avec les annotations
                }
                log(f"Found method: {method_info}")
                class_info['methods'].append(method_info)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    attr_info = {
                        'name': item.target.id,
                        'type': item.annotation.id if isinstance(item.annotation, ast.Name) else 'Unknown',
                        'visibility': 'public' if not item.target.id.startswith('_') else 'private'
                    }
                    log(f"Found attribute: {attr_info}")
                    class_info['attributes'].append(attr_info)
        
        self.classes.append(class_info)
        self.generic_visit(node)

def parse_python_file(filename):
    log(f"Parsing file: {filename}")
    with open(filename, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
    visitor = ClassVisitor()
    visitor.visit(tree)
    return visitor.classes

def analyze_project(directory):
    log(f"Analyzing project directory: {directory}")
    project_classes = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                log(f"Processing file: {filepath}")
                project_classes.extend(parse_python_file(filepath))
    return project_classes

def generate_uml(classes, output_file):
    log(f"Generating UML diagram in: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('@startuml\n')
        for cls in classes:
            file.write(f'class {cls["name"]} {{\n')
            for attr in cls['attributes']:
                visibility = '+' if attr['visibility'] == 'public' else '-'
                file.write(f'    {visibility} {attr["name"]}: {attr["type"]}\n')
            for method in cls['methods']:
                visibility = '+' if method['visibility'] == 'public' else '-'
                file.write(f'    {visibility} {method["name"]}()\n')
            file.write('}\n')
            for base in cls['bases']:
                file.write(f'{cls["name"]} --|> {base}\n')
        file.write('@enduml\n')

def main():
    parser = argparse.ArgumentParser(description='Génère des diagrammes UML à partir du code source Python.')
    parser.add_argument('directory', help='Répertoire du projet à analyser')
    parser.add_argument('-o', '--output', default='diagramme.uml', help='Fichier de sortie pour le diagramme UML')
    args = parser.parse_args()
    
    log("Démarrage de l'analyse...")
    project_classes = analyze_project(args.directory)
    log("Analyse terminée, génération du fichier UML...")
    generate_uml(project_classes, args.output)
    log("Fichier UML généré avec succès !")

if __name__ == '__main__':
    main()
