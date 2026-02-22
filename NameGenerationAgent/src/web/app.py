"""
Flask Web应用主文件
"""
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 加载.env文件
def load_env_file():
    """加载.env文件"""
    env_file_path = os.path.join(project_root, '.env')
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        os.environ[key] = value
            print("✅ .env文件加载成功")
        except Exception as e:
            print(f"❌ .env文件加载失败: {str(e)}")

# 立即加载环境变量
load_env_file()

# 延迟导入，避免循环导入问题
def get_config():
    """获取配置"""
    try:
        # 尝试多种导入方式
        try:
            from config.settings import config
        except ImportError:
            import sys
            import os
            # 添加项目根目录到路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from config.settings import config
        return config
    except ImportError as e:
        print(f"配置导入失败: {e}")
        # 返回默认配置
        class DefaultConfig:
            SECRET_KEY = 'dev-secret-key-change-in-production'
            DEBUG = True
            
            @staticmethod
            def ensure_directories():
                os.makedirs('data', exist_ok=True)
                os.makedirs('data/cache', exist_ok=True)
        
        return {'default': DefaultConfig()}

def get_name_generator():
    """获取姓名生成器"""
    try:
        # 尝试多种导入方式
        try:
            from src.core.name_generator import name_generator
        except ImportError:
            import sys
            import os
            # 添加项目根目录到路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
            import sys
            import os
            # 添加项目根目录到路径
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.utils.logger import get_logger
        return get_logger(__name__)
    except ImportError as e:
        print(f"日志记录器导入失败: {e}")
        import logging
        return logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 获取配置
    config = get_config()
    
    # 配置
    app.config['SECRET_KEY'] = config['default'].SECRET_KEY
    app.config['DEBUG'] = config['default'].DEBUG
    
    # 确保数据目录存在
    config['default'].ensure_directories()
    
    return app

app = create_app()

# 启用跨域支持，允许在uni-app前端中通过HTTP请求调用本地部署的智能体
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*')
if allowed_origins.strip() == '*':
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
else:
    origins = [origin.strip() for origin in allowed_origins.split(',') if origin.strip()]
    if origins:
        CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)
    else:
        CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
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
            'favorites': '/favorites'
        },
        'frontend': 'uni-app (智能姓名生成系统)',
        'description': '基于多平台AI的智能中文姓名生成API'
    })

@app.route('/generate', methods=['POST'])
def generate_names():
    """生成姓名API"""
    try:
        data = request.get_json()
        
        # 获取参数
        description = data.get('description', '').strip()
        count = int(data.get('count', 5))
        cultural_style = data.get('cultural_style', 'chinese_modern')
        gender = data.get('gender', 'neutral')
        age = data.get('age', 'adult')
        preferred_api = data.get('preferred_api')
        use_cache = data.get('use_cache', True)
        preferred_surname = (data.get('preferred_surname') or '').strip()
        surname_weight = float(data.get('surname_weight', 1.0) or 1.0)
        era_weight = float(data.get('era_weight', 1.0) or 1.0)
        preferred_era = (data.get('preferred_era') or '').strip()
        
        # 验证参数
        if not description:
            return jsonify({
                'success': False,
                'error': '角色描述不能为空'
            }), 400
        
        if count < 1 or count > 20:
            return jsonify({
                'success': False,
                'error': '姓名数量必须在1-20之间'
            }), 400
        
        # 生成姓名
        name_generator = get_name_generator()
        if name_generator:
            result = name_generator.generate_names(
                description=description,
                count=count,
                cultural_style=cultural_style,
                gender=gender,
                age=age,
                preferred_api=preferred_api,
                use_cache=use_cache,
                preferred_surname=preferred_surname,
                surname_weight=surname_weight,
                era_weight=era_weight,
                preferred_era=preferred_era
            )
        else:
            # 使用模拟数据
            mock_names = [
                {'name': '张三', 'meaning': '寓意勇敢坚强', 'source': 'mock'},
                {'name': '李四', 'meaning': '寓意智慧聪慧', 'source': 'mock'},
                {'name': '王五', 'meaning': '寓意正直善良', 'source': 'mock'},
                {'name': '赵六', 'meaning': '寓意才华横溢', 'source': 'mock'},
                {'name': '陈七', 'meaning': '寓意品德高尚', 'source': 'mock'}
            ]
            result = {
                'success': True,
                'names': mock_names[:count],
                'api_name': 'mock',
                'model': 'mock-model'
            }
        
        # 记录生成历史
        if result.get('success'):
            session['last_generation'] = {
                'description': description,
                'count': count,
                'cultural_style': cultural_style,
                'gender': gender,
                'age': age,
                'generated_at': datetime.now().isoformat(),
                'names_count': len(result.get('names', []))
            }
            # 追加到历史列表（存于会话，仅用于本地演示）
            history = session.get('history', [])
            history_entry = {
                'id': f"h_{int(datetime.now().timestamp()*1000)}",
                'description': description,
                'count': len(result.get('names', [])),
                'time': datetime.now().isoformat(),
                'names': [n.get('name', '') for n in result.get('names', [])],
            }
            history.insert(0, history_entry)
            # 限制最大条目数，避免会话过大
            session['history'] = history[:200]
        
        return jsonify(result)
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"生成姓名失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'生成姓名失败: {str(e)}'
        }), 500

@app.route('/options')
def get_options():
    """获取可用选项"""
    try:
        name_generator = get_name_generator()
        if name_generator:
            options = name_generator.get_available_options()
        else:
            # 返回默认选项
            options = {
                'cultural_styles': ['chinese_modern', 'chinese_traditional', 'fantasy', 'western'],
                'genders': ['male', 'female', 'neutral'],
                'ages': ['child', 'teen', 'adult', 'elder'],
                'apis': ['mock']
            }

        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取选项失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取选项失败: {str(e)}'
        }), 500

@app.route('/models', methods=['GET'])
def get_models():
    """获取所有可用平台的模型列表"""
    try:
        # 获取查询参数
        api_name = request.args.get('api')  # 可选：只获取特定平台的模型
        refresh = request.args.get('refresh', 'false').lower() == 'true'  # 是否强制刷新缓存

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
                return jsonify({
                    'success': False,
                    'error': f'未找到API平台: {api_name}'
                }), 404

            if not adapter.is_available():
                return jsonify({
                    'success': False,
                    'error': f'API平台未启用: {api_name}'
                }), 400

            models = model_manager.get_models_for_api(api_name, adapter)
            return jsonify({
                'success': True,
                'api': api_name,
                'models': models,
                'count': len(models)
            })
        else:
            # 获取所有平台的模型
            all_models = model_manager.get_all_models(unified_client.adapters)

            # 统计信息
            total_count = sum(len(models) for models in all_models.values())

            return jsonify({
                'success': True,
                'models': all_models,
                'platforms': list(all_models.keys()),
                'total_count': total_count
            })

    except Exception as e:
        logger = get_logger()
        logger.error(f"获取模型列表失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'获取模型列表失败: {str(e)}'
        }), 500

@app.route('/stats')
def get_stats():
    """获取系统统计信息"""
    try:
        name_generator = get_name_generator()
        if name_generator:
            stats = name_generator.get_generation_stats()
        else:
            # 返回默认统计信息
            stats = {
                'available_apis': 1,
                'api_status': {'mock': {'enabled': True}},
                'cache_stats': {'active_entries': 0}
            }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取统计信息失败: {str(e)}'
        }), 500

@app.route('/history')
def get_history():
    """获取生成历史"""
    try:
        history = session.get('last_generation')
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取历史失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取历史失败: {str(e)}'
        }), 500

@app.route('/history/list')
def get_history_list():
    """分页获取生成历史列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        q = (request.args.get('q') or '').strip()

        history = session.get('history', [])

        if q:
            history = [h for h in history if q in h.get('description', '')]

        total = len(history)
        start = max(0, (page - 1) * page_size)
        end = start + page_size
        items = history[start:end]

        return jsonify({
            'success': True,
            'page': page,
            'page_size': page_size,
            'total': total,
            'items': items
        })
    except Exception as e:
        logger = get_logger()
        logger.error(f"获取历史列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取历史列表失败: {str(e)}'
        }), 500

@app.route('/favorites', methods=['GET', 'POST', 'DELETE'])
def favorites():
    """收藏接口：GET获取列表，POST添加，DELETE批量删除"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'items': session.get('favorites', [])
            })

        data = request.get_json() or {}

        if request.method == 'POST':
            item = {
                'id': data.get('id') or f"f_{int(datetime.now().timestamp()*1000)}",
                'name': data.get('name', ''),
                'meaning': data.get('meaning', ''),
                'style': data.get('style', ''),
                'gender': data.get('gender', ''),
                'source': data.get('source', ''),
                'time': datetime.now().isoformat(),
            }
            favorites = session.get('favorites', [])
            # 去重：按 id 覆盖
            favorites = [f for f in favorites if f.get('id') != item['id']]
            favorites.insert(0, item)
            session['favorites'] = favorites[:500]
            return jsonify({'success': True, 'item': item})

        if request.method == 'DELETE':
            ids = data.get('ids') or []
            if not isinstance(ids, list):
                ids = [ids]
            favorites = session.get('favorites', [])
            favorites = [f for f in favorites if f.get('id') not in ids]
            session['favorites'] = favorites
            return jsonify({'success': True, 'deleted': ids})

        return jsonify({'success': False, 'error': '不支持的方法'}), 405
    except Exception as e:
        logger = get_logger()
        logger.error(f"收藏接口失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'收藏接口失败: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': 'Not Found',
        'message': '请求的资源不存在',
        'status': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger = get_logger()
    logger.error(f"内部服务器错误: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal Server Error',
        'message': '服务器内部错误',
        'status': 500
    }), 500

if __name__ == '__main__':
    logger = get_logger()
    config = get_config()
    logger.info("启动智能姓名生成系统")
    app.run(host='0.0.0.0', port=5000, debug=config['default'].DEBUG)
