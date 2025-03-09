import os
import ast
import argparse

def log(message):
    print(f"[DEBUG] {message}")

class ClassVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.relations = []
        self.current_class = None
        self.imports = {}

    def visit_ImportFrom(self, node):
        if node.module:
            module_name = node.module
            for alias in node.names:
                self.imports[alias.name] = module_name
                log(f"Detected import: {alias.name} from {module_name}")

    def visit_ClassDef(self, node):
        log(f"Analyzing class: {node.name}")
        class_info = {
            'name': node.name,
            'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
            'methods': [],
            'attributes': []
        }
        
        for base in class_info['bases']:
            self.relations.append(f"{node.name} --|> {base}")
        
        self.current_class = class_info
        self.generic_visit(node)
        self.classes.append(class_info)
        self.current_class = None

    def visit_FunctionDef(self, node):
        if self.current_class is not None:
            return_type = 'Unknown'
            if node.returns:
                return_type = self.get_type_annotation(node.returns)
            else:
                return_type = self.infer_return_type(node)
            
            method_info = {
                'name': node.name,
                'visibility': 'public' if not node.name.startswith('_') else 'private',
                'return_type': return_type
            }
            log(f"Found method: {method_info}")
            self.current_class['methods'].append(method_info)
        self.generic_visit(node)
    
    def visit_Assign(self, node):
        if self.current_class is not None:
            for target in node.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                    attr_type = 'Unknown'
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                        attr_type = node.value.func.id
                        self.relations.append(f"{self.current_class['name']} *-- {attr_type}")
                    attr_info = {
                        'name': target.attr,
                        'type': attr_type,
                        'visibility': 'public' if not target.attr.startswith('_') else 'private'
                    }
                    log(f"Found attribute: {attr_info}")
                    self.current_class['attributes'].append(attr_info)
        self.generic_visit(node)

    def get_type_annotation(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            value = self.get_type_annotation(node.value)
            slice_value = self.get_type_annotation(node.slice) if isinstance(node.slice, ast.Name) else '...'
            return f"{value}[{slice_value}]"
        return 'Unknown'

    def infer_return_type(self, node):
        for stmt in node.body:
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                    return stmt.value.func.id
        return 'Unknown'

def parse_python_file(filename):
    log(f"Parsing file: {filename}")
    with open(filename, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())
    visitor = ClassVisitor()
    visitor.visit(tree)
    return visitor.classes, visitor.relations

def analyze_project(directory):
    log(f"Analyzing project directory: {directory}")
    project_classes = []
    project_relations = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                log(f"Processing file: {filepath}")
                classes, relations = parse_python_file(filepath)
                project_classes.extend(classes)
                project_relations.extend(relations)
    return project_classes, project_relations

def generate_uml(classes, relations, output_file):
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
                file.write(f'    {visibility} {method["name"]}(): {method["return_type"]}\n')
            file.write('}\n')
        for relation in relations:
            file.write(f'{relation}\n')
        file.write('@enduml\n')

def main():
    parser = argparse.ArgumentParser(description='Génère des diagrammes UML à partir du code source Python.')
    parser.add_argument('directory', help='Répertoire du projet à analyser')
    parser.add_argument('-o', '--output', default='diagramme.uml', help='Fichier de sortie pour le diagramme UML')
    args = parser.parse_args()
    
    log("Démarrage de l'analyse...")
    project_classes, project_relations = analyze_project(args.directory)
    log("Analyse terminée, génération du fichier UML...")
    generate_uml(project_classes, project_relations, args.output)
    log("Fichier UML généré avec succès !")

if __name__ == '__main__':
    main()
