from flask import Flask, send_from_directory
import os
from flask_swagger_ui import get_swaggerui_blueprint

def setup_swagger(app: Flask):
    """
    Thiết lập Swagger UI cho Flask app
    """
    # Đường dẫn URL cho Swagger UI
    SWAGGER_URL = '/api/docs'
    
    # Đường dẫn tới file spec API
    API_URL = '/api/docs/swagger.yaml'
    
    # Tạo blueprint cho Swagger UI
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "RAG Learning Path API"
        }
    )
    
    # Đăng ký blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Route để phục vụ file YAML
    @app.route('/api/docs/swagger.yaml')
    def send_api_spec():
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return send_from_directory(dir_path, 'API_DOCS.yaml')
    
    print(f"Swagger UI available at {SWAGGER_URL}")

if __name__ == "__main__":
    # Test swagger setup
    app = Flask(__name__)
    setup_swagger(app)
    print("Swagger UI setup completed. Access at http://localhost:5000/api/docs")
    app.run(debug=True) 