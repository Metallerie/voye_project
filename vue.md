┌───────────────────────────────────────────────────────┐
│ 🏠 Navigation Bar: [ Menu 1 ]   [ Menu 2 ]           │
├───────────────────────────────────────────────────────┤
│ 📂 JSON Viewer   |  📄 PDF Viewer   | ✅ Validation │
│ (éditable)       |  (zoomable)       | [ Bouton 1 ] │
│                 |                   | [ Bouton 2 ] │
├───────────────────────────────────────────────────────┤
│ 🔔 Message de traitement (statut, erreurs)          │
└───────────────────────────────────────────────────────┘

# 📌 Mise en place du Frontend pour le projet Voye

Le frontend de Voye est une application **React avec Vite et Bootstrap**, qui est servie par **Django** en backend.

---

## **✅ 1️⃣ Installation et configuration de React avec Vite**
### **1.1 Créer le projet React**
Si le projet React n'est pas encore installé, exécute cette commande dans le dossier **frontend** :
```bash
cd /data/voye/frontend
npm create vite@latest voye-ui --template react
cd voye-ui
```

### **1.2 Installer Bootstrap**
Ajoute Bootstrap à ton projet :
```bash
npm install bootstrap
```
Dans **`src/main.jsx`** (ou **`src/index.jsx`** selon la structure) ajoute :
```javascript
import "bootstrap/dist/css/bootstrap.min.css";
```
Si besoin des composants interactifs (modals, dropdowns) :
```javascript
import "bootstrap/dist/js/bootstrap.bundle.min";
```

### **1.3 Tester l’interface React**
Ajoute un composant simple dans **`src/App.jsx`** :
```jsx
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <div className="container mt-5">
      <h1 className="text-primary">Bienvenue sur Voye UI 🎉</h1>
      <button className="btn btn-success">Cliquez ici</button>
    </div>
  );
}

export default App;
```
Puis démarre l'application :
```bash
npm run dev
```
L'interface sera accessible à **`http://localhost:5173/`**.

---

## **✅ 2️⃣ Construire et déployer le frontend avec Django**

### **2.1 Générer un build optimisé de React**
Dans le dossier **frontend** :
```bash
cd /data/voye/frontend/voye-ui
npm run build
```
Cela va générer un dossier **`dist/`** contenant les fichiers HTML/CSS/JS prêts à être servis par Django.

### **2.2 Déplacer le build dans Django**
On déplace les fichiers dans Django :
```bash
mv dist /data/voye/backend/voye_backend/static
```

### **2.3 Configurer Django pour servir les fichiers React**
Dans **`settings.py`**, ajoute :
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
```

### **2.4 Modifier `urls.py` pour afficher React**
Dans **`voye_backend/urls.py`**, ajoute :
```python
from django.views.generic import TemplateView

urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
```

### **2.5 Redémarrer Django et tester**
```bash
python manage.py runserver 0.0.0.0:1999
```

📌 **L’interface React Bootstrap est maintenant accessible sur `http://89.47.51.175:1999/`** 🎨.

---

## **✅ 3️⃣ Déploiement final**
Si besoin d'un **serveur de production** (ex: Gunicorn + Nginx) :
```bash
pip install gunicorn
```
Puis lancer le serveur Django avec :
```bash
gunicorn --bind 0.0.0.0:1999 voye_backend.wsgi
```

---

## **🚀 Résumé**
✅ **Création et configuration de React avec Vite et Bootstrap**
✅ **Génération du build et intégration avec Django**
✅ **Déploiement du frontend via Django**
✅ **Accès à l’interface sur `http://89.47.51.175:1999/`**

💡 **Prochaine étape : Ajouter des interactions API entre le frontend et Django REST Framework.** 🚀


