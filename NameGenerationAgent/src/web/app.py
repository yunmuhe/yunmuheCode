"""
Flask Web ?????
"""

import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request, session
from flask_cors import CORS

from src.utils.env_loader import get_env_source, set_env_source
from src.web.dev_server import get_dev_server_options

# ???????? Python ??
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)


def load_env_file():
    """?? .env ??"""
    env_file_path = os.path.join(project_root, ".env")
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key not in os.environ:
                            os.environ[key] = value
                            set_env_source(key, ".env")
                        elif get_env_source(key) == "missing":
                            set_env_source(key, "process_env")
            print(".env ??????")
        except Exception as e:
            print(f".env ??????: {str(e)}")


# ????????
load_env_file()


def get_config():
    """获取配置"""
    try:
        # 尝试多种导入方式
        try:
            from config.settings import config
        except ImportError:
            import os
            import sys

            # 添加项目根目录到路径
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from config.settings import config
        return config
    except ImportError as e:
        print(f"配置导入失败: {e}")

        # 返回默认配置
        class DefaultConfig:
            SECRET_KEY = "dev-secret-key-change-in-production"
            DEBUG = True

            @staticmethod
            def ensure_directories():
                os.makedirs("data", exist_ok=True)
                os.makedirs("data/cache", exist_ok=True)

        return {"default": DefaultConfig()}


def get_name_generator():
    """获取姓名生成器"""
    try:
        # 尝试多种导入方式
        try:
            from src.core.name_generator import name_generator
        except ImportError:
            import os
            import sys

            # 添加项目根目录到路径
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.core.name_generator import name_generator
        return name_generator
    except ImportError as e:
        print(f"姓名生成器导入失败: {e}")
        return None


def get_logger():
    """获取日志记录器"""
    try:
        # 尝试多种导入方式
        try:
            from src.utils.logger import get_logger
        except ImportError:
            import os
            import sys

            # 添加项目根目录到路径
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.utils.logger import get_logger
        return get_logger(__name__)
    except ImportError as e:
        print(f"日志记录器导入失败: {e}")
        import logging

        return logging.getLogger(__name__)


def get_auth_service():
    """Get auth service with delayed import."""
    try:
        try:
            from src.core.auth_service import auth_service
        except ImportError:
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.core.auth_service import auth_service
        return auth_service
    except ImportError as e:
        logger = get_logger()
        logger.error(f"auth service import failed: {str(e)}")
        return None


def get_record_service():
    """Get generation record service with delayed import."""
    try:
        try:
            from src.core.record_service import record_service
        except ImportError:
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.core.record_service import record_service
        return record_service
    except ImportError as e:
        logger = get_logger()
        logger.error(f"record service import failed: {str(e)}")
        return None


def extract_bearer_token():
    """Extract token from Authorization header or request body."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    return token.strip() if isinstance(token, str) else ""


def get_current_user_from_token(auth_service):
    token = extract_bearer_token()
    if not token:
        return None
    return auth_service.get_user_by_token(token)


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)

    # 获取配置
    config = get_config()

    # 配置
    app.config["SECRET_KEY"] = config["default"].SECRET_KEY
    app.config["DEBUG"] = config["default"].DEBUG

    # 确保数据目录存在
    config["default"].ensure_directories()

    return app


app = create_app()

# 启用跨域支持，允许在uni-app前端中通过HTTP请求调用本地部署的智能体
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins.strip() == "*":
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
else:
    origins = [
        origin.strip() for origin in allowed_origins.split(",") if origin.strip()
    ]
    if origins:
        CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)
    else:
        CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

try:
    from src.web.admin_views import admin_bp

    app.register_blueprint(admin_bp)
except Exception as e:
    logger = get_logger()
    logger.warning(f"admin blueprint disabled: {str(e)}")


@app.route("/")
def index():
    """API首页 - 返回系统信息"""
    return jsonify({
        'name': '智能姓名生成系统 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'options': '/options',
            'models': '/models',
            'generate': '/generate',
            'stats': '/stats',
            'history': '/history/list',
            'favorites': '/favorites',
            'auth_register': '/auth/register',
            'auth_login': '/auth/login',
            'auth_me': '/auth/me',
            'auth_logout': '/auth/logout',
            'auth_change_password': '/auth/change-password',
            'admin': '/admin'
        },
        'frontend': 'uni-app (智能姓名生成系统)',
        'description': '基于多平台AI的智能中文姓名生成API'
    })


@app.route("/generate", methods=["POST"])
def generate_names():
    """???? API"""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "???????"}), 500

        current_user = get_current_user_from_token(auth_service)
        if not current_user:
            return jsonify({"success": False, "error": "????"}), 401

        data = request.get_json() or {}

        description = data.get("description", "").strip()
        cultural_style = data.get("cultural_style", "chinese_modern")
        gender = data.get("gender", "neutral")
        age = data.get("age", "adult")
        preferred_api = data.get("preferred_api")
        model = data.get("model")
        use_cache = data.get("use_cache", True)
        preferred_surname = (data.get("preferred_surname") or "").strip()
        preferred_era = (data.get("preferred_era") or "").strip()

        try:
            count = int(data.get("count", 5))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "count ???????"}), 400

        try:
            surname_weight = float(data.get("surname_weight", 1.0) or 1.0)
            era_weight = float(data.get("era_weight", 1.0) or 1.0)
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "surname_weight/era_weight ???????"}), 400

        if not description:
            return jsonify({"success": False, "error": "????????"}), 400

        if count < 1 or count > 20:
            return jsonify({"success": False, "error": "??????? 1-20 ??"}), 400

        name_generator = get_name_generator()
        if name_generator:
            result = name_generator.generate_names(
                description=description,
                count=count,
                cultural_style=cultural_style,
                gender=gender,
                age=age,
                preferred_api=preferred_api,
                model=model,
                use_cache=use_cache,
                preferred_surname=preferred_surname,
                surname_weight=surname_weight,
                era_weight=era_weight,
                preferred_era=preferred_era,
            )
        else:
            mock_names = [
                {"name": "??", "meaning": "??????", "source": "mock"},
                {"name": "??", "meaning": "??????", "source": "mock"},
                {"name": "??", "meaning": "??????", "source": "mock"},
                {"name": "??", "meaning": "??????", "source": "mock"},
                {"name": "??", "meaning": "??????", "source": "mock"},
            ]
            result = {
                "success": True,
                "names": mock_names[:count],
                "api_name": "mock",
                "model": "mock-model",
            }

        if result.get("success"):
            session["last_generation"] = {
                "description": description,
                "count": count,
                "cultural_style": cultural_style,
                "gender": gender,
                "age": age,
                "generated_at": datetime.now().isoformat(),
                "names_count": len(result.get("names", [])),
            }

            record_service = get_record_service()
            if record_service:
                try:
                    record_service.create_generation_record(
                        user_id=int(current_user["id"]),
                        description=description,
                        cultural_style=cultural_style,
                        gender=gender,
                        age=age,
                        request_count=len(result.get("names", [])),
                        api_name=result.get("api_name", ""),
                        model=result.get("model", ""),
                        names=result.get("names", []),
                    )
                except Exception as save_error:
                    logger = get_logger()
                    logger.warning(f"save generation record failed: {str(save_error)}")

        return jsonify(result)

    except Exception as e:
        logger = get_logger()
        logger.error(f"??????: {str(e)}")
        return jsonify({"success": False, "error": f"??????: {str(e)}"}), 500


@app.route("/options")
def get_options():
    """获取可用选项"""
    try:
        name_generator = get_name_generator()
        if name_generator:
            options = name_generator.get_available_options()
        else:
            # 返回默认选项
            options = {
                "cultural_styles": [
                    "chinese_modern",
                    "chinese_traditional",
                    "fantasy",
                    "western",
                ],
                "genders": ["male", "female", "neutral"],
                "ages": ["child", "teen", "adult", "elder"],
                "apis": ["mock"],
            }

        return jsonify({"success": True, "options": options})
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取选项失败: {str(e)}")
        return jsonify({"success": False, "error": f"获取选项失败: {str(e)}"}), 500


@app.route("/models", methods=["GET"])
def get_models():
    """获取所有可用平台的模型列表"""
    try:
        # 获取查询参数
        api_name = request.args.get("api")  # 可选：只获取特定平台的模型
        refresh = (
            request.args.get("refresh", "false").lower() == "true"
        )  # 是否强制刷新缓存

        # 导入模型管理器和统一客户端
        from src.api.model_manager import model_manager
        from src.api.unified_client import unified_client

        # 如果需要刷新缓存
        if refresh:
            model_manager.clear_cache(api_name)

        # 获取模型列表
        if api_name:
            # 获取特定平台的模型
            adapter = unified_client.adapters.get(api_name)
            if not adapter:
                return jsonify(
                    {"success": False, "error": f"未找到API平台: {api_name}"}
                ), 404

            if not adapter.is_available():
                return jsonify(
                    {"success": False, "error": f"API平台未启用: {api_name}"}
                ), 400

            models = model_manager.get_models_for_api(api_name, adapter)
            return jsonify(
                {
                    "success": True,
                    "api": api_name,
                    "models": models,
                    "count": len(models),
                }
            )
        else:
            # 获取所有平台的模型
            all_models = model_manager.get_all_models(unified_client.adapters)

            # 统计信息
            total_count = sum(len(models) for models in all_models.values())

            return jsonify(
                {
                    "success": True,
                    "models": all_models,
                    "platforms": list(all_models.keys()),
                    "total_count": total_count,
                }
            )

    except Exception as e:
        logger = get_logger()
        logger.error(f"获取模型列表失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": f"获取模型列表失败: {str(e)}"}), 500


@app.route("/stats")
def get_stats():
    """获取系统统计信息"""
    try:
        name_generator = get_name_generator()
        if name_generator:
            stats = name_generator.get_generation_stats()
        else:
            # 返回默认统计信息
            stats = {
                "available_apis": 1,
                "api_status": {"mock": {"enabled": True}},
                "cache_stats": {"active_entries": 0},
            }

        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({"success": False, "error": f"获取统计信息失败: {str(e)}"}), 500


@app.route("/history")
def get_history():
    """??????????????"""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "???????"}), 500
        user = get_current_user_from_token(auth_service)
        if not user:
            return jsonify({"success": False, "error": "????"}), 401

        record_service = get_record_service()
        if not record_service:
            return jsonify({"success": True, "history": None})

        data = record_service.list_user_records(user_id=int(user["id"]), page=1, page_size=1, q="")
        history = data["items"][0] if data["items"] else None
        return jsonify({"success": True, "history": history})
    except Exception as e:
        logger = get_logger()
        logger.error(f"??????: {str(e)}")
        return jsonify({"success": False, "error": f"??????: {str(e)}"}), 500


@app.route("/history/list")
def get_history_list():
    """?????????????????"""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "???????"}), 500
        user = get_current_user_from_token(auth_service)
        if not user:
            return jsonify({"success": False, "error": "????"}), 401

        try:
            page = int(request.args.get("page", 1))
            page_size = int(request.args.get("page_size", 10))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "page/page_size ???????"}), 400

        q = (request.args.get("q") or "").strip()

        record_service = get_record_service()
        if not record_service:
            return jsonify({"success": True, "page": page, "page_size": page_size, "total": 0, "items": []})

        result = record_service.list_user_records(
            user_id=int(user["id"]),
            page=page,
            page_size=page_size,
            q=q,
        )

        return jsonify({
            "success": True,
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
            "items": result["items"],
        })
    except Exception as e:
        logger = get_logger()
        logger.error(f"????????: {str(e)}")
        return jsonify({"success": False, "error": f"????????: {str(e)}"}), 500


@app.route("/favorites", methods=["GET", "POST", "DELETE"])
def favorites():
    """?????GET ?????POST ???DELETE ????????????"""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "???????"}), 500

        user = get_current_user_from_token(auth_service)
        if not user:
            return jsonify({"success": False, "error": "????"}), 401

        record_service = get_record_service()
        if not record_service:
            return jsonify({"success": False, "error": "???????"}), 500

        if request.method == "GET":
            items = record_service.list_favorites(int(user["id"]))
            return jsonify({"success": True, "items": items})

        data = request.get_json() or {}

        if request.method == "POST":
            item = record_service.upsert_favorite(int(user["id"]), data)
            return jsonify({"success": True, "item": item})

        if request.method == "DELETE":
            ids = data.get("ids") or []
            if not isinstance(ids, list):
                ids = [ids]
            deleted = record_service.delete_favorites(int(user["id"]), ids)
            return jsonify({"success": True, "deleted": deleted})

        return jsonify({"success": False, "error": "??????"}), 405
    except Exception as e:
        logger = get_logger()
        logger.error(f"??????: {str(e)}")
        return jsonify({"success": False, "error": f"??????: {str(e)}"}), 500


@app.route("/auth/register", methods=["POST"])
def auth_register():
    """Register a new user with phone and password."""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "认证服务不可用"}), 500

        data = request.get_json() or {}
        phone = (data.get("phone") or "").strip()
        password = data.get("password") or ""
        success, result, status_code = auth_service.register_user(
            phone=phone, password=password
        )
        return jsonify(result), status_code
    except Exception as e:
        logger = get_logger()
        logger.error(f"register failed: {str(e)}")
        return jsonify({"success": False, "error": f"注册失败: {str(e)}"}), 500


@app.route("/auth/login", methods=["POST"])
def auth_login():
    """Login and return token."""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "认证服务不可用"}), 500

        data = request.get_json() or {}
        phone = (data.get("phone") or "").strip()
        password = data.get("password") or ""
        success, result, status_code = auth_service.login_user(
            phone=phone, password=password
        )
        return jsonify(result), status_code
    except Exception as e:
        logger = get_logger()
        logger.error(f"login failed: {str(e)}")
        return jsonify({"success": False, "error": f"登录失败: {str(e)}"}), 500


@app.route("/auth/me", methods=["GET"])
def auth_me():
    """Return current user from Bearer token."""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "认证服务不可用"}), 500

        token = extract_bearer_token()
        if not token:
            return jsonify({"success": False, "error": "未提供令牌"}), 401

        user = auth_service.get_user_by_token(token)
        if not user:
            return jsonify({"success": False, "error": "令牌无效或已过期"}), 401

        return jsonify({"success": True, "user": user})
    except Exception as e:
        logger = get_logger()
        logger.error(f"auth me failed: {str(e)}")
        return jsonify({"success": False, "error": f"鉴权失败: {str(e)}"}), 500


@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    """Revoke current Bearer token."""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "认证服务不可用"}), 500

        token = extract_bearer_token()
        if not token:
            return jsonify({"success": False, "error": "未提供令牌"}), 401

        auth_service.logout_token(token)
        return jsonify({"success": True})
    except Exception as e:
        logger = get_logger()
        logger.error(f"logout failed: {str(e)}")
        return jsonify({"success": False, "error": f"退出失败: {str(e)}"}), 500


@app.route("/auth/change-password", methods=["POST"])
def auth_change_password():
    """Change password for current logged-in user token."""
    try:
        auth_service = get_auth_service()
        if not auth_service:
            return jsonify({"success": False, "error": "???????"}), 500

        token = extract_bearer_token()
        if not token:
            return jsonify({"success": False, "error": "?????"}), 401

        data = request.get_json() or {}
        old_password = data.get("old_password") or ""
        new_password = data.get("new_password") or ""
        success, result, status_code = auth_service.change_password_by_token(
            token=token,
            old_password=old_password,
            new_password=new_password,
        )
        return jsonify(result), status_code
    except Exception as e:
        logger = get_logger()
        logger.error(f"change password failed: {str(e)}")
        return jsonify({"success": False, "error": f"??????: {str(e)}"}), 500


@app.route("/health")
def health_check():
    """健康检查"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    )


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify(
        {
            "success": False,
            "error": "Not Found",
            "message": "请求的资源不存在",
            "status": 404,
        }
    ), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger = get_logger()
    logger.error(f"内部服务器错误: {str(error)}")
    return jsonify(
        {
            "success": False,
            "error": "Internal Server Error",
            "message": "服务器内部错误",
            "status": 500,
        }
    ), 500


if __name__ == "__main__":
    logger = get_logger()
    config = get_config()
    logger.info("启动智能姓名生成系统")
    app.run(
        host="0.0.0.0",
        port=5000,
        **get_dev_server_options(debug=config["default"].DEBUG),
    )
