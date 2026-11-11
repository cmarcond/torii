import os
from devias.app import app


if __name__ == "__main__":    
    app.run(debug=os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true'))