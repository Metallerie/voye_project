# Documentation des Templates et Fichiers CSS

Ce dossier contient les templates XML et les fichiers CSS associés pour le projet `voye_project`. Voici une description détaillée de chaque fichier et de leur utilisation.

## Fichiers XML

### `index_document_view_form.xml`
Ce fichier définit la vue formulaire pour le modèle `voye_db.index.document`. Il inclut les sections `header` et `message-box` via des templates réutilisables.

```xml
<?xml version="1.0" encoding="utf-8"?>
<voye>
    <data>
        <!-- Définition de la vue formulaire pour le modèle 'voye_db.index.document' -->
        <record id="view_document_form" model="ir.ui.view">
            <field name="name">document.view.form</field>
            <field name="model">voye_db.index.document</field>
            <field name="arch" type="xml">
                <form string="Document">
                    <!-- Inclusion des fichiers CSS -->
                    <template>
                        <link rel="stylesheet" type="text/css" href="/static/css/index_document_view_form.css"/>
                    </template>

                    <!-- Inclusion du header -->
                    <t t-call="header_template"/>

                    <!-- Disposition horizontale principale -->
                    <group>
                        <group string="JSON Viewer" colspan="1">
                            <field name="json_data" widget="text" readonly="1"/>
                        </group>
                        <group string="PDF Viewer" colspan="2">
                            <field name="pdf_path" widget="url"/>
                        </group>
                        <group string="Validation" colspan="1">
                            <button string="Document Précédent" type="action" name="previous_document"/>
                            <button string="Document Suivant" type="action" name="next_document"/>
                        </group>
                    </group>

                    <!-- Inclusion de la message-box -->
                    <t t-call="message_box_template"/>
                </form>
            </field>
        </record>
    </data>
</voye>
```

### `header_template.xml`
Ce fichier contient le template pour le `header` de la vue, incluant les boutons de navigation.

```xml
<?xml version="1.0" encoding="utf-8"?>
<voye>
    <data>
        <template id="header_template">
            <t t-name="header_template">
                <!-- Inclusion des fichiers CSS pour le header -->
                <link rel="stylesheet" type="text/css" href="/static/css/header_template.css"/>
                <header class="navbar">
                    <ul>
                        <li><a href="#">🏠 Menu 1</a></li>
                        <li><a href="#">📂 Menu 2</a></li>
                    </ul>
                </header>
            </t>
        </template>
    </data>
</voye>
```

### `message_box_template.xml`
Ce fichier contient le template pour la `message-box`, utilisée pour afficher les messages de traitement.

```xml
<?xml version="1.0" encoding="utf-8"?>
<voye>
    <data>
        <template id="message_box_template">
            <t t-name="message_box_template">
                <!-- Inclusion des fichiers CSS pour la message-box -->
                <link rel="stylesheet" type="text/css" href="/static/css/message_box_template.css"/>
                <div class="message-box">
                    <field name="message" readonly="1"/>
                </div>
            </t>
        </template>
    </data>
</voye>
```

## Fichiers CSS

### `index_document_view_form.css`
Ce fichier contient les styles pour la mise en page principale du formulaire. Il exclut les styles du `header` et de la `message-box`.

```css
/* Styles généraux pour le document */
body, html {
    height: 100%;
    margin: 0;
    font-family: Arial, sans-serif;
}

/* Mise en page horizontale principale */
.horizontal-layout {
    display: flex;
    flex-direction: row;
    height: 65%;
    width: 100%;
}

.horizontal-layout .json-viewer,
.horizontal-layout .pdf-viewer,
.horizontal-layout .validation {
    flex: 1;
    height: 100%;
    margin: 0 10px;
}

.horizontal-layout .json-viewer {
    background-color: #f1f1f1;
}

.horizontal-layout .pdf-viewer {
    background-color: #e2e2e2;
}

.horizontal-layout .validation {
    background-color: #d3d3d3;
}
```

### `header_template.css`
Ce fichier contient les styles pour la barre de navigation (`header`).

```css
/* Styles pour la barre de navigation */
.navbar {
    height: 10%;
    width: 100%;
    background-color: #333;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

.navbar ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
}

.navbar li {
    margin: 0 20px;
}

.navbar a {
    color: white;
    text-decoration: none;
}
```

### `message_box_template.css`
Ce fichier contient les styles pour la `message-box`.

```css
/* Zone d'affichage des messages */
.message-box {
    height: 25%;
    width: 100%;
    background-color: #ccc;
    display: flex;
    justify-content: center;
    align-items: center;
}

.message-box p {
    margin: 0;
}
```

## Inclus dans les fichiers XML

Les fichiers CSS sont inclus dans les templates XML correspondants en utilisant la balise `<link>`. Cela permet de séparer les styles pour une meilleure modularité et réutilisabilité.

### Exemple d'inclusion dans `index_document_view_form.xml`
```xml
<template>
    <link rel="stylesheet" type="text/css" href="/static/css/index_document_view_form.css"/>
</template>
```

### Exemple d'inclusion dans `header_template.xml`
```xml
<link rel="stylesheet" type="text/css" href="/static/css/header_template.css"/>
```

### Exemple d'inclusion dans `message_box_template.xml`
```xml
<link rel="stylesheet" type="text/css" href="/static/css/message_box_template.css"/>
```

En suivant cette structure, vous pouvez facilement réutiliser et maintenir les différentes sections de vos formulaires.
